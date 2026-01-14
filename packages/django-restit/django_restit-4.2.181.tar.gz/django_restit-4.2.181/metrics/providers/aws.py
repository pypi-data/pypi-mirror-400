import boto3
from datetime import datetime, timedelta
from rest import settings
from objict import objict
from rest.extra import hostinfo


METRIC_MAP = {
    "ec2": "AWS/EC2",
    "rds": "AWS/RDS",
    "redis": "AWS/ElastiCache",
    "cpu": "CPUUtilization",
    "memory": "FreeableMemory",
    'cache_memory': "BytesUsedForCache",
    "cache_usage": "DatabaseMemoryUsagePercentage",
    "connections": "DatabaseConnections",
    "swap": "SwapUsage",
    "cons": "DatabaseConnections",
    "cache_cons": "CurrConnections",
    "max": "Maximum",
    "min": "Minimum",
    "avg": "Average",
    "ec2_cons": "EstablishedConnections"
}


def publishLocalMetrics():
    # this will publish any local metrics to cloudwatch
    instance = getLocalEC2()
    pushMetric(
        METRIC_MAP["ec2_cons"],
        hostinfo.getTcpEstablishedCount(),
        "Count", instance)


def getLocalEC2():
    """
    {
        "id": "i-0c50eec6fdf91dcaf",
        "image_id": "ami-035e0c65b8a27be8d",
        "name": "epoc.pauth.io",
        "private_ip": "172.31.49.79",
        "public_ip": "35.88.50.208",
        "security_groups": [ {
                "id": "sg-0e15d7c997b004458",
                "name": "epoc_server"
            }],
        "service": "unknown",
        "state": "running",
        "subnet_id": "subnet-e282b1ca",
        "type": "t3.medium",
        "vpc_id": "vpc-000e9565",
        "zone": "us-west-2d"
    }
    """
    return getEC2ByIP(hostinfo.getHostIP())


def getClient(region=settings.AWS_REGION, service="cloudwatch"):
    key = settings.AWS_KEY
    secret = settings.AWS_SECRET
    return boto3.client(service, aws_access_key_id=key, aws_secret_access_key=secret, region_name=region)


def pushMetric(name, value, unit="Count", instance=None):
    """Push the custom metric to CloudWatch."""
    cloudwatch = getClient(service="cloudwatch")
    if instance is None:
        instance = getLocalEC2()
    return cloudwatch.put_metric_data(
        Namespace = 'CustomMetrics',
        MetricData = [
            {
                'MetricName': name,
                'Dimensions': [
                    {
                        'Name': 'InstanceId',
                        'Value': instance.id
                    },
                ],
                'Value': value,
                'Unit': unit
            },
        ]
    )


def buildQuery(id, instance, period=300, metric="cpu", namespace="rds", stat="max"):
    dname = "DBInstanceIdentifier"
    if namespace in ["ec2", "CustomMetrics"]:
        dname = "InstanceId"
    elif namespace == "redis":
        dname = "CacheClusterId"
    mstat = dict(Namespace=METRIC_MAP.get(namespace, namespace), MetricName=metric)
    mstat["Dimensions"] = [dict(Name=dname, Value=instance)]
    return dict(Id=id, MetricStat=dict(Metric=mstat, Period=period, Stat=METRIC_MAP.get(stat, stat)))
    

def getMetrics(instances, period=300, duration_seconds=900, metric="cpu", namespace="rds", stat="max"):
    cloudwatch = getClient(service="cloudwatch")
    query = []
    id_to_instance = {}
    metric_query = METRIC_MAP.get(metric, metric)
    for i in instances:
        name = i.replace("-", "_")
        key = F"{name}_{metric}"
        id_to_instance[key] = i
        query.append(buildQuery(key, i, period, metric=metric_query, namespace=namespace, stat=stat))
    response = cloudwatch.get_metric_data(
        MetricDataQueries=query,
        StartTime=(datetime.now() - timedelta(seconds=duration_seconds)).timestamp(),
        EndTime=datetime.now().timestamp())
    if "MetricDataResults" in response:
        output = objict()
        for resp in response.get("MetricDataResults"):
            output[id_to_instance.get(resp.get("Id"), "unknown")] = resp.get("Values")
        return output
    return response


