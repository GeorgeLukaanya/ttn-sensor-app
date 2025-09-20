import os
import sys

# Add your app's directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import and run your application
from sensor_app import main

if __name__ == "__main__":
    main()