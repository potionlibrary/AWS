#!/bin/bash

data=$(\
aws secretsmanager get-secret-value\
 --secret-id jw/001\
 --query SecretString\
 --output text | tr -d '"')

user=$(echo $data | tr -d '{}' | cut -d "," -f 1 | cut -d ":" -f 2)
pass=$(echo $data | tr -d '{}' | cut -d "," -f 2 | cut -d ":" -f 2)


printf "$user\n"
printf "$pass\n"
