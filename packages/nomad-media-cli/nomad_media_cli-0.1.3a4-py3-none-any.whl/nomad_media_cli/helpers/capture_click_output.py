import io
import json
import sys
import os
import threading

# Global lock to ensure thread-safe stdout redirection
_capture_lock = threading.Lock()

def capture_click_output(ctx, command, **kwargs):
    """Utility to invoke a click command and capture its output.

    This function captures stdout to prevent internal command output from
    appearing in the terminal when commands are called programmatically.
    It preserves stderr so that debug messages can still be displayed.

    Thread-safe: Uses a global lock to prevent multiple threads from
    interfering with each other's stdout redirection.
    """
    # Use a lock to ensure only one thread can redirect sys.stdout at a time
    with _capture_lock:
        stdout_capture = io.StringIO()
        original_stdout = sys.stdout
        try:
            sys.stdout = stdout_capture
            try:
                ctx.invoke(command, **kwargs)
                exit_code = 0
            except SystemExit as e:
                exit_code = e.code
            stdout_capture.flush()
        finally:
            sys.stdout = original_stdout

        output = stdout_capture.getvalue()

        if exit_code != 0:
            try:
                raise Exception(json.loads(output)["error"])
            except Exception:
                raise Exception(f"Error: {output}")

        try:
            return json.loads(output) if output else None
        except Exception as e:
            raise Exception(f"Error parsing JSON output: {e}, output: {output}")