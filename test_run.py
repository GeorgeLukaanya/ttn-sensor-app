import os
import sys
import logging

# Set up environment variables
os.environ['TTN_USERNAME'] = 'bd-test-app2@ttn'
os.environ['TTN_PASSWORD'] = 'NNSXS.NGFSXX4UXDX55XRIDQZS6LPR4OJXKIIGSZS56CQ.6O4WUAUHFUAHSTEYRWJX6DDO7TL2IBLC7EV2LS4EHWZOOEPCEUOA'
os.environ['TTN_DEVICE_ID'] = 'lht65n-01-temp-humidity-sensor'
os.environ['THINGSPEAK_API_KEY'] = 'XW9YLMYR88WLG2NR'  # Replace with your key

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Import and run your function
try:
    from function_app import six_hour_sensor_collection
    print("Running six_hour_sensor_collection function...")
    six_hour_sensor_collection(None)
    print("Function completed successfully!")
except Exception as e:
    print(f"Error running function: {e}")
    import traceback
    traceback.print_exc()