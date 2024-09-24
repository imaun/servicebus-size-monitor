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

resources = []

for queue in queues:
    queue_name = queue.name
    max_size_bytes = queue.max_szie_in_megabytes * 1024 * 1024
    resource_id = (
        f'/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}'
        f'/providers/Microsoft.ServiceBus/namespaces/{namespace}/queues/{queue_name}'
    )
    resources.append({
        'name': queue_name,
        'type': 'queue',
        'resource_id': resource_id,
        'max_size': max_size_bytes
    })

for topic in topics:
    topic_name = topic.name
    max_size_bytes = topic.max_size_in_megabytes * 1024 * 1024  # Convert to bytes
    resource_id = (
        f'/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}'
        f'/providers/Microsoft.ServiceBus/namespaces/{namespace}/topics/{topic_name}'
    )
    resources.append({
        'name': topic_name,
        'type': 'topic',
        'resource_id': resource_id,
        'max_size': max_size_bytes
    })


def get_resource_size(resource_id):
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

def get_resources_exceeding_threshold(resources, threshold_percentage):
    response = []
    for resource in resources:
        name = resource['name']
        res_type = resource['type']
        res_id = resource['resource_id']
        max_size = resource['max_size']

    current_size = get_resource_size(res_id)

    if current_size is not None:
        usage_percentage = (current_size / max_size) * 100
        if usage_percentage > threshold_percentage:
            response.append({
                'name': name,
                'type': res_type,
                'usage_percentage': usage_percentage
            })
    else:
        print(f'Warning: Could not get current size for {res_type} "{name}".')

    return response


while True:
    exceeding_resources = get_resources_exceeding_threshold(resources, threshold_percentage)
    for resource in exceeding_resources:
        name = resource['name']
        resource_type = resource['type']
        usage_percentage = resource['user_percentage']
        print(f'Warning: {resource_type.capitalize()} "{name}" is at {usage_percentage:.2f}% of its maximum size.')

    time.sleep(3600)


