#!/bin/bash

printf "\n\n\n"

printf "Please enter the suite number you want to work with ():"
read suite_no

printf "\n\n\n"

printf "Please enter tag Key to be added:"
read suite_tag_key

printf "\n\n\n"

printf "Please enter tag Value associated with Key:"
read suite_tag_value

printf "\n\n\nPlease wait while the tags are added to $suite_no instances\n"


instance_ids=$(aws ec2 describe-instances \
--filters "Name=tag:Name,Values=*-$suite_no-*" \
--query 'Reservations[*].Instances[*].{Instance:InstanceId}' \
--output text)

for i in $instance_ids; do

    aws ec2 create-tags --resources $i --tags Key=$suite_tag_key,Value=$suite_tag_value

done


printf "\n\n\nDone...\n"
