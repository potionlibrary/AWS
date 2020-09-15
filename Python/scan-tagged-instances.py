
import boto3

session = boto3.Session(profile_name='default')

ec2 = boto3.client('ec2')
response = ec2.describe_instances()
print(response)
