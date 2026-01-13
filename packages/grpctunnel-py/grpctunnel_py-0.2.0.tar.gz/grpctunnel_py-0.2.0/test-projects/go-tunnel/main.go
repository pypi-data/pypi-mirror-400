package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/status"

	"github.com/jhump/grpctunnel"
	"github.com/jhump/grpctunnel/tunnelpb"

	"github.com/dvaldivia/grpctunnel-py/test-projects/go-tunnel/pb"
)

var (
	port = flag.Int("port", 50051, "The server port")
)

// ControlPlaneServer implements the ControlPlaneService
type ControlPlaneServer struct {
	pb.UnimplementedControlPlaneServiceServer
}

// ReportEdgeAlive handles edge worker alive reports
func (s *ControlPlaneServer) ReportEdgeAlive(ctx context.Context, req *pb.EdgeAliveRequest) (*pb.EdgeAliveResponse, error) {
	log.Printf("✓ Received EdgeAlive from edge_id=%s, timestamp=%d", req.EdgeId, req.Timestamp)

	if len(req.Metadata) > 0 {
		log.Printf("  Metadata: %v", req.Metadata)
	}

	return &pb.EdgeAliveResponse{
		Acknowledged: true,
		Message:      "Control plane acknowledges edge alive report",
	}, nil
}

// ReportEdgeGoingAway handles edge worker shutdown notifications
func (s *ControlPlaneServer) ReportEdgeGoingAway(ctx context.Context, req *pb.EdgeGoingAwayRequest) (*pb.EdgeGoingAwayResponse, error) {
	log.Printf("✓ Received EdgeGoingAway from edge_id=%s, reason=%s", req.EdgeId, req.Reason)

	return &pb.EdgeGoingAwayResponse{
		Acknowledged: true,
		Message:      "Control plane acknowledges edge shutdown notification",
	}, nil
}

func main() {
	flag.Parse()

	// Create TCP listener
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", *port))
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	// Create gRPC server
	s := grpc.NewServer()

	// Register the ControlPlane service
	controlPlaneService := &ControlPlaneServer{}
	pb.RegisterControlPlaneServiceServer(s, controlPlaneService)
	log.Printf("✓ Registered ControlPlaneService")

	// Create tunnel service handler with reverse tunnel support
	handler := grpctunnel.NewTunnelServiceHandler(grpctunnel.TunnelServiceHandlerOptions{})

	// Register the tunnel service with the gRPC server
	// This allows edge workers to open reverse tunnels
	tunnelpb.RegisterTunnelServiceServer(s, handler.Service())
	log.Printf("✓ Registered TunnelService for reverse tunnels")

	log.Printf("🚀 Control Plane Server listening on :%d", *port)
	log.Printf("Waiting for Python edge worker to connect...")

	// Start server in a goroutine
	go func() {
		if err := s.Serve(lis); err != nil {
			log.Fatalf("Failed to serve: %v", err)
		}
	}()

	// Wait a bit for reverse tunnel to be established
	log.Printf("Waiting for reverse tunnel to establish...")
	time.Sleep(5 * time.Second)

	// Get reverse tunnel channel
	reverseChannel := handler.AsChannel()

	// Wait for reverse channel to be ready
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	log.Printf("Waiting for reverse channel to be ready...")
	err = reverseChannel.WaitForReady(ctx)
	if err != nil {
		log.Printf("❌ Reverse channel not ready: %v", err)
		log.Printf("Make sure the Python edge worker is running!")
		// Continue running to keep server alive for manual testing
	} else {
		log.Printf("✓ Reverse tunnel established!")
		log.Printf("\n" + strings.Repeat("=", 60))
		log.Printf("Making RPC calls to Python edge worker via reverse tunnel")
		log.Printf(strings.Repeat("=", 60) + "\n")

		// Create stub for calling the Python edge worker
		edgeStub := pb.NewEdgeServiceClient(reverseChannel)

		// Call GetId
		log.Printf("→ Calling EdgeService.GetId()...")
		callCtx, callCancel := context.WithTimeout(context.Background(), 5*time.Second)
		idResp, err := edgeStub.GetId(callCtx, &pb.GetIdRequest{})
		callCancel()

		if err != nil {
			st, _ := status.FromError(err)
			log.Printf("❌ GetId failed: %v (code: %v)", st.Message(), st.Code())
		} else {
			log.Printf("✓ GetId succeeded!")
			log.Printf("  ID: %s", idResp.Id)
			log.Printf("  Hostname: %s", idResp.Hostname)
		}

		// Call GetWhatTimeItIs
		log.Printf("\n→ Calling EdgeService.GetWhatTimeItIs()...")
		callCtx, callCancel = context.WithTimeout(context.Background(), 5*time.Second)
		timeResp, err := edgeStub.GetWhatTimeItIs(callCtx, &pb.GetTimeRequest{})
		callCancel()

		if err != nil {
			st, _ := status.FromError(err)
			log.Printf("❌ GetWhatTimeItIs failed: %v (code: %v)", st.Message(), st.Code())
		} else {
			log.Printf("✓ GetWhatTimeItIs succeeded!")
			log.Printf("  Timestamp: %d", timeResp.Timestamp)
			log.Printf("  Formatted: %s", timeResp.Formatted)
			log.Printf("  Timezone: %s", timeResp.Timezone)
		}

		// Make multiple concurrent calls
		log.Printf("\n→ Making 3 concurrent GetId calls...")

		type result struct {
			resp *pb.GetIdResponse
			err  error
		}

		results := make(chan result, 3)

		for i := 0; i < 3; i++ {
			go func(idx int) {
				callCtx, callCancel := context.WithTimeout(context.Background(), 5*time.Second)
				defer callCancel()
				resp, err := edgeStub.GetId(callCtx, &pb.GetIdRequest{})
				results <- result{resp: resp, err: err}
			}(i)
		}

		successCount := 0
		for i := 0; i < 3; i++ {
			res := <-results
			if res.err == nil {
				successCount++
				log.Printf("  ✓ Call %d: ID=%s", i+1, res.resp.Id)
			} else {
				log.Printf("  ❌ Call %d failed: %v", i+1, res.err)
			}
		}

		log.Printf("✓ Concurrent calls completed: %d/3 succeeded", successCount)

		log.Printf("\n" + strings.Repeat("=", 60))
		log.Printf("All RPC calls to edge worker completed!")
		log.Printf(strings.Repeat("=", 60) + "\n")
	}

	// Wait for interrupt signal
	log.Printf("Server is running. Press Ctrl+C to stop...")
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)
	<-sigChan

	log.Printf("\n✓ Shutting down server...")
	s.GracefulStop()
	log.Printf("✓ Server stopped")
}
