# servicebus-size-monitor
This Python script monitors the maximum sizes of Azure ServiceBus Topics and Queues for active messages and reports their usage percentages in the terminal. The script is designed to help identify when these resources are nearing or exceeding a pre-configured usage threshold, alerting users before critical limits are reached.

## Features
- Monitors Azure ServiceBus Queues and Topics.
- Displays usage statistics in real-time.
- Configurable usage threshold for warnings.
- Customizable time interval for resource checks.
- Supports running in a Docker container.

## Prerequisites
- Python 3.9+
- An Azure subscription and ServiceBus namespace.
- Azure CLI installed and authenticated.

## Getting Started
### 1. Clons the repository
```bash
git clone https://github.com/yourusername/azure-servicebus-monitor.git
cd azure-servicebus-monitor
```

### 2. Install Dependencies
You can install the required Python dependencies using:
```bash
pip install -r requirements.txt
```

### 3. Define variables
Create a `.env` file in the project root and define the following environment variables:

```bash
SUBSCRIPTION_ID=<your-azure-subscription-id>
RESOURCE_GROUP_NAME=<your-resource-group-name>
SERVICEBUS_NAMESPACE=<your-servicebus-namespace>
THRESHOLD_PERCENTAGE=<usage-threshold-percentage>  # e.g., 80 for 80%
TIMER_INTERVAL=<time-interval-in-seconds>  # e.g., 60 for 60 seconds
```

### 4. Run the script
```bash
python app.py
```
The script will begin monitoring your Azure ServiceBus resources and display usage information for each Queue and Topic.

## Running with Docker

You can use the pre-built Docker image from Docker Hub, eliminating the need to build the Dockerfile manually.

### 1. Pull the Docker Image
```bash
docker pull imaun/azure-servicebus-monitor:latest
```

### 2. Run the Docker Container
```bash
docker run --env-file .env imaun/azure-servicebus-monitor:latest
```
This will start the container and run the monitoring script in a lightweight Python environment.

## How It Works
The script uses the Azure SDK to fetch information about all Queues and Topics in a given ServiceBus namespace. It compares their current active message size against the maximum configured size and calculates the usage percentage. If the usage exceeds the pre-configured threshold, a warning is printed to the terminal.

## Customization

- **Threshold Percentage**: Define how close to the resource's maximum size you want to be alerted (e.g., 80%).
- **Timer Interval**: Set how often the script checks the resource sizes.

## License
This project is licensed under the GPL-3.0 License.

