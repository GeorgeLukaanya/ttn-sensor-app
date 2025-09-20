import os
import sys

# Get the startup command from environment variable or use default
startup_cmd = os.environ.get('STARTUP_CMD', 'python sensor_app.py')

# Execute the startup command
os.system(startup_cmd)