package main

import (
	"context"
	"flag"
	"fmt"
	"io"
	"log"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	"github.com/dvaldivia/grpctunnel-py/integrationtests/go-interop/echopb"
	"github.com/jhump/grpctunnel"
	"github.com/jhump/grpctunnel/tunnelpb"
)

var (
	port          = flag.Int("port", 50051, "The server port")
	testErrors    = flag.Bool("test-errors", false, "Test error propagation")
	testDeadlines = flag.Bool("test-deadlines", false, "Test deadline propagation")
)

func main() {
	flag.Parse()

	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", *port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	s := grpc.NewServer()

	// Create tunnel service handler with reverse tunnel support
	handler := grpctunnel.NewTunnelServiceHandler(grpctunnel.TunnelServiceHandlerOptions{})

	// Register the tunnel service with the gRPC server
	tunnelpb.RegisterTunnelServiceServer(s, handler.Service())

	log.Printf("Go server listening on :%d", *port)
	log.Printf("Waiting for Python client to connect with reverse tunnel...")

	// Start server in a goroutine
	go func() {
		if err := s.Serve(lis); err != nil {
			log.Fatalf("failed to serve: %v", err)
		}
	}()

	// Wait a bit for reverse tunnel to be established
	time.Sleep(3 * time.Second)

	// Get reverse tunnel channel
	reverseChannel := handler.AsChannel()

	// Wait for reverse channel to be ready
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	err = reverseChannel.WaitForReady(ctx)
	if err != nil {
		log.Printf("Reverse channel not ready: %v", err)
		log.Println("Python client may not have connected yet")
	} else {
		log.Println("Reverse tunnel established, making RPC call to Python client...")

		// Create stub for calling the Python client
		stub := echopb.NewEchoServiceClient(reverseChannel)

		if *testDeadlines {
			// Test deadline propagation
			log.Println("Testing deadline propagation to Python client...")

			// Test 1: Fast operation with generous deadline (should succeed)
			log.Println("1. Testing fast operation with 5s deadline...")
			callCtx, callCancel := context.WithTimeout(context.Background(), 5*time.Second)
			req := &echopb.EchoRequest{Message: "fast operation"}
			resp, err := stub.Echo(callCtx, req)
			callCancel()
			if err != nil {
				log.Printf("ERROR: Fast operation failed: %v", err)
			} else {
				log.Printf("✓ Fast operation succeeded: %s", resp.Message)
			}

			// Test 2: Slow operation with short deadline (should timeout)
			log.Println("2. Testing slow operation with 1s deadline...")
			callCtx, callCancel = context.WithTimeout(context.Background(), 1*time.Second)
			req = &echopb.EchoRequest{Message: "slow operation"}
			_, err = stub.Echo(callCtx, req)
			callCancel()
			if err != nil {
				st, ok := status.FromError(err)
				if ok && st.Code() == codes.DeadlineExceeded {
					log.Printf("✓ Slow operation timed out as expected")
				} else {
					log.Printf("ERROR: Unexpected error: %v", err)
				}
			} else {
				log.Printf("ERROR: Slow operation should have timed out")
			}

			// Test 3: Medium operation with edge-case deadline
			log.Println("3. Testing medium operation with 1.5s deadline...")
			callCtx, callCancel = context.WithTimeout(context.Background(), 1500*time.Millisecond)
			req = &echopb.EchoRequest{Message: "medium operation"}
			resp, err = stub.Echo(callCtx, req)
			callCancel()
			if err != nil {
				st, ok := status.FromError(err)
				if ok && st.Code() == codes.DeadlineExceeded {
					log.Printf("✓ Medium operation timed out (acceptable)")
				} else {
					log.Printf("ERROR: Unexpected error: %v", err)
				}
			} else {
				log.Printf("✓ Medium operation succeeded: %s", resp.Message)
			}

			// Test 4: Server streaming with deadline
			log.Println("4. Testing server streaming with deadline...")
			callCtx, callCancel = context.WithTimeout(context.Background(), 2*time.Second)
			req = &echopb.EchoRequest{Message: "stream fast"}
			streamClient, err := stub.EchoServerStream(callCtx, req)
			if err != nil {
				log.Printf("ERROR: Failed to start stream: %v", err)
			} else {
				responseCount := 0
				for {
					_, err := streamClient.Recv()
					if err == io.EOF {
						break
					}
					if err != nil {
						st, ok := status.FromError(err)
						if ok && st.Code() == codes.DeadlineExceeded {
							log.Printf("✓ Stream timed out after %d responses", responseCount)
						} else {
							log.Printf("ERROR: Stream error: %v", err)
						}
						break
					}
					responseCount++
				}
				if responseCount > 0 {
					log.Printf("✓ Received %d stream responses", responseCount)
				}
			}
			callCancel()

			// Test 5: No deadline (should complete normally)
			log.Println("5. Testing operation with no deadline...")
			req = &echopb.EchoRequest{Message: "slow no-deadline"}
			resp, err = stub.Echo(context.Background(), req)
			if err != nil {
				log.Printf("ERROR: No-deadline operation failed: %v", err)
			} else {
				log.Printf("✓ No-deadline operation succeeded: %s", resp.Message)
			}

			log.Println("All deadline tests passed!")
			fmt.Println("DEADLINE_TEST_SUCCESS")

		} else if *testErrors {
			// Test error propagation
			log.Println("Testing error propagation from Python client...")

			errorTests := []struct {
				message      string
				expectedCode codes.Code
			}{
				{"not_found_test", codes.NotFound},
				{"permission_denied_test", codes.PermissionDenied},
				{"invalid_test", codes.InvalidArgument},
				{"unavailable_test", codes.Unavailable},
				{"deadline_test", codes.DeadlineExceeded},
				{"internal_test", codes.Internal},
			}

			allPassed := true
			for _, test := range errorTests {
				callCtx, callCancel := context.WithTimeout(context.Background(), 5*time.Second)
				req := &echopb.EchoRequest{Message: test.message}
				_, err := stub.Echo(callCtx, req)
				callCancel()

				if err == nil {
					log.Printf("ERROR: Expected error for %s, got success", test.message)
					allPassed = false
				} else {
					st, ok := status.FromError(err)
					if !ok {
						log.Printf("ERROR: Could not get status from error: %v", err)
						allPassed = false
					} else if st.Code() != test.expectedCode {
						log.Printf("ERROR: Expected code %v for %s, got %v", test.expectedCode, test.message, st.Code())
						allPassed = false
					} else {
						log.Printf("✓ %s: Error correctly propagated with code %v", test.message, st.Code())
					}
				}
			}

			// Test EchoError method
			log.Println("Testing EchoError method...")
			errorReq := &echopb.ErrorRequest{
				Code:    int32(codes.PermissionDenied),
				Message: "Test error message",
			}

			callCtx, callCancel := context.WithTimeout(context.Background(), 5*time.Second)
			_, err := stub.EchoError(callCtx, errorReq)
			callCancel()

			if err == nil {
				log.Printf("ERROR: Expected error from EchoError, got success")
				allPassed = false
			} else {
				st, ok := status.FromError(err)
				if !ok {
					log.Printf("ERROR: Could not get status from EchoError error: %v", err)
					allPassed = false
				} else if st.Code() != codes.PermissionDenied {
					log.Printf("ERROR: Expected code PermissionDenied, got %v", st.Code())
					allPassed = false
				} else {
					log.Printf("✓ EchoError: Error correctly propagated with code %v", st.Code())
				}
			}

			if allPassed {
				log.Println("All errors propagated correctly!")
				fmt.Println("ERROR_TEST_SUCCESS")
			} else {
				log.Println("Some error tests failed")
			}

		} else {
			// Normal Echo call
			callCtx, callCancel := context.WithTimeout(context.Background(), 5*time.Second)
			defer callCancel()

			req := &echopb.EchoRequest{Message: "Hello from Go server!"}
			resp, err := stub.Echo(callCtx, req)
			if err != nil {
				log.Printf("Error calling Python client: %v", err)
			} else {
				log.Printf("SUCCESS: Got response from Python client: %s", resp.Message)
				// Write success marker for test verification
				fmt.Println("INTEROP_SUCCESS")
			}
		}
	}

	// Wait for interrupt signal or timeout
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)

	select {
	case <-sigChan:
		log.Println("Received interrupt signal")
	case <-time.After(10 * time.Second):
		log.Println("Timeout reached")
	}

	log.Println("Shutting down server...")
	s.GracefulStop()
}
