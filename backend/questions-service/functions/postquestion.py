import boto3
import json
import os
import logging
import uuid
import random
import time

client = boto3.client('dynamodb')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(event)
    eventBody = json.loads(event["body"])
    question = {}
    question["QuestionId"] = {
        "S": str(uuid.uuid4())
        }
    question["QuestionText"] = {
        "S": eventBody["questionText"]
        }
    question["UserEmailAddress"] = {
        "S": eventBody["email"]
        }

    response = client.put_item(
        TableName=os.environ['MYSFITS_QUESTIONS_TABLE'],
        Item=question
        ) 
    logger.info(response)   
    responseBody = {}
    responseBody["status"] = "success"
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': 'https://mythicalmysfits.houessou.com',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET',
            'Content-Type': 'application/json'
        },
        'body': json.dumps(responseBody)  
    }

