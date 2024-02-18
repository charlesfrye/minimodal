"""A very simple demo application for our very simple demo Modal."""

from pathlib import Path
import sys

import cloudpickle

sys.path.append(str(Path(__file__).resolve().parent.parent / "client"))

import client as stupid_modal

stub = stupid_modal.Stub()


@stub.function
def inference(x1, x2):
    """A stand in for real inference.

    This is a dot product, or a 'shallow linear neural network' if you're raising VC funds.
    """

    import numpy as np

    model_weights = np.array([-1.0, 1.0])

    return float(model_weights @ np.array([x1, x2]))


if __name__ == "__main__":
    import string

    while True:
        try:
            if len(sys.argv) < 3:
                num1 = input("1️⃣  Enter the first number (Ctrl+C or letters to quit): ")
                if num1.lower()[0] not in string.digits + ".,-":
                    break
                num1 = float(num1)

                num2 = input("2️⃣  Enter the second number: ")
                num2 = float(num2)
            else:
                num2 = float(sys.argv.pop())
                num1 = float(sys.argv.pop())

            try:
                result = inference.local(num1, num2)
                print(f"💚 succeeded locally: {result}")
            except ImportError as e:
                print(f"❌ failed to run locally: {e}")
            result = inference.remote(num1, num2)
            print(f"💚 succeeded on remote server: {result}")

        except ValueError:
            print(f"Invalid input: {num1, num2}. Exiting.")
        except (KeyboardInterrupt, EOFError):
            break
