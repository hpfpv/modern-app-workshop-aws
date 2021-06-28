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

    client.put_item(
        TableName=os.environ['MYSFITS_QUESTIONS_TABLE'],
        Item=question
        )
    
    response = {}
    response["headers"] = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*", "Access-Control-Allow-Methods": "*"}
    response["statusCode"] = 200
    responseBody = {}
    responseBody["status"] = "success"
    response["body"] =  json.dumps(responseBody)
    logger.info(response)
    return response