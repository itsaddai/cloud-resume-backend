import os
import sys
import json
import boto3
import pytest
from moto import mock_dynamodb


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lambda_app.app import lambda_handler, VISITOR_ID, TABLE_NAME

def create_mock_table(dynamodb_client, table_name):
    dynamodb_client.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )


@mock_dynamodb
def test_visitor_counter_initial_increment():
    """test visitor counter increment"""
    dynamodb = boto3.client("dynamodb", region_name="us-east-1")
    create_mock_table(dynamodb, TABLE_NAME)

    dynamodb.put_item(
        TableName=TABLE_NAME,
        Item={"id": {"S": VISITOR_ID}, "visitor_count": {"N": "0"}}
    )

    os.environ["TABLE_NAME"] = TABLE_NAME

    result = lambda_handler({}, None, client=dynamodb)
    body = json.loads(result["body"])
    assert body["visitor_count"] == 1


@mock_dynamodb
def test_visitor_counter_multiple_increments():
    dynamodb = boto3.client("dynamodb", region_name="us-east-1")
    create_mock_table(dynamodb, TABLE_NAME)

    dynamodb.put_item(
        TableName=TABLE_NAME,
        Item={"id": {"S": VISITOR_ID}, "visitor_count": {"N": "5"}}
    )

    os.environ["TABLE_NAME"] = TABLE_NAME

    for expected_count in range(6, 9):
        result = lambda_handler({}, None, client=dynamodb)
        body = json.loads(result["body"])
        assert body["visitor_count"] == expected_count
