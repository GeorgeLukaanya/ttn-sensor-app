# IoT Sensor Data Pipeline

This project is a Python application that collects sensor data from The Things Network (TTN) via MQTT, and forwards it to ThingSpeak for real-time monitoring and to Azure Blob Storage for historical data storage.

## Features

- **MQTT Integration:** Connects to a TTN MQTT broker to receive real-time sensor data.
- **ThingSpeak Integration:** Forwards sensor data to a ThingSpeak channel for visualization.
- **Azure Blob Storage Integration:** Saves both real-time and historical sensor data to Azure Blob Storage for long-term storage and analysis.
- **Historical Data Fetching:** Retrieves the last 12 hours of sensor data from TTN upon startup and every 12 hours thereafter.
- **Resilient Connectivity:** Implements a retry mechanism with a 5-minute backoff for MQTT connection failures.
- **Configuration via Environment Variables:** All sensitive information and configuration parameters are managed through environment variables, ensuring that no credentials are hard-coded in the source code.

## Prerequisites

- Python 3.6+
- A The Things Network (TTN) account and a registered device
- A ThingSpeak account and a channel set up with the required fields
- (Optional) An Azure Storage account

## Configuration

The application is configured through environment variables. Below is a list of the required and optional variables:

| Variable                          | Description                                                                                              | Required |
| --------------------------------- | -------------------------------------------------------------------------------------------------------- | -------- |
| `TTN_BROKER`                      | The TTN MQTT broker address (e.g., `eu1.cloud.thethings.network`).                                         | Yes      |
| `TTN_PORT`                        | The port for the TTN MQTT broker (e.g., `1883`).                                                         | Yes      |
| `TTN_USERNAME`                    | Your TTN application ID.                                                                                 | Yes      |
| `TTN_PASSWORD`                    | Your TTN API key with rights to read application traffic.                                                  | Yes      |
| `TTN_DEVICE_ID`                   | The ID of your device in TTN.                                                                            | Yes      |
| `THINGSPEAK_API_KEY`              | Your ThingSpeak channel's write API key.                                                                 | Yes      |
| `AZURE_STORAGE_CONNECTION_STRING` | The connection string for your Azure Storage account. If not provided, the Azure integration is disabled. | No       |
| `AZURE_STORAGE_CONTAINER`         | The name of the container in Azure Blob Storage where data will be stored. Defaults to `sensor-data`.    | No       |
| `STARTUP_CMD`                     | The command to run the application. Defaults to `python sensor_app.py`.                                  | No       |

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```

2.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Set the environment variables:**

    Export the required environment variables listed in the **Configuration** section. For example:

    ```bash
    export TTN_BROKER="eu1.cloud.thethings.network"
    export TTN_PORT="1883"
    export TTN_USERNAME="your-ttn-app-id"
    export TTN_PASSWORD="your-ttn-api-key"
    export TTN_DEVICE_ID="your-device-id"
    export THINGSPEAK_API_KEY="your-thingspeak-api-key"
    ```

2.  **Run the application:**

    ```bash
    python sensor_app.py
    ```

The application will start, fetch historical data, and begin listening for new sensor data from the TTN MQTT broker.

## How It Works

The application is composed of several key components:

-   **`sensor_app.py`**: The main application file that contains the logic for connecting to TTN, fetching and processing data, and sending it to ThingSpeak and Azure Storage.
-   **`web.py`**: A simple wrapper to run the main application.
-   **`application.py`**: A startup script that executes the command specified in the `STARTUP_CMD` environment variable.
-   **`requirements.txt`**: A list of the Python dependencies required for the project.
-   **`startup.txt`**: A file that contains the default startup command.

The application uses the `paho-mqtt` library to connect to the TTN MQTT broker and the `requests` library to send data to the ThingSpeak API. For Azure integration, it uses the `azure-storage-blob` library. The `schedule` library is used to periodically fetch historical data.