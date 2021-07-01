import boto3
import json
import os
import logging
from collections import defaultdict
from functools import reduce
from boto3.dynamodb.conditions import Key, And

client = boto3.client('dynamodb', region_name='us-east-1')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def getMysfitsJson(items):
    # loop through the returned mysfits and add their attributes to a new dict
    # that matches the JSON response structure expected by the frontend.
    mysfitList = defaultdict(list)

    for item in items:
        mysfit = {}
        mysfit["mysfitId"] = item["MysfitId"]["S"]
        mysfit["Name"] = item["Name"]["S"]
        mysfit["Species"] = item["Species"]["S"]
        mysfit["Description"] = item["Description"]["S"]
        mysfit["Age"] = int(item["Age"]["N"])
        mysfit["GoodEvil"] = item["GoodEvil"]["S"]
        mysfit["LawChaos"] = item["LawChaos"]["S"]
        mysfit["ThumbImageUri"] = item["ThumbImageUri"]["S"]
        mysfit["ProfileImageUri"] = item["ProfileImageUri"]["S"]
        mysfit["Likes"] = item["Likes"]["N"]
        mysfit["Adopted"] = item["Adopted"]["BOOL"]
        mysfitList["mysfits"].append(mysfit)
    return mysfitList

def queryMysfitItems(filter, value):
    # Use the DynamoDB API Query to retrieve mysfits from the table that are
    # equal to the selected filter values.
    response = client.query(
        TableName=os.environ['MYSFITS_TABLE'],
        IndexName=filter+'Index',
        KeyConditions={
            filter: {
                'AttributeValueList': [
                    {
                        'S': value
                    }
                ],
                'ComparisonOperator': "EQ"
            }
        }
    )
    logging.info(response["Items"])
    mysfitList = getMysfitsJson(response["Items"])
    return json.dumps(mysfitList)
    
def getmysfits():
    response = client.scan(TableName='MysfitsTable')
    logging.info(response["Items"])
    mysfitList = getMysfitsJson(response["Items"])
    return json.dumps(mysfitList)

def lambda_handler(event, context):
    logger.info(event)
    if (event["rawQueryString"] == ''):
        print("Getting all values")
        items = getmysfits()
        logger.info(items)
    else:
        print("Getting filtered values")
        data = event["queryStringParameters"].items()
        for key, value in data:
            items = queryMysfitItems(key, value)
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': 'https://mythicalmysfits.houessou.com',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET',
            'Content-Type': 'application/json'
        },
        'body': items
    }

