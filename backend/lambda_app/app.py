import json
import os
import boto3

TABLE_NAME = os.environ.get("TABLE_NAME", "VisitorTable")
VISITOR_ID = "visitor_counter"

def get_dynamodb_client():
    return boto3.client("dynamodb", region_name="us-east-1")

def lambda_handler(event, context, client=None):
    if client is None:
        client = get_dynamodb_client()
    return get_visitor_count(TABLE_NAME, client)

def get_visitor_count(table_name, client):
    """increment the visitor count, return it."""
    try:
        response = client.update_item(
            TableName=table_name,
            Key={"id": {"S": VISITOR_ID}},
            UpdateExpression="SET visitor_count = if_not_exists(visitor_count, :start) + :inc",
            ExpressionAttributeValues={
                ":inc": {"N": "1"},
                ":start": {"N": "0"}
            },
            ReturnValues="UPDATED_NEW"
        )

        new_count = int(response["Attributes"]["visitor_count"]["N"])

    except Exception as e:
        print("Error updating visitor count:", e)
        new_count = 0

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Content-Type": "application/json"
        },
        "body": json.dumps({"visitor_count": new_count})
    }
