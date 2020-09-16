#libraries
import boto3
import subprocess

#instance variables
aws_region = "test"
tags_to_find = ['Backup','Name']

#code
session = boto3.Session(profile_name='default')

ec2 = boto3.client('ec2')

response = ec2.describe_instances(Filters=[{'Name' : 'tag-key','Values' : tags_to_find }])

print(response)
