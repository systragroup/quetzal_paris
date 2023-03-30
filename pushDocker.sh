#!/bin/bash

# *******************************************************
# Ce script permet de mettre a jour le docker sur
# le repo ECR d'AWS.
#*******************************************************
cd ..

name=quetzal-paris
function_name=$name
model_dir=quetzal_paris

#ask user for a tag TODO use commit of model
#ask user for a tag
echo Enter a docker TAG:
read TAG

#Build docker image
docker build -t $name:$TAG -f $model_dir/Dockerfile .

aws_account=$(aws sts get-caller-identity | jq '.Account' | sed 's/"//g')
aws_region=$(aws configure get region)

#Tag docker
docker tag $name:$TAG $aws_account.dkr.ecr.$aws_region.amazonaws.com/$name:$TAG

#Push docket to aws
docker push $aws_account.dkr.ecr.$aws_region.amazonaws.com/$name:$TAG

read -p "Do you want tag this image as latest and update lambda (y/N)? " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
    docker tag $name:$TAG $aws_account.dkr.ecr.$aws_region.amazonaws.com/$name:latest
    docker push $aws_account.dkr.ecr.$aws_region.amazonaws.com/$name:latest
    aws lambda update-function-code --region $aws_region --function-name  $function_name \
        --image-uri $aws_account.dkr.ecr.$aws_region.amazonaws.com/$name:latest
fi