#base status check code for EC2 instances

# will be fed as a condition to buffer actions in the system level

import subprocess

instance_id = "some-instance-id"

status = subprocess.check_output((
        "aws",
        "ec2",
        "describe-instances",
        "--instance-ids",
        "{}".format(instance_id),
        "--query",
        "Reservations[*].Instances[*].{State:State.Name}",
        "--output",
        "text"
        ))

print(status)
