import logging
import boto3
import json
import os

sns = boto3.resource('sns')
topic = sns.Topic(os.environ['TOPIC_ARN'])
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(event)
    try:
        for record in event['Records']:
            if record['eventName'] == 'INSERT':
                question = record.get('dynamodb').get('NewImage')
                logger.info(question)
                QuestionText = question["QuestionText"]
                UserEmailAddress = question["UserEmailAddress"]
            response = topic.publish(
                Message = 'FROM EMAIL: ' + UserEmailAddress['S'] + '  QUESTION: ' + QuestionText['S'] ,
                Subject = 'Question from :' + UserEmailAddress['S'] ,
                MessageStructure = 'string'
            )
            print(str(response) + ' has been published!')
        return response
    except Exception as er:
        print(er)
        print('Couldnt publish message to SNS')
    