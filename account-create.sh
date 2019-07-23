#!/bin/bash
#Create a new user and create a new profile

#Create access keys
aws iam create-user --user-name devops-user1
credentials=$(aws iam create-access-key --user-name devops-user1 \
--query ‘AccessKey.[AccessKeyID, SecretAccessKey]’ \
--output text)

#Pull keys out of variables
access_key_id=$(echo $credentials | cut -d ‘ ’ -f 1)
secret_access_key=$(echo $credentials | cut -d ‘ ’ -f 2)

#Set the keys in profile
aws configure set profile.devops.aws_access_key_id “$access_key_id”
aws configure set profile.devops.aws_secret_access_key_id “$secret_access_key_id”
