import json
import boto3
from boto3.dynamodb.conditions import Key
import time
import os
import requests
from botocore.exceptions import ClientError
from forex_python.converter import CurrencyRates


# Get the exchange rate for the hour
def get_rate(fromCurrency, toCurrency, amount):
    """
    function to get rate from forex_python
   
    Returns
    the exchange rate at the hour
    """
   
    currency = CurrencyRates()
    rate = currency.convert(fromCurrency, toCurrency, amount)
     
    return(rate)


# Add the rate to DynamoDB table
def add_rate(item):
    """
    function to generate exchange rate for table
    
    Returns
    New row with the current rate
    """
    
    ddb_data= json.loads(json.dumps(item), parse_float=Decimal)
    dynamodb = boto3.resource('dynamodb') 
    table = dynamodb.Table(table_name)
    
    response = table.put_item(
            Item={
                'currency':  key,
                'timestamp': int(round(time.time() * 1000)),
                'rate': ddb_data[key]
            }
        )
   
    return response



# To send an email
def send_email():
   
    SENDER = "robinbista22@gmail.com" # must be verified in AWS SES Email
    
    RECIPIENT = "robista7118@gmail.com" # must be verified in AWS SES Email

    AWS_REGION = "us-east-1" # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    
    CHARSET = "UTF-8" # The character encoding for the email.
    
    client = boto3.client('ses',region_name=AWS_REGION)  # Create a new SES resource and specify a region.
  
    SUBJECT = "Desired Increase in Exchange Rate" # The subject line for the email.

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("Hello, \n"
                
                "There is more than 2% increase in exchange rate of USD to NPR, compared to previous hour. It might be suitable time to exchange dollars!"
	
                "Regards,"
                "Robin Bista"
                )
                
    # The HTML body of the email.
    BODY_HTML = """<html>
    <head></head>
    <body>
    <p>
    Hello, 
    </p>

    <p>
    There is more than 2% increase in exchange rate of USD to NPR, compared to previous hour. It might be suitable time to exchange dollars!
    </p>
    
    <p>Regards,</p>
    <p>Robin Bista</p>
    
    </body>
    </html>
                """            


    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,      
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
        
def recent_rate(id):
    """function to see rate form the ddb
    Returns
    
    recent rate from the table
    """
 
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table(table_name)
    response = table.query(
        KeyConditionExpression=Key('rate').eq(id),
        ScanIndexForward= False
    )
    rate = response['rate']
    return rate  
    
def when_insert(record):
    """trigger when the event type is INSERT
   
    Returns
    Volatility and sends email if the rate increased by 2% or more
    """
    newImage = record["dynamodb"]["NewImage"]
    rate   = newImage["rate"]["S"]
    newRate = newImage["rate"]["N"]
    timestamp      = newImage["timestamp"]["N"]
    recentRate = recent_rate(rateNum)
    return check_volatility(recentRate)


def check_volatility(value):
 
    item_value = value[:2]
    currency = item_value[0]['NPR']
    volatile_rate = []
    value = float(rate['rate'])
    volatile_rate.append(value)

    if len(volatile_rate) ==1:
        pass
    else:
        if volatile_rate[0]>volatile_rate[1]:
            increase = volatile_rate[0] - volatile_rate[1]
            increase_percent = int((increase/volatile_rate[1])*100)
            if increase_percent > 2:
                send_email()
        elif volatile_values[0] == volatile_values[1]:
            pass
    

def lambda_handler(event, context):
    # TODO implement
    rate = get_rate("USD","NPR, 1")
    add_rate(rate)
    recentRate = recent_rate("NPR")
    check_volatility(recentRate)