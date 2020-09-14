# checks subnet for available ipv4 addresses
# final output needs trimming 

import re
import subprocess

data = subprocess.check_output((
        "aws",
        "ec2",
        "describe-subnets",
        "--query",
        "Subnets[*].{ID:SubnetId}",
        "--output",
        "text"
        ))

data = data.decode("utf-8")
data = data.replace("\n","\t")
data = data.split("\t")
data.pop()

#aws ec2 describe-subnets --query 'Subnets[*].{ID:AvailableIpAddressCount}'

for i in data:

    ips = subprocess.check_output((
        "aws",
        "ec2",
        "describe-subnets",
        "--subnet-ids",
        "{}".format(i),
        "--query",
        "Subnets[*].{ID:AvailableIpAddressCount}",
        "--output",
        "text"
        ))

    print(ips)
