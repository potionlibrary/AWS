import subprocess

snap_data = list()

date = 0

def scan_snapshots():

    snapshots = subprocess.check_output((
    "aws",
    "ec2",
    "describe-snapshots",
    "--owner-ids",
    "xxxxxxxxxxxxx",
    "--query",
    "Snapshots[?StartTime<=`2020-10-01`].SnapshotId",
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


def delete_snapshots(snapshots):

    count = 0

    print("Snapshot delete candidates: {}".format(len(snapshots)))

    for i in snapshots:

        try:
            print(subprocess.check_output((
                "aws",
                "ec2",
                "delete-snapshot",
                "--snapshot-id",
                "{}".format(i)
            )))

            count = count + 1
            print("number of snapshots deleted: {}".format(count))

        except Exception as err:
            print("Could not delete {}".format(i))

delete_snapshots(scan_snapshots())
#test to verify the snapshots are from correct date
#get_info(scan_snapshots())
