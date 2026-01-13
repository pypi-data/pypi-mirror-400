module github.com/dvaldivia/grpctunnel-py/test-projects/go-tunnel

go 1.23

require (
	github.com/jhump/grpctunnel v0.2.0
	google.golang.org/grpc v1.68.1
	google.golang.org/protobuf v1.35.2
)

require (
	github.com/fullstorydev/grpchan v1.1.1 // indirect
	golang.org/x/net v0.29.0 // indirect
	golang.org/x/sys v0.25.0 // indirect
	golang.org/x/text v0.18.0 // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20240903143218-8af14fe29dc1 // indirect
)

// Exclude the old genproto to avoid ambiguous import
exclude google.golang.org/genproto v0.0.0-20221013201013-33fc6f83cba4
