"""Test script: starts the backend server and tests the health endpoint."""
import subprocess
import time
import urllib.request
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
)

try:
    time.sleep(4)
    req = urllib.request.Request("http://localhost:8000/api/health")
    with urllib.request.urlopen(req) as resp:
        print("Health check:", resp.read().decode())
    print("Backend is RUNNING on http://localhost:8000")
    print("Press Ctrl+C to stop.")
    # keep running
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping server...")
finally:
    proc.terminate()
    proc.wait()
