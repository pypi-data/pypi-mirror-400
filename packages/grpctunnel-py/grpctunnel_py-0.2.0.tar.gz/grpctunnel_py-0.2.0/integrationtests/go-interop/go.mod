module github.com/dvaldivia/grpctunnel-py/integrationtests/go-interop

go 1.24.0

require (
	github.com/jhump/grpctunnel v0.3.0
	google.golang.org/grpc v1.76.0
	google.golang.org/protobuf v1.36.10
)

require (
	github.com/fullstorydev/grpchan v1.1.1 // indirect
	golang.org/x/net v0.42.0 // indirect
	golang.org/x/sys v0.34.0 // indirect
	golang.org/x/text v0.27.0 // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20250804133106-a7a43d27e69b // indirect
)

replace google.golang.org/genproto => google.golang.org/genproto v0.0.0-20240528184218-531527333157
