import boto3
import json
import os

sns = boto3.resource('sns')
topic = sns.Topic(os.environ['TOPIC_ARN'])

def getquestion(event, context):
    print (event)
    try:
        for record in event['Records']:
            if record['eventName'] == 'INSERT':
                response = json.loads(record["dynamodb"]["NewImage"])
        return response
    except Exception as er:
        print(er)
def lambda_handler(event, context):
    try:
        question = getquestion(event, context)
        response = topic.publish(
            Message = 'FROM EMAIL: ' + question['UserEmailAddress'] + '  QUESTION: ' + question['questionText'] ,
            Subject = 'Question from :' + question['UserEmailAddress'],
            MessageStructure = 'string'
        )
        print(str(response) + ' has been published!')
        return response
    except Exception as er:
        print(er)
        print('Couldnt publish message to SNS')
    