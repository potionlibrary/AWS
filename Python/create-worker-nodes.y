#Use this script to create worker nodes for environment
#Creates Worker nodes with appended suite # starting from 3 and ending in 10

#libraries
import re
import subprocess

# Instance variables for task
ami_id = "ami-xxxxx"
instance_id_1_name = "yourappname"

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
        "ResourceType=instance,Tags=[{{Key=Name,Value={}}}]".format(instance_id_1_name + "{}".format(i)),
        "ResourceType=volume,Tags=[{{Key=Name,Value={}}}]".format(instance_id_1_name + "{}".format(i)),
        "--output",
        "text"
        ))
