"""AWS CloudWatch utilities for ElastiCache monitoring."""

import logging
import boto3
from datetime import timedelta, timezone

logger = logging.getLogger("elasticache-monitor-web")


def get_aws_engine_cpu_utilization(cluster_id: str, cache_cluster_id: str, 
                                    start_time, end_time, region: str = 'ap-south-1'):
    """Get AWS EngineCPUUtilization for comparison with Redis INFO CPU.
    
    Args:
        cluster_id: The replication group ID
        cache_cluster_id: The specific cache cluster/node ID (e.g., my-cluster-0001-001)
        start_time: Start of monitoring period (datetime)
        end_time: End of monitoring period (datetime)  
        region: AWS region
        
    Returns:
        dict with 'average' and 'maximum' CPU utilization percentages, or None values if unavailable
    """
    try:
        logger.info(f"{cache_cluster_id}: Fetching EngineCPUUtilization for cluster {cluster_id}, region {region}")
        cloudwatch = boto3.client('cloudwatch', region_name=region)

        # Extend time window slightly to ensure we capture the monitoring period
        # Make times timezone-aware to match CloudWatch response format
        utc_tz = timezone.utc
        extended_start = (start_time - timedelta(minutes=2)).replace(tzinfo=utc_tz)
        extended_end = (end_time + timedelta(minutes=2)).replace(tzinfo=utc_tz)

        logger.info(f"{cache_cluster_id}: Time window: {extended_start} to {extended_end}")

        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/ElastiCache',
            MetricName='EngineCPUUtilization',
            Dimensions=[
                {'Name': 'CacheClusterId', 'Value': cache_cluster_id},
            ],
            StartTime=extended_start,
            EndTime=extended_end,
            Period=60,  # 1-minute granularity
            Statistics=['Average', 'Maximum']
        )

        datapoints = response.get('Datapoints', [])
        logger.info(f"{cache_cluster_id}: Found {len(datapoints)} EngineCPUUtilization datapoints")

        if datapoints:
            # Sort by timestamp and filter to our monitoring window
            datapoints.sort(key=lambda x: x['Timestamp'])

            # Filter datapoints that overlap with our monitoring window
            relevant_datapoints = []
            for dp in datapoints:
                dp_time = dp['Timestamp']
                if extended_start <= dp_time <= extended_end:
                    relevant_datapoints.append(dp)

            if relevant_datapoints:
                # Extract average and maximum values
                avg_values = [dp['Average'] for dp in relevant_datapoints if 'Average' in dp]
                max_values = [dp['Maximum'] for dp in relevant_datapoints if 'Maximum' in dp]

                avg_engine_cpu = sum(avg_values) / len(avg_values) if avg_values else None
                max_engine_cpu = max(max_values) if max_values else None

                logger.info(f"{cache_cluster_id}: AWS EngineCPUUtilization - Avg: {avg_engine_cpu:.2f}%, Max: {max_engine_cpu:.2f}% (from {len(relevant_datapoints)} datapoints)")
                return {'average': avg_engine_cpu, 'maximum': max_engine_cpu}

        logger.warning(f"{cache_cluster_id}: No EngineCPUUtilization data found")
        return {'average': None, 'maximum': None}

    except Exception as e:
        logger.error(f"{cache_cluster_id}: Failed to get EngineCPUUtilization: {e}")
        return {'average': None, 'maximum': None}

