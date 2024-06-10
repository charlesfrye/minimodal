import logging
import subprocess
import time
import signal

logging.basicConfig(level=logging.INFO)


def run_server():
    command = "source server/.server/bin/activate && python server/server.py"
    try:
        process = subprocess.Popen(command, shell=True, executable="/bin/bash")
        logging.info("Server started with PID %d", process.pid)
        return process
    except Exception as e:
        logging.error("Failed to start server: %s", e)
        raise


def run_app():
    command = "source app/.app/bin/activate && minimodal run app/app.py"
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            executable="/bin/bash",
        )
        logging.info("App started with PID %d", process.pid)
        return process
    except Exception as e:
        logging.error("Failed to start app: %s", e)
        raise


def test_e2e():
    server = run_server()
    time.sleep(1)

    app = run_app()
    time.sleep(1)

    # simulate user interaction
    inputs = b"3\n5\n"
    app.stdin.write(inputs)
    app.stdin.flush()
    time.sleep(1)

    stdout, stderr = app.communicate()
    print("Client Output:\n", stdout.decode())
    print("Client Error:\n", stderr.decode())

    # send keyboard interrupt to the app process
    app.send_signal(signal.SIGINT)

    server.terminate()
    server.wait()


if __name__ == "__main__":
    test_e2e()
