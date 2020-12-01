import boto3
from boto3.dynamodb import table
from boto3.dynamodb.conditions import Key
from boto3 import resource
from botocore.exceptions import ClientError
from pydantic import BaseModel
from ddb import NotFoundException
from collections import namedtuple


def _parse_query(query: dict):
    q = query.items()
    if len(list(q)) > 1:
        raise AttributeError(f"Query {query} must contain only a single key:value pair.")
    for k,v in q:
        d = {'key': k, 'value': v}
        return namedtuple('query', d.keys())(*d.values())


class BotoTable:
    def __init__(self, connection: resource = None, ddb_table: table = None):
        if not connection:
            self.dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

        if not ddb_table:
            current_table = self.dynamodb.Table('Burnlist')

            try:
                exists = current_table.table_status
                self.table: table = current_table
            except ClientError:
                self.table: table = self.create_table()
        else:
            self.table: table = ddb_table

    def create_table(self):

        ddb_table = self.dynamodb.create_table(
            TableName="Burnlist",
            KeySchema=[
                {
                    'AttributeName': 'pk',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'sk',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'pk',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'sk',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'region_id',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'structure_index',
                    'KeySchema': [
                        {
                            'AttributeName': 'region_id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'sk',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL',
                    }
                }
            ]
        )

        return ddb_table

    def put(self, model: BaseModel):
        if not hasattr(model, 'pk'):
            raise AttributeError("Model must contain a pk")

        if not hasattr(model, 'sk'):
            raise AttributeError("Model must contain a sk")

        return self.table.put_item(TableName=self.table.name, Item=model.dict())

    def get(self, pk, sk):
        got = self.table.get_item(Key={'pk': pk, 'sk': sk})
        try:
            return got['Item']
        except KeyError:
            raise NotFoundException("No items found")

    def query_index(self, index, pk_query: dict, sk_query: dict = None):
        pk_query = _parse_query(pk_query)
        print(f"key: {getattr(pk_query, 'key')} value: {getattr(pk_query, 'value')}")
        if not sk_query:
            results = self.table.query(IndexName=index, KeyConditionExpression=Key(getattr(pk_query, 'key'))
                                       .eq(getattr(pk_query, 'value')))
        else:
            sk_query = _parse_query(sk_query)
            print(f"key: {getattr(sk_query, 'key')} value: {getattr(sk_query, 'value')}")
            results = self.table.query(IndexName=index, KeyConditionExpression=Key(getattr(pk_query, 'key'))
                                       .eq(getattr(pk_query, 'value')) & Key(getattr(sk_query, 'key'))
                                       .eq(getattr(sk_query, 'value')))
        print(results)
        return results['Items']

    def query(self, pk_value):
        results = self.table.query(TableName=self.table.name, KeyConditionExpression=Key('pk')
                                   .eq(pk_value))
        print(results)
        return results['Items']
