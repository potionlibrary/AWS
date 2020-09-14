# Use this script to create worker nodes for environment
# Edit lines 10, 17, 28, 29 to fit your environment
# Tested on RHEL 8, 9-14-2020 - JW

#libraries
import re
import subprocess


# Instance variables for task
suite_no = input("Enter suite No. for instance Name (eg:No.1,No.2,No.3):")
ami_id = input("Enter AMI ID instance will be created from:")
instance_name = "env-name".format(suite_no)

# Possible addition in future iteration
# subnet_id = input("Enter subnet ID where these instances will be located:")

for i in range (3, 11):

    create = subprocess.check_output((
        "aws",
        "ec2",
        "run-instances",
        "--image-id",
        "{}".format(ami_id),
        "--instance-type",
        "c4.2xlarge",
        "--count","1",
        "--subnet-id", "subnet-xxxxx",
        "--key-name", "yourkey",
        "--tag-specifications",
        "ResourceType=instance,Tags=[{{Key=Name,Value={}}}]".format(instance_name + "{}".format(i)),
        "ResourceType=volume,Tags=[{{Key=Name,Value={}}}]".format(instance_name + "{}".format(i)),
        "--output",
        "text"
        ))
