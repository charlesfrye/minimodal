"""A simple gRPC server for remote Python code execution."""

from concurrent import futures
from pathlib import Path
import sys

import cloudpickle
import grpc

sys.path.append(
    str(Path(__file__).resolve().parent.parent / "common" / "generated" / "python")
)

import stupid_modal_pb2
import stupid_modal_pb2_grpc


class StupidModalServicer(stupid_modal_pb2_grpc.StupidModalServicer):

    def RunFunction(self, request, context):
        response = stupid_modal_pb2.PickledPythonResponse()
        request_function = cloudpickle.loads(request.pickled_function)
        print(f"🏃 running {request_function}")
        request_arguments = cloudpickle.loads(request.pickled_arguments)
        response.pickled_result = cloudpickle.dumps(
            request_function(*request_arguments)
        )
        return response


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    stupid_modal_pb2_grpc.add_StupidModalServicer_to_server(
        StupidModalServicer(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    print("👂 listening on port 50051")
    server.wait_for_termination()


if __name__ == "__main__":
    print("🎬 starting up stupid_modal")
    serve()
