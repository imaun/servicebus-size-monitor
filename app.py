import os
from dotenv import load_dotenv
from azure.identity import AzureCliCredential
from azure.mgmt.servicebus import ServiceBusManagementClient
from azure.monitor.query import MetricsQueryClient
from azure.servicebus.management import ServiceBusAdministrationClient
import time

load_dotenv()

credentials = AzureCliCredential()

subscription_id = os.getenv('SUBSCRIPTION_ID')

# servicebus_client = ServiceBusManagementClient(credentials, subscription_id)
# metrics_client = MetricsQueryClient(credentials)

resource_group_name = os.getenv('RESOURCE_GROUP_NAME')
namespace = os.getenv('SERVICEBUS_NAMESPACE')
full_namespace = f'{namespace}.servicebus.windows.net'
threshold_percentage = float(os.getenv('THRESHOLD_PERCENTAGE'))
timer_interval = int(os.getenv('TIMER_INTERVAL'))

# queues = servicebus_client.queues.list_by_namespace(resource_group_name, namespace)

# topics = servicebus_client.topics.list_by_namespace(resource_group_name, namespace)

admin_client = ServiceBusAdministrationClient(
    fully_qualified_namespace=full_namespace,
    credential=credentials
)

queues = admin_client.list_queues()
topics = admin_client.list_topics()

resources = []

for queue in queues:
    queue_name = queue.name
    max_size_bytes = queue.max_size_in_megabytes * 1024 * 1024
    print(f'{queue.name}: {queue.max_size_in_megabytes}')
    # resource_id = (
    #     f'/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}'
    #     f'/providers/Microsoft.ServiceBus/namespaces/{namespace}/queues/{queue_name}'
    # )
    # print(f'{queue.name} id: "{resource_id}"')
    resources.append({
        'name': queue_name,
        'type': 'queue',
        # 'resource_id': resource_id,
        'max_size': max_size_bytes
    })


for topic in topics:
    topic_name = topic.name
    max_size_bytes = topic.max_size_in_megabytes * 1024 * 1024 
    print(f'{topic.name}: {topic.max_size_in_megabytes}')
    # resource_id = (
    #     f'/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}'
    #     f'/providers/Microsoft.ServiceBus/namespaces/{namespace}/topics/{topic_name}'
    # )
    # print(f'{topic.name} id: "{resource_id}"')
    resources.append({
        'name': topic_name,
        'type': 'topic',
        # 'resource_id': resource_id,
        'max_size': max_size_bytes
    })


def get_resource_size(resource):
    # metrics_data = metrics_client.query_resource(
    #     resource_id,
    #     metric_names=['Size'],
    #     timespan=None, # Get the latest value
    #     granularity=None,
    #     aggregations=['Max'],
    # )

    # if metrics_data.metrics:
    #     size_metric = metrics_data.metrics[0]
    #     if size_metric.timeseries:
    #         data_points = size_metric.timeseries[0].data
    #         if data_points:
    #             current_size = data_points[-1].max
    #             return current_size
    # return None
    if resource['type'] == 'queue':
        runtime_properties = admin_client.get_queue_runtime_properties(resource['name'])
        current_size = runtime_properties.size_in_bytes
        return current_size
    elif resource['type'] == 'topic':
        runtime_properties = admin_client.get_topic_runtime_properties(resource['name'])
        current_size = runtime_properties.size_in_bytes
        return current_size
    else:
        return None
    
def to_megabytes(bytes_value):
    megabytes = bytes_value / (1024 * 1024)
    return f"{megabytes:.2f} MB"


def get_resources_exceeding_threshold():
    response = []
    if not resources:
        print('NO resources found!')
        exit(-1)
    
    print('**********************************************************************************')
    for resource in resources:
        name = resource['name']
        res_type = resource['type']
        # res_id = resource['resource_id']
        max_size = resource['max_size']

        current_size = get_resource_size(resource)

        if current_size is not None:
            usage_percentage = (current_size / max_size) * 100
            print(f'- {name} usage is { usage_percentage:.2f} | current size is: {to_megabytes(current_size)}')
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
    exceeding_resources = get_resources_exceeding_threshold()
    for resource in exceeding_resources:
        name = resource['name']
        resource_type = resource['type']
        usage_percentage = resource['user_percentage']
        print(f'Warning: {resource_type.capitalize()} "{name}" is at {usage_percentage:.2f}% of its maximum size.')

    time.sleep(timer_interval)