#Use this script to recover instances
#To use this script you must enter an valid ami-id, valid instance ID

#libraries
import re
import time
import subprocess

# Instance variables for task
ami_id = 0
instance_id_1 = 0
instance_id_2 = 0 
type_of_server = 0
type_of_recovery = 0
instance_id_1_name = 0
instance_id_2_name = 0

volume_d_name_list = list()
volume_id_list_1 = list()
volume_id_list_2 = list()
volume_id_list_3 = list()
volume_id_list_4 = list()



#Buffer function to be used to synch aws with user consolse

def aws_synch(x):
    time.sleep(x)

# Ask the user for the AMI and instance ID that will be used for backup

def get_user_data():
    global ami_id, instance_id_1, type_of_server

    type_of_server = input("Please Enter type of xxx instance to be recovered(eg: ui, integ, grid, sso, db):")
    ami_id = input("Please Enter AMI id of backup to be used:")
    instance_id_1 = input("Please Enter instance ID of server to be recovered:")

#Get name of instance

def set_instance_name(instance_id):
    global  instance_id_1_name, instance_id_2_name

    #Queries Amazon for name of instance

    name = subprocess.check_output((
        "aws",
        "ec2",
        "describe-instances",
        "--instance-ids",
        "{}".format(instance_id),
        "--query",
        "Reservations[*].Instances[*].[Tags[?Key==`Name`].Value]",
        "--output",
        "text"
        ))

    #Removes the added formating and extra values assigns names of instances to be used.
    instance_id_1_name = name.decode('utf-8').rstrip("\n") 
    instance_id_2_name = name.decode('utf-8').rstrip("\n") + "-recovery"


#function decide type of recovery to be performed

def set_type_of_recovery(user_input):    
    global type_of_recovery

    print("\n\n\n")

    if user_input == "ui":
        print ("you have selected to recover a toapgi user interface node")
        type_of_recovery = "single"
    elif user_input == "integ":
        print ("you have selected to recover a toapgi intergration node")
        type_of_recovery = "single"
    elif user_input == "grid":
        print ("you have selected to recover a toapgi grid node")
        type_of_recovery = "single"
    elif user_input == "sso":
        print ("you have selected to recover a toapig single signon node")
        type_of_recovery = "single"
    elif user_input == "db":
        print ("you have selected to recover a toapgi database node")
        type_of_recovery = "multi"
    else: 
        print ("option is invalid") # todo: I want to make this a while loop incase someone puts in a wrong value - JW 8/19/2020


def create_instance(instance_name):
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
        "--subnet-id", "subnet-287a434c",
        "--key-name", "noss-zone-a-private",
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

    aws_synch(60)

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

    aws_synch(60)
        

def detach_volume(instance_id,volume_id,instance_name):

    subprocess.check_output((
        "aws","ec2",
        "detach-volume",
        "--instance-id",
        "{0}".format(instance_id),
        "--volume-id",
        "{0}".format(volume_id)

    ))

    print("detaching volume:" + volume_id + " instance-name:" + instance_name)
    aws_synch(20)

def attach_volume(instance_id,volume_id,device_id,instance_name):

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
    aws_synch(20)

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

    print(instance_id_1_name)
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

    print("Before:=============================================")

    print(instance_id_1_name)

    for i in volume_id_list_1:
        print(i)

    print(instance_id_2_name + ":" + instance_id_2)

    for i in volume_id_list_2:
        print(i)

    aws_synch(5)

    #Prints instance 1 and 2 information after the swap

    print("After:=============================================")

    print(instance_id_1_name)

    for i in volume_id_list_3:
        print(i)

    print(instance_id_2_name + ":" + instance_id_2)

    for i in volume_id_list_4:
        print(i)



#def final_remarks()

def perform_recovery():

    get_user_data()
    set_instance_name(instance_id_1)
    set_type_of_recovery(type_of_server)
    create_instance(instance_id_2_name)
    stop_instance(instance_id_1,instance_id_2)
    volume_swap(instance_id_1, instance_id_2)
    #final_remarks ill work on this next week 8/21/2020

perform_recovery()
