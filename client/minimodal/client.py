"""The client-side logic for MiniModal."""

from pathlib import Path
import sys

import cloudpickle
import grpc

sys.path.append(
    str(Path(__file__).resolve().parent.parent.parent / "common" / "generated" / "python")
)

import minimodal_pb2
import minimodal_pb2_grpc


class Stub:
    def __init__(self):
        self._channel = grpc.insecure_channel("localhost:50051")
        self._stub = minimodal_pb2_grpc.MiniModalStub(self._channel)

    def function(self, func):
        function_id = func.__name__

        def wrapper(*args):
            pickled_args = cloudpickle.dumps(args)
            response = self._stub.RunFunction(
                minimodal_pb2.RunFunctionRequest(
                    function_id=function_id,
                    pickled_inputs=pickled_args,
                )
            )
            return cloudpickle.loads(response.pickled_result)

        def remote(*args, **kwargs):
            return wrapper(*args, **kwargs)

        wrapper.remote = remote
        wrapper.local = func
        return wrapper

    def mount(self, file):
        with open(file, "rb") as f:
            content = f.read()
        result = self._stub.SendPythonFile(minimodal_pb2.PythonFile(py_file=content))
        if result.status != 0:
            raise Exception("failed to send file to server")
