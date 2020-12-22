# Added final remarks sections to compare volume lists, success messege if the volume are in correct order.
# On line 119 and 120 change the values "--subnet-id", "some-subnet", "--key-name", "some-key", to fit your evironment.
# Script has been testing on RHEL images, can be modified for windows if customer wants to host on another platform.
# Script execution speed has increased by 30% since 8/1/2020 - JW
# Script should utilize boto3 library in the future 9/9/2020 - JW

#libraries
import re
import time
import subprocess
import collections

# Instance variables for task
ami_id = 0
instance_id_1 = 0
instance_id_2 = 0 
instance_id_1_name = 0
instance_id_2_name = 0

volume_d_name_list = list()
volume_id_list_1 = list()
volume_id_list_2 = list()
volume_id_list_3 = list()
volume_id_list_4 = list()


# Collect infomration from users

def get_user_data():
    global ami_id, instance_id_1

    ami_id = input("Please Enter AMI id of backup to be used:")
    instance_id_1 = input("Please Enter instance ID of server to be recovered:")

#Buffer function to be used to synch aws with user consolse

def aws_synch(instance_id,timer):
    
    while(1):

        time.sleep(2)

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

        status = status.decode('utf-8')
        status = status.replace("\n","")

        if status == "stopping":
            print("Synchronizing with AWS...")
            time.sleep(timer)

        elif status == "pending":
            print("Synchronizing with AWS...")
            time.sleep(timer)

        elif status == "shutting-down":
            print("Synchronizing with AWS...")
            time.sleep(timer)

        elif status == "starting":
            print("Synchronizing with AWS...")
            time.sleep(timer)

        elif status == "running" or status == "stopped":
            break

        else:
            print("Instance returned: " + status + "status \n")
            time.sleep(timer)

#Get name of instance

def set_instance_name(id_1):

    global instance_id_1_name, instance_id_2_name

    #Queries Amazon for name of instance

    name = subprocess.check_output((
        "aws",
        "ec2",
        "describe-instances",
        "--instance-ids",
        "{}".format(id_1),
        "--query",
        "Reservations[*].Instances[*].[Tags[?Key==`Name`].Value]",
        "--output",
        "text"
        ))


    #Removes the added formating and extra values assigns names of instances to be used.
    instance_id_1_name = name.decode('utf-8').rstrip("\n") 
    instance_id_2_name = name.decode('utf-8').rstrip("\n") + "-recovery"


#function decide type of recovery to be performed

def create_instance(name_2, ami_id):

    global instance_id_2
    
    temp = subprocess.check_output((
        "aws",
        "ec2",
        "run-instances",
        "--image-id",
        "{}".format(ami_id),
        "--instance-type",
        "c4.2xlarge",
        "--count","1",
        "--subnet-id", "subnet-08768663",
        "--key-name", "basic",
        "--tag-specifications",
        "ResourceType=instance,Tags=[{{Key=Name,Value={}}}]".format(instance_id_2_name),
        "ResourceType=volume,Tags=[{{Key=Name,Value={}}}]".format(instance_id_2_name),
        "--output",
        "text"
        ))
    temp =  re.findall("\ti-[^\s]*",temp.decode("utf-8"))
    temp = temp[0].replace('\t','')
    instance_id_2 = temp 

    print("\n\n\n")
    print("Recovery instance has been created with following details.")
    print("Name:{0}".format(instance_id_2_name))
    print("Instance-Id:{0}".format(instance_id_2))
    print("\n\n\n")

    aws_synch(instance_id_2,5)

def stop_instance(id_1,id_2):

    action = subprocess.check_output((
        "aws",
        "ec2",
        "stop-instances",
        "--instance-ids",
        "{}".format(id_1),
        "{}".format(id_2),
        "--output",
        "json"
    ))

    print("\n" + action.decode('utf-8') + "\n")

    aws_synch(id_1,5)
    aws_synch(id_2,5)
        

