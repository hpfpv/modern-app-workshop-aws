import boto3
import json
import logging
from collections import defaultdict
from functools import reduce
from boto3.dynamodb.conditions import Key, And

client = boto3.client('dynamodb', region_name='us-east-1')

def getMysfitJson(item):
    mysfit = {}
    mysfit["mysfitId"] = item["MysfitId"]["S"]
    mysfit["name"] = item["Name"]["S"]
    mysfit["age"] = int(item["Age"]["N"])
    mysfit["goodevil"] = item["GoodEvil"]["S"]
    mysfit["lawchaos"] = item["LawChaos"]["S"]   
    mysfit["species"] = item["Species"]["S"]
    mysfit["description"] = item["Description"]["S"]
    mysfit["thumbImageUri"] = item["ThumbImageUri"]["S"]
    mysfit["profileImageUri"] = item["ProfileImageUri"]["S"]
    mysfit["likes"] = item["Likes"]["N"]
    mysfit["adopted"] = item["Adopted"]["BOOL"] 
    return mysfit

def getMysfit(mysfitId):
    response = client.get_item(
        TableName='MysfitsTable',
        Key={
            'MysfitId': {
                'S': mysfitId
            }
        }
    )
    response = getMysfitJson(response["Item"])
    return json.dumps(response)

#path /mysfits/{mysfitId}
def lambda_handler(event, context):
    mysfitId = event['pathParameters']['mysfitId']
    print('Getting mysfit:' + mysfitId)
    items = getMysfit(mysfitId)
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': '*',
            'Content-Type': 'application/json'
        },
        'body': items
    }