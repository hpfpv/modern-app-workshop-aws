import boto3
import json
import logging
from collections import defaultdict
from functools import reduce
from boto3.dynamodb.conditions import Key, And

client = boto3.client('dynamodb', region_name='us-east-1')

def getMysfitsJson(items):
    # loop through the returned mysfits and add their attributes to a new dict
    # that matches the JSON response structure expected by the frontend.
    mysfitList = defaultdict(list)

    for item in items:
        mysfit = {}
        mysfit["mysfitId"] = item["MysfitId"]["S"]
        mysfit["name"] = item["Name"]["S"]
        mysfit["species"] = item["Species"]["S"]
        mysfit["description"] = item["Description"]["S"]
        mysfit["age"] = int(item["Age"]["N"])
        mysfit["goodevil"] = item["GoodEvil"]["S"]
        mysfit["lawchaos"] = item["LawChaos"]["S"]
        mysfit["thumbImageUri"] = item["ThumbImageUri"]["S"]
        mysfit["profileImageUri"] = item["ProfileImageUri"]["S"]
        mysfit["likes"] = item["Likes"]["N"]
        mysfit["adopted"] = item["Adopted"]["BOOL"]
        mysfitList["mysfits"].append(mysfit)
    return mysfitList
    
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
    
def getmysfits():
    response = client.scan(TableName='MysfitsTable')
    logging.info(response["Items"])
    mysfitList = getMysfitsJson(response["Items"]) 
    return json.dumps(mysfitList)
    
def queryMysfitItems(filter, value):
    # Use the DynamoDB API Query to retrieve mysfits from the table that are
    # equal to the selected filter values.
    response = client.query(
        TableName='MysfitsTable',
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
    mysfitList = getMysfitsJson(response["Items"])
    return json.dumps(mysfitList)
    
# Retrive a single mysfit from DynamoDB using their unique mysfitId    
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

# increment the number of likes for a mysfit by 1
def likeMysfit(mysfitId):
    response = client.update_item(
        TableName='MysfitsTable',
        Key={
            'MysfitId': {
                'S': mysfitId
            }
        },
        UpdateExpression="SET Likes = Likes + :n",
        ExpressionAttributeValues={':n': {'N': '1'}}
    )

    response = {}
    response["Update"] = "Success";

    return json.dumps(response)

# mark a mysfit as adopted
def adoptMysfit(mysfitId):
    response = client.update_item(
        TableName='MysfitsTable',
        Key={
            'MysfitId': {
                'S': mysfitId
            }
        },
        UpdateExpression="SET Adopted = :b",
        ExpressionAttributeValues={':b': {'BOOL': True}}
    )

    response = {}
    response["Update"] = "Success";

    return json.dumps(response)

def lambda_handler(event, context):
    if (event['path'] == '/mysfits' and (event["queryStringParameters"] is None)):
        print("Getting all values")
        items = getmysfits()
    elif (event['path'] == '/mysfits' and event["queryStringParameters"] is not None) :
        if ('LawChaos' in str(event["queryStringParameters"])) :
            filter = 'LawChaos'
            value = event["queryStringParameters"]['LawChaos']
        else:
            filter = 'GoodEvil' 
            value = event["queryStringParameters"]['GoodEvil'] 
        print('Getting filtered values')
        items = queryMysfitItems(filter, value)
    elif (event['resource'] == '/mysfits/{mysfitId}'):
        mysfitId = event['pathParameters']['mysfitId']
        print('Getting mysfit:' + mysfitId)
        items = getMysfit(mysfitId)
    elif (event['resource'] == '/mysfits/{mysfitId}/like'):
        mysfitId = event['pathParameters']['mysfitId']
        print('One like for mysfit:' + mysfitId)
        items = likeMysfit(mysfitId)
    elif (event['resource'] == '/mysfits/{mysfitId}/adopt'):
        mysfitId = event['pathParameters']['mysfitId']
        print('Got adopted mysfit:' + mysfitId)
        items = adoptMysfit(mysfitId)
    elif (event['path'] == '/'):
        items = json.dumps({"message" : "Nothing here, used for health check. Try /mysfits instead."})
    else:
        print ('Unable to retrieve values')
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
        
  


