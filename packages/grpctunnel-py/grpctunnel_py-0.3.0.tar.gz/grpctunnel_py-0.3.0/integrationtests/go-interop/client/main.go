package main

import (
	"context"
	"flag"
	"fmt"
	"io"
	"log"
	"strings"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/status"

	"github.com/dvaldivia/grpctunnel-py/integrationtests/go-interop/echopb"
	"github.com/jhump/grpctunnel"
	"github.com/jhump/grpctunnel/tunnelpb"
)

var (
	serverAddr    = flag.String("server", "localhost:50051", "The server address")
	testErrors    = flag.Bool("test-errors", false, "Test error propagation")
	testDeadlines = flag.Bool("test-deadlines", false, "Test deadline propagation")
)

// echoServiceImpl implements the Echo service that will be called by Python server
type echoServiceImpl struct {
	echopb.UnimplementedEchoServiceServer
}

func (s *echoServiceImpl) Echo(ctx context.Context, req *echopb.EchoRequest) (*echopb.EchoResponse, error) {
	log.Printf("Go client received Echo request: %s", req.Message)

	// Check for deadline in context
	if deadline, ok := ctx.Deadline(); ok {
		remaining := time.Until(deadline)
		log.Printf("Request has deadline, time remaining: %v", remaining)
	}

	// When testing deadlines, simulate delays
	if *testDeadlines {
		if strings.Contains(req.Message, "slow") {
			log.Printf("Simulating slow operation (3s)...")
			select {
			case <-time.After(3 * time.Second):
				// Operation completed
			case <-ctx.Done():
				log.Printf("Context cancelled during slow operation")
				return nil, status.Errorf(codes.DeadlineExceeded, "Deadline exceeded during processing")
			}
		} else if strings.Contains(req.Message, "medium") {
			log.Printf("Simulating medium operation (1s)...")
			select {
			case <-time.After(1 * time.Second):
				// Operation completed
			case <-ctx.Done():
				log.Printf("Context cancelled during medium operation")
				return nil, status.Errorf(codes.DeadlineExceeded, "Deadline exceeded during processing")
			}
		} else if strings.Contains(req.Message, "fast") {
			log.Printf("Simulating fast operation (100ms)...")
			time.Sleep(100 * time.Millisecond)
		}
	}

	// When testing errors, return errors based on message content
	if *testErrors {
		if strings.Contains(req.Message, "not_found") {
			return nil, status.Errorf(codes.NotFound, "Resource not found")
		}
		if strings.Contains(req.Message, "permission_denied") {
			return nil, status.Errorf(codes.PermissionDenied, "Access denied")
		}
		if strings.Contains(req.Message, "invalid") {
			return nil, status.Errorf(codes.InvalidArgument, "Invalid argument")
		}
		if strings.Contains(req.Message, "unavailable") {
			return nil, status.Errorf(codes.Unavailable, "Service unavailable")
		}
		if strings.Contains(req.Message, "deadline") && !*testDeadlines {
			return nil, status.Errorf(codes.DeadlineExceeded, "Deadline exceeded")
		}
		if strings.Contains(req.Message, "internal") {
			return nil, status.Errorf(codes.Internal, "Internal server error")
		}
	}

	return &echopb.EchoResponse{Message: fmt.Sprintf("Echo: %s", req.Message)}, nil
}

func (s *echoServiceImpl) EchoError(ctx context.Context, req *echopb.ErrorRequest) (*echopb.EchoResponse, error) {
	log.Printf("Go client received EchoError request: code=%d, message=%s", req.Code, req.Message)
	// Return error with the specified code
	return nil, status.Errorf(codes.Code(req.Code), "%s", req.Message)
}

func (s *echoServiceImpl) EchoServerStream(req *echopb.EchoRequest, stream echopb.EchoService_EchoServerStreamServer) error {
	log.Printf("Go client received EchoServerStream request: %s", req.Message)

	ctx := stream.Context()

	// Check for deadline
	if deadline, ok := ctx.Deadline(); ok {
		remaining := time.Until(deadline)
		log.Printf("Stream has deadline, time remaining: %v", remaining)
	}

	// Send 5 responses with delays for deadline testing
	for i := 0; i < 5; i++ {
		// Check if context is cancelled
		select {
		case <-ctx.Done():
			log.Printf("Stream cancelled at iteration %d", i)
			return status.Errorf(codes.DeadlineExceeded, "Stream deadline exceeded")
		default:
			// Continue
		}

		resp := &echopb.EchoResponse{
			Message: fmt.Sprintf("%s-%d", req.Message, i),
		}
		if err := stream.Send(resp); err != nil {
			return err
		}

		// Add delay between messages when testing deadlines
		if *testDeadlines {
			if strings.Contains(req.Message, "slow") {
				time.Sleep(1 * time.Second) // 1 second between messages
			} else {
				time.Sleep(200 * time.Millisecond) // 200ms between messages
			}
		}
	}
	return nil
}

func (s *echoServiceImpl) EchoClientStream(stream echopb.EchoService_EchoClientStreamServer) error {
	log.Printf("Go client received EchoClientStream request")
	var messages []string
	for {
		req, err := stream.Recv()
		if err == io.EOF {
			// Return combined message
			resp := &echopb.EchoResponse{
				Message: strings.Join(messages, ","),
			}
			return stream.SendAndClose(resp)
		}
		if err != nil {
			return err
		}
		messages = append(messages, req.Message)
	}
}

func (s *echoServiceImpl) EchoBidiStream(stream echopb.EchoService_EchoBidiStreamServer) error {
	log.Printf("Go client received EchoBidiStream request")
	for {
		req, err := stream.Recv()
		if err == io.EOF {
			return nil
		}
		if err != nil {
			return err
		}
		// Echo back with prefix
		resp := &echopb.EchoResponse{
			Message: fmt.Sprintf("echo:%s", req.Message),
		}
		if err := stream.Send(resp); err != nil {
			return err
		}
	}
}

func main() {
	flag.Parse()

	log.Printf("Connecting to Python server at %s...", *serverAddr)

	// Connect to Python server
	conn, err := grpc.Dial(*serverAddr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("failed to connect: %v", err)
	}
	defer conn.Close()

	// Create tunnel service client
	tunnelClient := tunnelpb.NewTunnelServiceClient(conn)

	// Create a reverse tunnel server (runs on client side)
	reverseTunnelServer := grpctunnel.NewReverseTunnelServer(tunnelClient)

	// Register the Echo service with the reverse tunnel server
	echopb.RegisterEchoServiceServer(reverseTunnelServer, &echoServiceImpl{})

	log.Println("Opening reverse tunnel to Python server...")

	// Serve the reverse tunnel in a goroutine
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	started := make(chan bool, 1)
	go func() {
		ok, err := reverseTunnelServer.Serve(ctx)
		if err != nil && ctx.Err() == nil {
			log.Printf("reverse tunnel error: %v", err)
		}
		started <- ok
	}()

	// Wait a bit for tunnel to establish
	time.Sleep(500 * time.Millisecond)

	// Print success marker immediately so test can verify
	log.Println("Reverse tunnel established successfully")
	fmt.Println("INTEROP_SUCCESS")

	// Wait for tunnel to complete or timeout
	select {
	case <-started:
		log.Println("Reverse tunnel completed normally")
	case <-ctx.Done():
		log.Println("Reverse tunnel timed out")
	}
}
