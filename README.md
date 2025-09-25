# IoT Sensor Data Pipeline with Azure Functions

This project is an Azure Function App that collects sensor data from The Things Network (TTN) and forwards it to ThingSpeak for real-time monitoring.

## Features

- **Azure Function Integration:** Runs as a timer-triggered Azure Function, executing every 6 hours.
- **TTN Integration:** Connects to a TTN MQTT broker to receive real-time sensor data and fetches historical data from the TTN Storage Integration.
- **ThingSpeak Integration:** Forwards sensor data to a ThingSpeak channel for visualization.
- **Historical Data Fetching:** Retrieves the last 6 hours of sensor data from TTN upon startup.
- **Resilient Connectivity:** Listens for real-time data for 6 hours after fetching historical data.
- **Configuration via Environment Variables:** All sensitive information and configuration parameters are managed through environment variables.

## Prerequisites

- Python 3.6+
- An Azure account with Azure Functions support.
- A The Things Network (TTN) account and a registered device with the Storage Integration enabled.
- A ThingSpeak account and a channel set up with the required fields.

## Configuration

The application is configured through environment variables. Below is a list of the required variables:

| Variable | Description | Required |
|---|---|---|
| `TTN_BROKER` | The TTN MQTT broker address (e.g., `eu1.cloud.thethings.network`). | Yes |
| `TTN_PORT` | The port for the TTN MQTT broker (e.g., `1883`). | Yes |
| `TTN_USERNAME` | Your TTN application ID. | Yes |
| `TTN_PASSWORD` | Your TTN API key with rights to read application traffic and read from the storage integration. | Yes |
| `TTN_DEVICE_ID` | The ID of your device in TTN. | Yes |
| `THINGSPEAK_API_KEY` | Your ThingSpeak channel's write API key. | Yes |

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

## Local Testing

The `test_run.py` script is provided for local testing of the function.

1.  **Set the environment variables:**

    Open `test_run.py` and replace the placeholder values for the environment variables with your actual credentials.

2.  **Run the test script:**

    ```bash
    python test_run.py
    ```

The script will execute the `six_hour_sensor_collection` function, and you should see log output in your console.

## Deployment

This application is designed to be deployed as an Azure Function.

1.  **Create an Azure Function App:**

    Follow the official Microsoft documentation to create a new Function App in your Azure subscription.

2.  **Configure Application Settings:**

    In the Azure portal, navigate to your Function App's configuration and add the environment variables listed in the **Configuration** section as Application Settings.

3.  **Deploy the code:**

    You can deploy the function code to Azure using various methods, such as the Azure Functions extension for Visual Studio Code, or by setting up a CI/CD pipeline from your git repository.

## How It Works

-   **`function_app.py`**: The main application file containing the Azure Function logic. It's triggered by a timer (`@app.timer_trigger`) every 6 hours.
-   **`requirements.txt`**: A list of the Python dependencies required for the project.
-   **`test_run.py`**: A script for running the function locally for testing and debugging.

The function performs the following steps:
1.  Fetches the last 6 hours of historical data from the TTN Storage Integration.
2.  Sends this historical data to ThingSpeak.
3.  Connects to the TTN MQTT broker to listen for real-time data for the next 6 hours.
4.  Sends incoming real-time data to ThingSpeak.