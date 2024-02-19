"""The client-side logic for Stupid Modal.

We define our local 'Stub', the information we need to control local execution of the application,
and it handles communication with the server."""

from pathlib import Path
import sys

import cloudpickle
import grpc

sys.path.append(
    str(Path(__file__).resolve().parent.parent / "common" / "generated" / "python")
)

import stupid_modal_pb2
import stupid_modal_pb2_grpc


class Stub:
    def __init__(self):
        self._channel = grpc.insecure_channel("localhost:50051")
        self._stub = stupid_modal_pb2_grpc.StupidModalStub(self._channel)

    def function(self, func):
        def wrapper(*args):
            pickled_func = cloudpickle.dumps(func)
            pickled_args = cloudpickle.dumps(args)
            response = self._stub.RunFunction(
                stupid_modal_pb2.PickledPythonRequest(
                    pickled_function=pickled_func,
                    pickled_arguments=pickled_args,
                )
            )
            return cloudpickle.loads(response.pickled_result)

        def remote(*args, **kwargs):
            return wrapper(*args, **kwargs)

        wrapper.remote = remote
        wrapper.local = func
        return wrapper
