 # aegis-proto

 Language-agnostic IDL (Protocol Buffers) for the Aegis platform.

 ## Layout
 - `proto/`: source `.proto` files
 - `gen/`: generated outputs (Go and Python)

 ## Prerequisites
 - `protoc` 25.x
 - Go (for `protoc-gen-go` and `protoc-gen-go-grpc`)
 - Python 3.x (for `grpcio-tools`)
 - `task` (Taskfile runner)

 ## Generate code
 ```bash
 task gen
 ```

 ## Clean generated code
 ```bash
 task clean
 ```
