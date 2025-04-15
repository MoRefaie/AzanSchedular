import os
import time
from dotenv import load_dotenv,set_key
from pathlib import Path
import subprocess
import signal

# Path to the .env file
env_path = Path(".env")

# Path to the second process script
process_2_script = "run()"

# Global variable to store the child process
child_process = None

def update_env_and_restart_process(new_value):
    """
    Update the .env file with the new value and restart the second process.
    """
    global child_process

    # Update the .env file
    set_key(env_path, "TEST", new_value)
    print(f"Updated TEST in .env file to: {new_value}")

    # Restart the second process
    if child_process:
        print("Terminating the existing process...")
        child_process.terminate()  # Gracefully terminate the process
        child_process.wait()  # Wait for the process to terminate

    print("Starting a new process...")
    child_process = subprocess.Popen(["python3", process_2_script])  # Start a new process

if __name__ == "__main__":
    try:
        # Start the second process initially
        child_process = subprocess.Popen(["python3", process_2_script])

        # Continuously wait for user input to update the .env file and restart the process
        while True:
            new_value = input("Enter a new value for TEST (or type 'exit' to quit): ")
            if new_value.lower() == "exit":
                break  # Exit the loop if the user types 'exit'

            update_env_and_restart_process(new_value)

        print("Terminating the child process...")
        if child_process:
            child_process.terminate()  # Gracefully terminate the child process
            child_process.wait()  # Wait for the process to terminate
        print("Exiting...")
    except KeyboardInterrupt:
        print("Terminating the child process...")
        if child_process:
            child_process.terminate()  # Gracefully terminate the child process
            child_process.wait()  # Wait for the process to terminate
        print("Exiting...")
        
def run():
    load_dotenv()
    x=0
    while x < 10:
        x=x+1
        print(f'{x}:{os.getenv("TEST")}')
        time.sleep(1)
