#libraries
import boto3

#instance variables
aws_region = "test"

#code
session = boto3.Session(profile_name='default')

ec2 = boto3.client('ec2')

response = ec2.describe_instances()

#rint("Scanning region: {}".format(aws_region))

for i in response

print(response)
