import sys
import threading


def log_subprocess_output(process, *, prefix_stdout="STDOUT: ", prefix_stderr="STDERR: "):
    """
    Continuously read stdout/stderr from a subprocess without blocking
    the main thread. Starts daemon threads automatically.
    """

    def _reader(pipe, prefix):
        for line in iter(pipe.readline, ''):
            if not line:
                break
            sys.stdout.write(prefix + line)
            sys.stdout.flush()
        pipe.close()

    if process.stdout:
        threading.Thread(
            target=_reader,
            args=(process.stdout, prefix_stdout),
            daemon=True,
        ).start()

    if process.stderr:
        threading.Thread(
            target=_reader,
            args=(process.stderr, prefix_stderr),
            daemon=True,
        ).start()