def getMetricsList(instance, namespace="rds"):
    dname = "DBInstanceIdentifier"
    if namespace == "ec2" or namespace == "CustomMetrics":
        dname = "InstanceId"
    cloudwatch = getClient(service="cloudwatch")
    response = cloudwatch.list_metrics(
        Namespace=METRIC_MAP.get(namespace, namespace),
        Dimensions=[dict(Name=dname, Value=instance)])
    metrics_list = response['Metrics']
    metrics_names = [metric['MetricName'] for metric in metrics_list]
    return metrics_names


def getAllRDS(just_ids=False, region=settings.AWS_REGION):
    # Assume a boto3 session has already been started.
    ec2_client = getClient(region=region, service="rds")
    # Use the describe_db_instances method to list all RDS instances.
    response = ec2_client.describe_db_instances()
    instances = []
    for instance in response['DBInstances']:
        instances.append(_normalizeRDS(instance))

    if not just_ids:
        return instances
    return [inst.id for inst in instances]

# Loop through the list of instances and print the instance ID.


def getAllEC2(just_ids=False, region=settings.AWS_REGION):
    """
    This function returns a list with all EC2 instances in a region.
    """
    ec2_client = getClient(region=region, service="ec2")
    response = ec2_client.describe_instances()
    # log.prettyWrite(response)
    instances_reservation = response['Reservations']
    instances_description = []
    for res in instances_reservation:
        for instance in res['Instances']:
            instances_description.append(_normalizeEC2(instance))
    if not just_ids:
        return instances_description
    return [inst.id for inst in instances_description]


def getEC2ByIP(ip):
    # retreives the local ec2 instance details by private ip
    client = getClient(service="ec2")
    filters = [dict(Name="private-ip-address", Values=[ip])]
    resp = client.describe_instances(Filters=filters)["Reservations"]
    try:
        details = resp[0]['Instances'][0]
    except Exception:
        return None
    return _normalizeEC2(details)


def _normalizeEC2(details):
    name = "unknown"
    service = "unknown"
    for tag in details["Tags"]:
        if tag["Key"] == "Name":
            name = tag["Value"]
        elif tag["Key"] == "Service":
            service = tag["Value"]
    info = objict(
        id=details["InstanceId"],
        image_id=details["ImageId"],
        type=details["InstanceType"],
        name=name,
        service=service,
        security_groups=[])

    try:
        info.zone = details["Placement"]["AvailabilityZone"]
        info.public_ip = details.get("PublicIpAddress", "")
        info.private_ip = details.get("PrivateIpAddress", "")
        info.state = details["State"]["Name"]
        info.subnet_id = details["SubnetId"]
        info.vpc_id = details["VpcId"]
    except Exception:
        pass
    
    for group in details["SecurityGroups"]:
        info.security_groups.append(dict(name=group["GroupName"], id=group["GroupId"]))
    return info


def _normalizeRDS(details):
    info = objict(
        id=details["DBInstanceIdentifier"],
        instance_class=details["DBInstanceClass"],
        engine=details["Engine"],
        engine_version=details["EngineVersion"],
        name=details.get("DBName", ""),
        endpoint=objict(),
        zone=details["AvailabilityZone"],
        multi_az=details["MultiAZ"],
        status=details["DBInstanceStatus"],
        username=details["MasterUsername"]
    )

    for key, value in details["Endpoint"].items():
        info.endpoint[key.lower()] = value
    return info


from rest import log
def getAllRedis(just_ids=False, region=settings.AWS_REGION):
    # Assume a boto3 session has already been started.
    ec2_client = getClient(region=region, service="elasticache")
    # Use the describe_db_instances method to list all RDS instances.
    response = ec2_client.describe_cache_clusters()
    instances = []
    for instance in response['CacheClusters']:
        log.pp(instance)
        instances.append(objict(
            id=instance['CacheClusterId'],
            group_id=instance['ReplicationGroupId'],
            arn=instance["ARN"],
            type=instance['CacheNodeType'],
            engine=instance['Engine'],
            engine_version=instance['EngineVersion'],
            nodes=instance['NumCacheNodes'],
            zone=instance['PreferredAvailabilityZone'],
            status=instance['CacheClusterStatus']
        ))

    if not just_ids:
        return instances
    return [inst.id for inst in instances]


