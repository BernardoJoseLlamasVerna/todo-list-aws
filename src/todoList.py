import os
import boto3
import time
import uuid
import json
import functools
from botocore.exceptions import ClientError

def get_table(dynamodb=None):
    print('##### get_table ####')
    if not dynamodb:
        URL = os.environ['ENDPOINT_OVERRIDE']
        if URL:
            print(
                'URL dynamoDB:'+
                URL
            )
            boto3.client = functools.partial(
                boto3.client,
                endpoint_url=URL
            )
            boto3.resource = functools.partial(
                boto3.resource,
                endpoint_url=URL
            )
        variable_dynamodb = "dynamodb"
        dynamodb = boto3.resource(
            variable_dynamodb
        )
    # fetch todo from the database

    print('#### DYNAMODB_TABLE ####')
    variable_dynamo_table = 'DYNAMODB_TABLE'
    variable_dynamodb_environ = os.environ[variable_dynamo_table]
    table = dynamodb.Table(
        variable_dynamodb_environ
    )
    return table


def get_item(key, dynamodb=None):
    print('#### get_item #####')
    table = get_table(
        dynamodb
    )
    try:
        print('#### result ####')
        result = table.get_item(
            Key={
                'id': key
            }
        )

    except ClientError as e:
        print(
            e.response
            ['Error']
            ['Message']
        )
    else:
        print('####################')
        print(
            'Result getItem:'+str(result)
        )
        print('####################')
        if 'Item' in result:
            return result['Item']


def get_items(dynamodb=None):
    print('##### get_items ####')
    table = get_table(dynamodb)
    # fetch todo from the database
    print('#### result ####')
    result = table.scan()
    return result['Items']


def put_item(text, dynamodb=None):
    print('#### put_item #####')
    table = get_table(dynamodb)
    timestamp = str(time.time())
    print('#### Table name ####')
    print(
        'Table name:' +table.name
    )
    print('#### Table name ####')
    item = {
        'id': str(uuid.uuid1()),
        'text': text,
        'checked': False,
        'createdAt': timestamp,
        'updatedAt': timestamp,
    }
    try:
        # write the todo to the database
        table.put_item(Item=item)
        # create a response
        statusCode = "statusCode"
        status_ok = 200
        body = "body"
        body_value = json.dumps(item)
        print('#### response ####')
        response = {}
        response[statusCode] = status_ok
        response[body] = body_value
        print('#### response ####')

    except ClientError as e:
        # print error message:
        print(
            e.response
            ['Error']
            ['Message']
        )
    else:
        return response


def update_item(key, text, checked, dynamodb=None):
    print('#### update_item ####')
    table = get_table(dynamodb)
    timestamp = int(time.time() * 1000)
    # update the todo in the database
    try:
        result = table.update_item(
            Key={
                'id': key
            },
            ExpressionAttributeNames={
              '#todo_text': 'text',
            },
            ExpressionAttributeValues={
              ':text': text,
              ':checked': checked,
              ':updatedAt': timestamp,
            },
            UpdateExpression='SET #todo_text = :text, '
                             'checked = :checked, '
                             'updatedAt = :updatedAt',
            ReturnValues='ALL_NEW',
        )

    except ClientError as e:
        print(
            e.response
            ['Error']
            ['Message']
        )
    else:
        print('#### result[Attributes] ####')
        return result['Attributes']


def delete_item(key, dynamodb=None):
    print('#### delete_item ####')
    table = get_table(dynamodb)
    # delete the todo from the database
    try:
        table.delete_item(
            Key={
                'id': key
            }
        )

    except ClientError as e:
        # error message
        print(
            e.response
            ['Error']
            ['Message']
        )
    else:
        return


def create_todo_table(dynamodb):
    print('#### create_todo_table ####')
    # For unit testing
    tableName = os.environ['DYNAMODB_TABLE']
    print(
        'Creating Table with name:' +tableName
    )
    table = dynamodb.create_table(
        TableName=tableName,
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )

    # Wait until the table exists.
    print('#### Wait until the table exists ####')
    table\
        .meta\
        .client\
        .get_waiter('table_exists')\
        .wait(TableName=tableName)
    if (table.table_status != 'ACTIVE'):
        raise AssertionError()

    return table
