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

# increment the number of likes for a mysfit by 1
def likeMysfit(mysfitId):
    response = client.update_item(
        TableName=os.environ['MYSFITS_TABLE'],
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
#path /mysfits/{mysfitId}/like
def lambda_handler(event, context):
    logger.info(event)
    mysfitId = event['pathParameters']['mysfitId']
    print('One like for mysfit:' + mysfitId)
    items = likeMysfit(mysfitId)
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': 'https://mythicalmysfits.houessou.com',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET, POST',
            'Content-Type': 'application/json'
        },
        'body': items
    }