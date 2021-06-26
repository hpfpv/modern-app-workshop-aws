import boto3
import json
import logging
from collections import defaultdict
from functools import reduce
from boto3.dynamodb.conditions import Key, And

client = boto3.client('dynamodb', region_name='us-east-1')

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

    #path /mysfits/{mysfitId}/adopt
def lambda_handler(event, context):
    mysfitId = event['pathParameters']['mysfitId']
    print('Got adopted mysfit:' + mysfitId)
    items = adoptMysfit(mysfitId)
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