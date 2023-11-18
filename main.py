import docker
import subprocess
import shlex
import threading

def run_command_with_timeout(command, timeout_seconds):
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    def kill_process():
        process.terminate()
        process.wait()

    timer = threading.Timer(timeout_seconds, kill_process)

    try:
        timer.start()
        stdout, stderr = process.communicate()
        exit_code = process.returncode
    finally:
        timer.cancel()

    return exit_code, stdout, stderr


def python_container(image_name, source_path, target_path, script_name, timeout_seconds):
    client = docker.from_env()
    volumes = {source_path: {'bind': target_path, 'mode': 'rw'}}

    command = f'python {target_path}/{script_name}'


    try:
        container = client.containers.run(
            image=image_name,
            command=command,
            volumes=volumes,
            working_dir=target_path,
            detach=True
        )
        exit_code, _, _ = run_command_with_timeout(command, timeout_seconds)
        logs = container.logs()
        print(logs.decode('utf-8'))
    except docker.errors.ContainerError as e:
        print(f"Container error: {e}")
        exit_code = e.exit_status
    except docker.errors.APIError as e:
        print(f"Docker API error: {e}")
        exit_code = 1 

    finally:
        container.stop()
        container.remove()

    return exit_code

image_name = "python"
source_path = "/home/mani1911/Documents/code-driver/app"
target_path = "/tmp/scripts"
script_name = "test.py"
timeout_seconds = 3

exit_code = python_container(image_name, source_path, target_path, script_name, timeout_seconds)
print(f"Container exited with code: {exit_code}")