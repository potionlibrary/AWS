import boto3


aws_regions = ['us-east-2']
tags_to_find = ['Backup', 'backup']

def lambda_handler(event, context):
    
    ec2 = boto3.client('ec2', region_name='us-east-2')
    response = ec2.describe_instances(Filters=[{'Name' : 'tag-key','Values' : tags_to_find },]) 
    
    for i in response["Reservations"]:
        print(i["Instances"][0]["PrivateDnsName"])
        print(i["Instances"][0]["PrivateIpAddress"])
        print(i["Instances"][0]["State"])
        print(i["Instances"][0]["InstanceId"])
        print(i["Instances"][0]["BlockDeviceMappings"])
