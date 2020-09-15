
import boto3
import os
import sys
import traceback
import datetime
import time

# List every region you'd like to scan.  We'll need to update this if AWS adds a region
aws_regions = ['region']


# List of the tags on instances we want to look for to backup
tags_to_find = ['Backup']


#Scan instances with tags
def scanned_tagged_instances(ec2):
    
    print("Scanning for volumes with tags ({})".format(tags_to_find))

    
    volumes = ec2.describe_volumes(Filters=[{'Name': 'tag-key', 'Values': tags_to_find}])

        
    # TODO: Help I can't do this pythonically...  PR welcome...
    volumes_array = []
    for volume in volumes['Volumes']:
        if volume['State'] in ['available','in-use']:
            volumes_array.append(volume)

    # Get our volumes and iterate through them...
    if len(volumes_array) == 0:
        return
    print("  Found {} volumes to backup...".format(len(volumes_array)))
    for volume in volumes_array:
        print("  Volume ID: {}".format(volume['VolumeId']))
        # pprint(volume)

# If ran on the CLI, go ahead and run it
if __name__ == "__main__":
    lambda_handler({},{})
