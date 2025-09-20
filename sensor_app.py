import paho.mqtt.client as mqtt
import json
from datetime import datetime
import time
import os
import requests
import logging
import schedule
import threading
from azure.storage.blob import BlobServiceClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration - Use environment variables
broker = os.getenv("TTN_BROKER", "eu1.cloud.thethings.network")
port = int(os.getenv("TTN_PORT", "1883"))
username = os.getenv("TTN_USERNAME")
password = os.getenv("TTN_PASSWORD")
device_id = os.getenv("TTN_DEVICE_ID")

# ThingSpeak Configuration
thingspeak_api_key = os.getenv("THINGSPEAK_API_KEY")
thingspeak_url = "https://api.thingspeak.com/update"

# Azure Storage Configuration (optional)
azure_storage_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container_name = os.getenv("AZURE_STORAGE_CONTAINER", "sensor-data")

# Initialize Azure Blob Service Client if connection string is provided
blob_service_client = None
if azure_storage_connection_string:
    try:
        blob_service_client = BlobServiceClient.from_connection_string(azure_storage_connection_string)
        logger.info("Connected to Azure Blob Storage")
    except Exception as e:
        logger.error(f"Failed to connect to Azure Storage: {e}")

def save_to_azure(data, filename):
    """Save data to Azure Blob Storage"""
    if not blob_service_client:
        return False
        
    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)
        blob_client.upload_blob(json.dumps(data), overwrite=True)
        logger.info(f"Successfully saved {filename} to Azure Storage")
        return True
    except Exception as e:
        logger.error(f"Failed to save to Azure Storage: {e}")
        return False

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
        
        # Send to ThingSpeak
        response = requests.get(thingspeak_url, params=thingspeak_data)
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
    """Fetch historical data from TTN"""
    app_id = username.split('@')[0] if '@' in username else username
    
    url = f"https://{broker}/api/v3/as/applications/{app_id}/devices/{device_id}/packages/storage/uplink_message"

    headers = {"Authorization": f"Bearer {password}"}
    params = {"last": "12h"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            
            # Save to Azure if configured
            if azure_storage_connection_string:
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                filename = f"historical/historical_data_{timestamp}.json"
                save_to_azure(data, filename)
            
            logger.info(f"Retrieved {len(data.get('result', []))} historical records")
            
            # Also send historical data to ThingSpeak
            for record in data.get('result', []):
                send_to_thingspeak(record)
                
        else:
            logger.error(f"Error fetching historical data: {response.status_code}, {response.text}")
    except Exception as e:
        logger.error(f"Exception in get_historical_sensor_data: {e}")

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to TTN MQTT broker!")
        client.subscribe(f"v3/{username}/devices/{device_id}/up")
    else:
        logger.error(f"Failed to connect, return code {rc}")
        time.sleep(300)  # Wait 5 minutes before reconnect

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        
        # Save to Azure if configured
        if azure_storage_connection_string:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"realtime/realtime_data_{timestamp}.json"
            save_to_azure(payload, filename)
        
        # Send to ThingSpeak
        send_to_thingspeak(payload)
        
        logger.info("Processed new sensor data")
    except Exception as e:
        logger.error(f"Error processing message: {e}")

def run_mqtt_client():
    """Run MQTT client in a separate thread"""
    client = mqtt.Client()
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_message = on_message
    
    while True:
        try:
            client.connect(broker, port, 60)
            client.loop_forever()
        except Exception as e:
            logger.error(f"MQTT connection failed: {e}")
            time.sleep(300)  # Wait 5 minutes before retrying

def main():
    logger.info("Starting sensor data collection application")
    
    # Get historical data on startup
    get_historical_sensor_data()
    
    # Schedule historical data fetch every 12 hours
    schedule.every(12).hours.do(get_historical_sensor_data)
    
    # Start MQTT in a separate thread
    mqtt_thread = threading.Thread(target=run_mqtt_client)
    mqtt_thread.daemon = True
    mqtt_thread.start()
    
    # Keep the main thread alive and run scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()