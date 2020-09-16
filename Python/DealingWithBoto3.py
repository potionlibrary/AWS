import boto3

client = boto3.client('ec2')

response = client.describe_instances()
block_mappings = (block_mapping
                  for reservation in response["Reservations"]
                  for instance in reservation["Instances"]
                  for block_mapping in instance["BlockDeviceMappings"])

for block_mapping in block_mappings:
  print(block_mapping["Ebs"]["DeleteOnTermination"])

#=======================================================================================:

import jmespath
import boto3

client = boto3.client('ec2')

response = client.describe_instances()
print(jmespath.search(
    "Reservations[].Instances[].DeviceBlockMappings[].Ebs.DeleteOnTermination", 
    response
))
