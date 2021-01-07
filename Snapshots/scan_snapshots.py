import subprocess

snap_data = list()

date = 0

def scan_snapshots():

    snapshots = subprocess.check_output((
    "aws",
    "ec2",
    "describe-snapshots",
    "--owner-ids",
    "xxxxxxxxxxxx",
    "--query",
    "Snapshots[?StartTime<=`2020-05-01`].SnapshotId",
    "--output",
    "text"
    ))

    snapshots = snapshots.decode('utf-8')
    snapshots = snapshots.replace("\n","\t")
    snapshots = snapshots.split("\t")
    snapshots.pop()

    return snapshots

def get_info(snapshots):

    for i in snapshots:

        print(subprocess.check_output((
        "aws",
        "ec2",
        "describe-snapshots",
        "--snapshot-ids",
        "{}".format(i),
        "--query",
        "Snapshots[*].StartTime",
        "--output",
        "text"
        )))

        print(len(snapshots))


#test to verify the snapshots are from correct date
get_info(scan_snapshots())
