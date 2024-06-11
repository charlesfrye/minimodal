"""A simple gRPC server for remote Python code execution."""

from concurrent import futures
from pathlib import Path
import signal
import sys

import cloudpickle
import grpc

sys.path.append(
    str(Path(__file__).resolve().parent.parent / "common" / "generated" / "python")
)

import minimodal_pb2
import minimodal_pb2_grpc


class MiniModalServicer(minimodal_pb2_grpc.MiniModalServicer):
    script_path = Path("/tmp/app.py")

    def __init__(self):
        self.environment = {}  # Placeholder for environment management

    def SendPythonFile(self, request, context):
        try:
            with open(self.script_path, "wb") as py_file:
                py_file.write(request.py_file)
            return minimodal_pb2.PythonFileResponse(status=0)  # Success
        except Exception as e:
            print(f"error: {e}")
            return minimodal_pb2.PythonFileResponse(status=1)  # Failure

    def RunFunction(self, request, context):
        import importlib

        print(f"📦 loading app: {self.script_path}")
        spec = importlib.util.spec_from_file_location("app", self.script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        print(f"🏃‍ running function: {request.function_id}")
        func = getattr(module, request.function_id)
        inputs = cloudpickle.loads(request.pickled_inputs)
        result = func.local(*inputs)

        print(f"🏁 result: {result}")

        # Serialize the result and send it back
        pickled_result = cloudpickle.dumps(result)

        return minimodal_pb2.RunFunctionResponse(pickled_result=pickled_result)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    minimodal_pb2_grpc.add_MiniModalServicer_to_server(MiniModalServicer(), server)

    server.add_insecure_port("[::]:50051")
    server.start()
    print("👂 listening on port 50051")

    # handle shutdown
    def handle_signal(sig, frame):
        print("\n👋 shutting down minimodal server")
        server.stop(0)
        print("✅ minimodal server stopped")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    server.wait_for_termination()


if __name__ == "__main__":
    print("🎬 starting up minimodal server")
    serve()
