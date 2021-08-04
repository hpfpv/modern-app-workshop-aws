# Sample modern web application with AWS SAM

Hi guys!
In this blog, we'll be building a modern application on AWS with Python following  [this](https://aws.amazon.com/getting-started/hands-on/build-modern-app-fargate-lambda-dynamodb-python/) tutorial. We will build a sample website called Mythical Mysfits that enables visitors to adopt a fantasy creature (mysfit) as pet.
The main difference with the tutorial is that we will use the AWS Serverless Application Model SAM Framework to deploy the backend services - API, Lambda (instead of Fargate), DynamoDB and Cognito).

We will use all the Frontend provided code from the tutorial - just working on the backend services here with Python as our programming language. 

**Application Architecture**
![arch-diagram.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1625486964545/Lbz8vXvyT.png)

The steps to complete this tutorial are:
- Build a static website to serve static content - S3 + CloudFront
- Enable users to retrieve, filter, like and adopt mysfits - API Gateway + AWS Lambda + DynamoDB - *microservice #1*
- Enable users authentication - Cognito
- Enable users to contact the Mythical Mysfits staff via a Contact Us button - API Gateway + AWS Lambda + DynamoDB + SNS - *microservice #2*
- Capture user behavior with a clickstream analysis - API Gateway + Lambda + Kinesis - *microservice #3*
- Use Machine Learning to recommend a Mysfit - API Gateway + Lambda + SageMaker - *microservice #4*

**GitHub repository: https://github.com/hpfpv/mythicalmysfits-aws**

**Created web app: https://mythicalmysfits.houessou.com**

Alright, let's break this down.

### Static website with S3 and CloudFront

![website.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1625482335139/vNsCxOQm8.png)
This one is straight forward. Use the aws cli to create a bucket and copy the *xx/web/index*.html file. Modify the bucket policy to allow public read and set the bucket to serve static website content: 
![s3bucket1.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1623608041286/IR6f9aNJQ.png)
For this project, we have also implemented a CloudFront distro with a custom domain name.
Accessing the bucket display an HTML page with a list of mysfits stored in a dict variable in the code.
We need to load the mysfits from a DynamoDB Table for dynamic operations like get and update.

### Backend microservice #1: Operations on Mysfits + user authentication

![micrservice 1.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1625498559323/Y-G6HZllM.png)

This microservice is deployed using the SAM Framework and requires 4 REST APIs coupled with 4 Lambda functions (getmyfits, getmyfit, likemysfit, adoptmysfit) which perform QUERY and UPDATE actions on the Mysfits DynamoDB Table also created in the same stack.
Since *adopt* and *like* mysfit operations are allowed for signed in users only, we need to create a Cognito User Pool and Client to be set as authorizer for those functions.

In the SAM template file, we will provisionne below resources:

**DynamoDB Table to store mysfits**

![dynamoDB.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1625482141148/FGJp_c9_Y.png)

Make sure to set the GlobalSecondaryIndex to allow filtering on GoodEvil and LawChaos attributes.

**Cognito User Pool and Client**

We need to add an authorizer to our API Gateway in other to authenticate and authorize users before they could like or adopt a mysfit. For that, we first need to create a Cognito user pool and client in our stack.

- Cognito User Pool

![UserPool.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1625482885429/3sNBT0s2p.png)

- Cognito User Pool Client

![userpoolclient.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1625482910260/nMnmO8R5qF.png)

- Cognito User Pool Domain

![userpooldomain.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1625482922187/YW6zEkLW8.png)

We can now reference this cognito user pool and client as authorizer for our main HTTP API.

**Main HTTP API**

![httpapi.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1625483158085/0uy3mkZ2J.png)

The authorizer settings has been added to the HTTP API properties. It uses a JWT configuration with our cognito user pool as issuer and user pool client as audience. I have also added the CORS settings to allow GET and POST requests only from the website.

**Lambda functions associated to the main HTTPApi**

Lambda code is written in Python and performs CRUD operations on the DynamoDB table containing mysfits items based on the event received - in our case the HTTPApi path and request parameters.

 I have set the 4 functions below:
