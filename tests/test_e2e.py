import logging
import os
import subprocess
import signal
import sys
import time

logging.basicConfig(level=logging.INFO)


def run_server():
    command = "source server/.server/bin/activate && python server/server.py"
    try:
        process = subprocess.Popen(
            command, shell=True, executable="/bin/bash", preexec_fn=os.setsid
        )
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
    try:
        app.stdin.flush()
    except BrokenPipeError:
        print("Error starting app")
        print("App Output:\n", app.stdout.read().decode())
    time.sleep(1)

    stdout, stderr = app.communicate()
    print("App Output:\n", stdout.decode())
    if err := stderr.decode():
        print("App Error:\n", err)

    # send keyboard interrupt to the app process
    app.send_signal(signal.SIGINT)
    app.wait()

    # send interrupt to server process group
    os.killpg(os.getpgid(server.pid), signal.SIGINT)
    server.wait()


if __name__ == "__main__":
    sys.exit(test_e2e())
