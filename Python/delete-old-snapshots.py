import boto3
import pytz
from datetime import datetime, timedelta

# Get my AWS Account ID
myAccount = boto3.client('sts').get_caller_identity()['Account']

# Connect to EC2
client = boto3.client('ec2', region_name = 'ap-southeast-2')

# Get a list of snapshots for my AWS account (not all public ones)
snapshots = client.describe_snapshots(OwnerIds=[myAccount])['Snapshots']

# Find snapshots more than 30 days old
oldest_date = datetime.now(pytz.utc) - timedelta(days=30)
old_snapshots = [s for s in snapshots if s['StartTime'] < oldest_date]

# Delete the old snapshots
for s in old_snapshots:
  client.delete_snapshot(SnapshotId = s['SnapshotId'])