def detach_volume(instance_id,volume_id,instance_name):

    global  instance_id_1_name, instance_id_2_name

    subprocess.check_output((
        "aws","ec2",
        "detach-volume",
        "--instance-id",
        "{0}".format(instance_id),
        "--volume-id",
        "{0}".format(volume_id)

    ))

    print("detaching volume:" + volume_id + " instance-name:" + instance_name)
    

def attach_volume(instance_id,volume_id,device_id,instance_name):

    global  instance_id_1_name, instance_id_2_name

    subprocess.check_output((
        "aws","ec2",
        "attach-volume",
        "--instance-id",
        "{0}".format(instance_id),
        "--volume-id",
        "{0}".format(volume_id),
        "--device",
        "{0}".format(device_id)
    ))

    
    print("attaching volume:" + volume_id + " instance-name:" + instance_name)

def get_volume_data(id):

    data=subprocess.check_output((
        "aws","ec2",
        "describe-instances",
        "--instance-ids",
        "{0}".format(id),
        "--query",
        "Reservations[*].Instances[*].[BlockDeviceMappings[*].[DeviceName,Ebs.VolumeId]]",
        "--output",
        "text"
        ))

    data = data.decode("utf-8")
    data = data.replace("\n","\t")
    data = data.split("\t")
    data.pop()

    return data

def volume_swap(id_1,id_2):
    global volume_d_name_list, volume_id_list_1, volume_id_list_2, volume_id_list_3, volume_id_list_4

    data_1 = get_volume_data(id_1)
    data_2 = get_volume_data(id_2)

    #When the volume data comes from amazon it comes in list([x,y]) form, where x = device name, and y = volume ID eg:(dev/sda1,vol-12345678)
    #Seperation of these elements into another list is needed to easly perform attach/dettach actions more simply

    for i in data_1[::2]:
        volume_d_name_list.append(i)

    for i in data_1[1::2]:
        volume_id_list_1.append(i)

    for i in data_2[1::2]:
        volume_id_list_2.append(i)

    #Loops through list and detaches volumes

    print(instance_id_1_name)
    for i in volume_id_list_1:
        detach_volume(instance_id_1,i,instance_id_1_name)

    print("\n")

    print(instance_id_2_name)
    for i in volume_id_list_2:
        detach_volume(instance_id_2,i,instance_id_2_name)

    print("\n")

    #Loops through list and attaches volumes
    print(instance_id_1_name)
    for i in range (len(volume_d_name_list)):
        attach_volume(instance_id_1,volume_id_list_2[i],volume_d_name_list[i],instance_id_1_name)

    print("\n")

    print(instance_id_2_name)
    for i in range (len(volume_d_name_list)):
        attach_volume(instance_id_2,volume_id_list_1[i],volume_d_name_list[i],instance_id_2_name)

    # Allocates new volume data after detach attach operation is done:

    data_3 = get_volume_data(id_1)
    data_4 = get_volume_data(id_2)

    #When the volume data comes from amazon it comes in list([x,y]) form, where x = device name, and y = volume ID eg:(dev/sda1,vol-12345678)
    #Seperation of these elements into another list is needed to easly perform attach/dettach actions more simply

    for i in data_3[1::2]:
        volume_id_list_3.append(i)

    for i in data_4[1::2]:
        volume_id_list_4.append(i)

    #Prints instance 1 and 2 information before the swap

def final_remarks(list1, list2):

    # Compares list of original instance with swapped instance to test if the volumes are alligned

    if collections.Counter(list1) == collections.Counter(list2):

        print("\n Volume ID to Device name matched, recovery complete please test your instance \n")

def perform_recovery():

    get_user_data()
    set_instance_name(instance_id_1)
    create_instance(instance_id_2_name, ami_id)
    stop_instance(instance_id_1,instance_id_2)
    volume_swap(instance_id_1, instance_id_2)
    final_remarks(volume_id_list_2,volume_id_list_3)

perform_recovery()

