from azure.identity import DefaultAzureCredential
from azure.mgmt.servicebus import ServiceBusManagementClient
from azure.monitor.query import MetricsQueryClient
import time

credentials = DefaultAzureCredential()

subscription_id = ''

servicebus_client = ServiceBusManagementClient(credentials, subscription_id)
metrics_client = MetricsQueryClient(credentials)

resource_group_name = ''
namespace = ''
threshold_percentage = 80

queues = servicebus_client.queues.list_by_namespace(resource_group_name, namespace)

topics = servicebus_client.topics.list_by_namespace(resource_group_name, namespace)

def get_maxsize(resource_id):
    metrics_data = metrics_client.query_resource(
        resource_id,
        metric_names=['Size'],
        timespan=None, # Get the latest value
        granularity=None,
        aggregations=['Max'],
    )

    if metrics_data.metrics:
        size_metric = metrics_data.metrics[0]
        if size_metric.timeseries:
            data_points = size_metric.timeseries[0].data
            if data_points:
                current_size = data_points[-1].max
                return current_size
    return None