- **getmysfits:**
Retrieve all mysfits for the main page and performs filtering based on GoodEvil or LawChaos value

*SAM ressource*

![getmysfits.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1625484019918/2-UBPtRv0.png)

*Function code*

```
# Returns a list of filtered mysfits based on queryParameters
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
    mysfitList = getMysfitsJson(response["Items"])  # getMysfitsJson adds mysfits attributes to a dict that matches the JSON response structure
    return json.dumps(mysfitList)
 
# Returns all mysfits list   
def getmysfits():
    response = client.scan(TableName='MysfitsTable')
    logging.info(response["Items"])
    mysfitList = getMysfitsJson(response["Items"]) 
    return json.dumps(mysfitList)

def lambda_handler(event, context):
    if (event["rawQueryString"] == ""): # check the presence of queryParameters in the request
        print("Getting all values")
        items = getmysfits()
    else:
        print("Getting filtered values")
        data = event["queryStringParameters"].items()
        for key, value in data:
            items = queryMysfitItems(key, value)
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
``` 

- **getmysfit:**
Return one item based on path parameters {MysfitsId}

*SAM resource*

![getmysfit.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1625484355098/oq8DO8rI6.png)

- **likemysfit:**
Increment the like value for a specified mysfit

*SAM resource*

![likemysfit.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1625484396268/qH8z19k4g.png)

- **adoptmysfit:**
Update the adopt value to TRUE for a specified mysfit

*SAM resource*

![adoptmysfit.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1625484422581/SlE-7vQNp.png)

When writing your code, remember to break down things as much as possible to keep your functions simple.
Build your SAM template and test the functions and APIs locally then deploy to AWS (which will create a CloudFormation stack with the resources specified in the template file).
Validate your config by testing the APIs with POSTMAN. You can use the **AWS hosted UI** which provides an OAuth 2.0 authorization server with built-in webpages that can be used to sign up and sign in users (required to like and adopt a mysfit).

At this stage, we have successfully created the microservice needed to serve the frontend (retrieve all mysfits, filter mysfits, like and adopt mysfits). We only need to update the frontend html files by adding the HTTP API url, Cognito user pool and Cognito user pool client.

### Backend microservice #2: Enable users to contact the Mythical Mysfits

![questions microservice 2.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1625498667351/ptkCnH8Ag.png)

This microservice is deployed as a seperate CloudFormation stack and also using the SAM Framework. It requires 1 REST API coupled with 1 Lambda function which writes in a DynamoDB table to allow users to send questions through a form on our website. Once a question is posted in the table, a stream triggers another function which uses SNS SDK to publish the question (received as an event) as a topic message. All resources required are defined in the SAM template file:

**DynamoDB Table to store questions**

![questions dynamotable.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1625499643309/OLyIITXqf.png)

DynamoDB table to store users questions. Stream enabled with NEW_IMAGE view type.

**Questions SNS Topic**

![questions sns topic.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1625499697572/1qTT2M0Cx.png)

SNS Topic which to retrieve questions from the dynamodb table and send notification to topic subscribers (Mythical Mysfits staff).

**Questions API**

![questions http api.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1625499848674/rJAJ28yNm.png)

HTTP Api which will trigger our lambda function to post a question to the questions table. CORS settings has been set to allow GET and POST requests only from our website.

**Lambda functions*

- **postquestion()**: retrieve posted question from the request body and save it to the questions table
*SAM resource*

![post question.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1625500240234/6p9Hfqcc5.png)

*Function code*

```
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
``` 
- **publishquestion()**: publish the newly posted question from the questions table to SNS topic
*SAM resource*

![publish question.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1625500390776/QjxoixCri.png)

*Function code*

```
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
        print('Couldn't publish message to SNS')
    
``` 
Build your SAM template and test the functions and APIs locally then deploy to AWS (which will create a CloudFormation stack with the resources specified in the template file).
At this stage, we have successfully created the microservice needed to allow users to post questions. We only need to update the frontend html files by adding the questions HTTP API url.

Microservices 3 and 4 coming soon...
 
