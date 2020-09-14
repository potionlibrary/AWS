
import boto3
import os
import sys
import traceback
import datetime
import time

# List every region you'd like to scan.  We'll need to update this if AWS adds a region
aws_regions = ['region']


# List of the tags on instances we want to look for to backup
tags_to_find = ['backupTest', 'BackupTest']


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

        # Get the name of the instance, if set...
        try:
            volume_name = [t.get('Value') for t in volume['Tags']if t['Key'] == 'Name'][0]
        except:
            volume_name = volume['VolumeId']

        # Get the instance attachment, if attached (mostly just to print)...
        try:
            instance_id = volume['Attachments'][0]['InstanceId']
        except:
            instance_id = 'No attachment'

        print("Volume Name: {}".format(volume_name))
        print("Instance ID: {}".format(instance_id))
    
        # Get days to retain the backups from tags if set...
        try:
            retention_days = [int(t.get('Value')) for t in volume['Tags']if t['Key'] == 'Retention'][0]
        except:
            retention_days = default_retention_time
        print('       Time: {} days'.format(retention_days))
    
        # Catch if we were dry-running this
        if dry_run:
            print("Backup Name: {}".format("{}-backup-{}".format(volume_name, datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S.%f'))))
            print("DRY_RUN: Would have created a volume backup...")
        else:
            # Create our AMI
            try:
                # Get all the tags ready that we're going to set...
                delete_fmt = (datetime.date.today() + datetime.timedelta(days=retention_days)).strftime('%m-%d-%Y')
                tags = []
                tags.append({'Key': 'Name', 'Value': "{}-backup-{}".format(volume_name, datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S.%f'))})
                tags.append({'Key': 'DeleteAfter', 'Value': delete_fmt})
                tags.append({'Key': 'OriginalVolumeID', 'Value': volume['VolumeId']})
                tags.append({'Key': global_key_to_tag_on, 'Value': 'true'})
                # Also grab our old tags
                try:
                    if 'Tags' in volume:
                        for index, item in enumerate(volume['Tags']):
                            if item['Key'].startswith('aws:'):
                                print("Modifying internal aws tag so it doesn't fail: {}".format(item['Key']))
                                tags.append({'Key': 'internal-{}'.format(item['Key']), 'Value': item['Value']})
                            elif item['Key'] == 'Name':
                                pass  # Skip our old name, we're overriding it
                            else:
                                tags.append(item)
                except:
                    pass

                #snapshot = ec2.create_snapshot(
                 #   Description="Automatic Backup of {} from {}".format(volume_name, volume['VolumeId']),
                 #   VolumeId=volume['VolumeId'],
                 #   TagSpecifications=[{
                 #       'ResourceType': 'snapshot',
                  #      'Tags': tags,
                  #  }],
                    # DryRun=True
                #)
                #print("Snapshot ID: {}".format(snapshot['SnapshotId']))

            except Exception as e:
                print('Caught exception while trying to process volume')
                pprint(e)

    

# If ran on the CLI, go ahead and run it
if __name__ == "__main__":
    lambda_handler({},{})
