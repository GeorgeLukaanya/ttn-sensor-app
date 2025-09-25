import azure.functions as func
import paho.mqtt.client as mqtt
import json
import time
import os
import requests
import logging
import threading

app = func.FunctionApp()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from environment variables
broker = os.getenv("TTN_BROKER", "eu1.cloud.thethings.network")
port = int(os.getenv("TTN_PORT", "1883"))
username = os.getenv("TTN_USERNAME")
password = os.getenv("TTN_PASSWORD")
device_id = os.getenv("TTN_DEVICE_ID")
thingspeak_api_key = os.getenv("THINGSPEAK_API_KEY")
thingspeak_url = "https://api.thingspeak.com/update"

# Global variable to control MQTT loop
mqtt_running = False
mqtt_client = None

def send_to_thingspeak(payload):
    """Send sensor data to ThingSpeak"""
    if not thingspeak_api_key:
        logger.warning("ThingSpeak API key not configured")
        return False
        
    try:
        # Extract data from TTN payload
        decoded_payload = payload.get("uplink_message", {}).get("decoded_payload", {})
        
        # Map TTN fields to ThingSpeak fields
        thingspeak_data = {
            'api_key': thingspeak_api_key,
            'field1': decoded_payload.get("field5", 0),  # Temperature
            'field2': decoded_payload.get("field3", 0),  # Humidity
            'field3': decoded_payload.get("field4", 0),  # Motion Count
            'field4': decoded_payload.get("field1", 0),  # Battery Voltage
        }
        
        logger.info(f"Sending to ThingSpeak: {thingspeak_data}")
        
        # Send to ThingSpeak
        response = requests.get(thingspeak_url, params=thingspeak_data, timeout=10)
        if response.status_code == 200 and int(response.text) > 0:
            logger.info("Data sent to ThingSpeak successfully")
            return True
        else:
            logger.error(f"ThingSpeak error: {response.status_code}, {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending to ThingSpeak: {e}")
        return False

def get_historical_sensor_data():
    """Fetch historical data from TTN for the past 6 hours"""
    try:
        app_id = username.split('@')[0] if '@' in username else username
        
        url = f"https://{broker}/api/v3/as/applications/{app_id}/devices/{device_id}/packages/storage/uplink_message"

        headers = {"Authorization": f"Bearer {password}"}
        params = {"last": "6h"}  # Get data from last 6 hours
        
        logger.info("Fetching historical data from TTN...")
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            records = data.get('result', [])
            logger.info(f"Retrieved {len(records)} historical records")
            
            # Send historical data to ThingSpeak
            success_count = 0
            for record in records:
                if send_to_thingspeak(record):
                    success_count += 1
                time.sleep(1)  # Avoid rate limiting
            
            logger.info(f"Successfully sent {success_count} records to ThingSpeak")
            return success_count
        else:
            logger.error(f"Error fetching historical data: {response.status_code}")
            return 0
    except Exception as e:
        logger.error(f"Exception in get_historical_sensor_data: {e}")
        return 0

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to TTN MQTT broker!")
        client.subscribe(f"v3/{username}/devices/{device_id}/up")
    else:
        logger.error(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        logger.info("Received new sensor data")
        
        # Send to ThingSpeak
        send_to_thingspeak(payload)
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")

def run_mqtt_client():
    """Run MQTT client to listen for real-time data"""
    global mqtt_running, mqtt_client
    
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(username, password)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    
    mqtt_running = True
    logger.info("Starting MQTT client for real-time data")
    
    try:
        mqtt_client.connect(broker, port, 60)
        mqtt_client.loop_start()
        
        # Keep running for 6 hours (21600 seconds)
        for _ in range(2160):  # Check every 10 seconds for 6 hours
            if not mqtt_running:
                break
            time.sleep(10)
            
    except Exception as e:
        logger.error(f"MQTT error: {e}")
    finally:
        mqtt_running = False
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        logger.info("MQTT client stopped")

@app.timer_trigger(schedule="0 0 6 * * *", arg_name="mytimer", run_on_startup=False, use_monitor=False) 
def six_hour_sensor_collection(mytimer: func.TimerRequest):
    # This function will run at 6:00 AM every day
    logger.info("Starting 6-hour sensor data collection")
    
    # 1. First get historical data from the past 6 hours
    historical_count = get_historical_sensor_data()
    logger.info(f"Processed {historical_count} historical records")
    
    # 2. Then listen for real-time data for the next 6 hours
    mqtt_thread = threading.Thread(target=run_mqtt_client)
    mqtt_thread.daemon = True
    mqtt_thread.start()
    
    # Wait for 6 hours (function will stay warm)
    time.sleep(21600)  # 6 hours in seconds
    
    # Stop MQTT client
    global mqtt_running
    mqtt_running = False
    
    logger.info("6-hour collection period completed")