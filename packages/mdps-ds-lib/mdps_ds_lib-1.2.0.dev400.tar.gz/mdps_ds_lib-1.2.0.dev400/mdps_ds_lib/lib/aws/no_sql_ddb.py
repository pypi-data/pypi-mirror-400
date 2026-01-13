import json
import logging
from collections import defaultdict
from decimal import Decimal
from typing import Union

from boto3.dynamodb.conditions import Attr
from mdps_ds_lib.lib.aws.aws_cred import AwsCred

from mdps_ds_lib.lib.utils.time_utils import TimeUtils

from mdps_ds_lib.lib.aws.no_sql_abstract import NoSqlAbstract, NoSqlProps

LOGGER = logging.getLogger(__name__)


class NoSqlDdb(NoSqlAbstract):
    update_expression = 'update_expression'
    update_keys = 'update_keys'
    update_values = 'update_values'

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.__props = NoSqlProps().load_from_json(kwargs)
        client_params= {
            'service_name': 'dynamodb',
        }
        aws_creds = AwsCred()
        self.__ddb_resource = aws_creds.get_resource(**client_params)
        self.__ddb_client = aws_creds.get_client(**client_params)

    def __replace_decimals(self, obj):
        """
        Ref:
            https://stackoverflow.com/a/46738251  in the comments
            https://github.com/boto/boto3/issues/369#issuecomment-157205696

        :param obj:
        :return:
        """
        if isinstance(obj, list):
            for i in range(len(obj)):
                obj[i] = self.__replace_decimals(obj[i])
            return obj
        elif isinstance(obj, dict):
            for k in obj.keys():
                obj[k] = self.__replace_decimals(obj[k])
            return obj
        elif isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            else:
                return float(obj)
        else:
            return obj

    def generate_set_stmt(self, updating_obj: dict):
        """
        :param updating_obj: dictionary of key value pairs
        :return:
        """
        expression = []
        keys = {}
        values = {}
        for k, v in updating_obj.items():
            keys[f'#{k}_key'] = k
            values[f':{k}_val'] = v
            expression.append(f'#{k}_key = :{k}_val')
        return {
            self.update_expression: expression,
            self.update_keys: keys,
            self.update_values: values,
        }

    def generate_add_stmt(self, updating_obj: dict):
        expression = []
        keys = {}
        values = {}
        for k, v in updating_obj.items():
            keys[f'#{k}_key'] = k
            values[f':{k}_val'] = v
            expression.append(f'#{k}_key = #{k}_key + :{k}_val')
        return {
            self.update_expression: expression,
            self.update_keys: keys,
            self.update_values: values,
        }

    def has_table(self):
        if self.__props.table is None:
            raise ValueError('missing table')
        try:
            tbl_details = self.__ddb_client.describe_table(TableName=self.__props.table)
            LOGGER.debug(f'table found: {tbl_details}')
            return True
        except Exception as e:
            LOGGER.exception('error while describing DDB table')
        return False

    def create_tbl(self, gsi: list = []):
        if self.__props.table is None:
            raise ValueError('missing table')
        if self.__props.primary_key is None:
            raise ValueError('missing primary_key')
        LOGGER.info('creating a table: {}'.format(self.__props.table))
        attribute_definitions = [
            {
                'AttributeName': self.__props.primary_key,
                'AttributeType': self.__props.primary_key_type
            }
        ]
        key_schema = [
            {
                'AttributeName': self.__props.primary_key,
                'KeyType': 'HASH',  # 'RANGE' if there is secondary key
            }
        ]
        for each in gsi:
            each = {**{'Projection': {'ProjectionType': 'ALL'}}, **each}  # Default to ALL if missing
        if self.__props.secondary_key is not None:
            attribute_definitions.append({
                'AttributeName': self.__props.secondary_key,
                'AttributeType': self.__props.secondary_key_type,
            })
            key_schema.append({
                'AttributeName': self.__props.secondary_key,
                'KeyType': 'RANGE',
            })
        create_tbl_params = {
            'TableName': self.__props.table,
            'AttributeDefinitions': attribute_definitions,
            'KeySchema': key_schema,
            'BillingMode': 'PAY_PER_REQUEST',  # TODO setting it to on-demand. might need to re-visit later
            'SSESpecification': {'Enabled': False}  # TODO had to disable it since it does not support 'AES256' yet.
        }
        if len(gsi) > 0:
            create_tbl_params['GlobalSecondaryIndexes'] = gsi
        create_result = self.__ddb_client.create_table(**create_tbl_params)
        return create_result

    def __actual_query(self, table, key_condition):
        response = table.query(KeyConditionExpression=key_condition)
        all_results = response.get('Items', [])
        # Handle pagination
        while 'LastEvaluatedKey' in response:
            response = table.query(
                KeyConditionExpression=key_condition,
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            all_results.extend(response.get('Items', []))

        return self.__replace_decimals(all_results) if all_results else None

    def get(self, primary_key: object, secondary_key: object, **kwargs):
        """
        Retrieve item(s) from DynamoDB table.

        :param primary_key: The partition key value
        :param secondary_key: The sort key value (can be None to retrieve all items with the partition key)
        :param kwargs: Additional options:
            - secondary_key_operation: 'eq' (default) or 'begins_with' - operation to use with secondary_key
        :return: Single item (dict) when using get_item, or list of items when using query
        """
        LOGGER.info('retrieving item(s) from DDB using the key')
        table = self.__ddb_resource.Table(self.__props.table)
        if self.__props.secondary_key is None:  # table has no secondary key.
            LOGGER.debug('table has no SORT key. Ignoring that part. ')
            query_key = {self.__props.primary_key: primary_key}
            item_result = table.get_item(Key=query_key)
            if 'Item' not in item_result:
                return None
            return self.__replace_decimals(item_result['Item'])

        from boto3.dynamodb.conditions import Key
        key_condition = Key(self.__props.primary_key).eq(primary_key)
        if secondary_key is None:
            LOGGER.debug('request has no SORT key. Ignoring that part. ')
            return self.__actual_query(table, key_condition)

        LOGGER.debug('request has SORT key. Adding that part. ')
        secondary_key_operation = kwargs.get('secondary_key_operation', 'eq')
        if secondary_key_operation == 'begins_with':
            key_condition = key_condition & Key(self.__props.secondary_key).begins_with(secondary_key)
        elif secondary_key_operation == 'eq':
            key_condition = key_condition & Key(self.__props.secondary_key).eq(secondary_key)
        else:
            raise ValueError(
                f"Unsupported secondary_key_operation: {secondary_key_operation}. Use 'eq' or 'begins_with'")
        return self.__actual_query(table, key_condition)

    def delete(self, primary_key: object, secondary_key: object, **kwargs) -> object:
        LOGGER.info('deleting one item from DDB using they key')
        query_key = {self.__props.primary_key: primary_key}
        if secondary_key is not None and self.__props.secondary_key is not None:
            query_key[self.__props.secondary_key] = secondary_key
        item_result = self.__ddb_resource.Table(self.__props.table).delete_item(Key=query_key, ReturnValues='ALL_OLD')
        if 'Attributes' not in item_result:
            LOGGER.warning('cannot retrieved deleted attributes.')
            return None
        return self.__replace_decimals(item_result['Attributes'])

    def add(self, primary_key: object, secondary_key: object, item: dict, replace: bool, **kwargs):
        LOGGER.info('adding one item from DDB using they key')
        expression_attr_names = {
            '#p_key': self.__props.primary_key
        }
        item[self.__props.primary_key] = primary_key
        if secondary_key is not None and self.__props.secondary_key is not None:
            expression_attr_names['#s_key'] = self.__props.secondary_key
            item[self.__props.secondary_key] = secondary_key

        if self.__props.ttl_key is not None and self.__props.ttl_in_second is not None:
            item[self.__props.ttl_key] = (TimeUtils.get_current_unix_milli() // 1000) + self.__props.ttl_in_second

        addition_arguments = {
            'Item': json.loads(json.dumps(item), parse_float=Decimal),
            'ReturnValues': 'ALL_OLD',
        }
        if replace is False:
            if secondary_key is not None and self.__props.secondary_key is not None:
                condition = Attr(self.__props.primary_key).not_exists() & Attr(self.__props.secondary_key).not_exists()
            else:
                condition = Attr(self.__props.primary_key).not_exists()
            addition_arguments['ConditionExpression'] = condition
        try:
            item_result = self.__ddb_resource.Table(self.__props.table).put_item(**addition_arguments)
        except Exception as e1:
            if 'ConditionalCheckFailedException' in str(e1):
                raise RuntimeError(f'Item exists. Unable to overwrite')
            raise e1

        """
        {'ResponseMetadata': {'RequestId': '49876A3IFHPMRFIEUMANGFAO8VVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 08 Mar 2021 17:58:08 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '2', 'connection': 'keep-alive', 'x-amzn-requestid': '49876A3IFHPMRFIEUMANGFAO8VVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '2745614147'}, 'RetryAttempts': 0}}
        """
        # TODO check result
        return

    def __merge_update_stmt(self, updating_item: Union[list, dict]):
        if isinstance(updating_item, dict):  # dictionary means only 1 update statement
            if any([k not in updating_item for k in [self.update_expression, self.update_keys, self.update_values]]):
                raise ValueError('invalid updating_item. Pls use generate_set_stmt or generate_add_stmt to create an item')
            return updating_item
        if not isinstance(updating_item, list):  # unsupported type
            raise TypeError('unsupported type for updating_item. only supported dict or list')
        if len(updating_item) < 1:
            raise ValueError('empty updating_list')
        if len(updating_item) == 1:  # only 1 update statement
            return self.__merge_update_stmt(updating_item[0])
        expression = []
        keys = defaultdict(list)
        values = defaultdict(list)
        for each in updating_item: # 1 or more update statements
            if any([k not in each for k in [self.update_expression, self.update_keys, self.update_values]]):
                raise ValueError('invalid updating_item in updating_list. Pls use generate_set_stmt or generate_add_stmt to create an item')
            expression.extend(each[self.update_expression])
            for k, v in each[self.update_keys].items():
                keys[k].append(v)
            for k, v in each[self.update_values].items():
                values[k].append(v)
        duplicated_keys = [k for k, v in keys.items() if len(v) > 1]
        duplicated_values = [k for k, v in keys.items() if len(v) > 1]
        if len(duplicated_keys) > 0 or len(duplicated_values) > 0:
            raise ValueError(f'attempting to update the same key or value twice. duplicated_keys: {duplicated_keys}. duplicated_values: {duplicated_values}')
        return {
            self.update_expression: expression,
            self.update_keys: {k: v[0] for k, v in keys.items()},
            self.update_values: {k: v[0] for k, v in values.items()},
        }

    def update(self, primary_key: object, secondary_key: object, item: Union[list, dict], **kwargs):
        """


        self._ddb_middleware.update_one_item(
            'SET #size_key = #size_key + :size_val ',
            {'#size_key': 'total_size'},
            {':size_val': -1 * deleted_item['size']},
            self._disk_size, self._disk_size)


        :param primary_key:
        :param secondary_key:
        :param item:
        :param kwargs: {"retrieve_new_val": "<bool>"}
        :return:
        """

        merged_update_stmt = self.__merge_update_stmt(item)
        LOGGER.info('updating one item from DDB using they key')
        query_key = {self.__props.primary_key: primary_key}
        if secondary_key is not None and self.__props.secondary_key is not None:
            query_key[self.__props.secondary_key] = secondary_key
        item_result = self.__ddb_resource.Table(self.__props.table).update_item(
            Key=query_key,
            UpdateExpression=f"SET {','.join(merged_update_stmt[self.update_expression])}",
            ExpressionAttributeNames=merged_update_stmt[self.update_keys],
            ExpressionAttributeValues=json.loads(json.dumps(merged_update_stmt[self.update_values]), parse_float=Decimal),
            ReturnValues='ALL_NEW' if 'retrieve_new_val' in kwargs and kwargs['retrieve_new_val'] is True else 'ALL_OLD'
        )
        if 'Attributes' not in item_result:
            return None
        return self.__replace_decimals(item_result['Attributes'])

    def query_gsi(self, index_name: str, key_condition: object = None, **kwargs):
        """
        Query a Global Secondary Index (GSI).

        :param index_name: The name of the GSI to query
        :param key_condition: boto3.dynamodb.conditions.Key condition (optional). If None, scans entire GSI.
        :param kwargs: Additional options:
            - projection_type: 'ALL_ATTRIBUTES' (default), 'ALL_PROJECTED_ATTRIBUTES', or 'SPECIFIC_ATTRIBUTES'
            - attributes_to_get: list of attribute names (only used with projection_type='SPECIFIC_ATTRIBUTES')
        :return: List of items from the GSI
        """
        LOGGER.info(f'querying GSI: {index_name}')
        table = self.__ddb_resource.Table(self.__props.table)
        projection_type = kwargs.get('projection_type', 'ALL_PROJECTED_ATTRIBUTES')

        query_params = {
            'IndexName': index_name,
        }

        # Set projection
        if projection_type == 'SPECIFIC_ATTRIBUTES' and 'attributes_to_get' in kwargs:
            query_params['ProjectionExpression'] = ','.join(kwargs['attributes_to_get'])
        elif projection_type == 'ALL_PROJECTED_ATTRIBUTES':
            query_params['Select'] = 'ALL_PROJECTED_ATTRIBUTES'
        else:
            query_params['Select'] = 'ALL_ATTRIBUTES'

        # If key_condition is provided, use query operation
        if key_condition is not None:
            query_params['KeyConditionExpression'] = key_condition
            response = table.query(**query_params)
        else:
            # If no key condition, scan the GSI
            response = table.scan(**query_params)

        all_results = response.get('Items', [])

        # Handle pagination
        while 'LastEvaluatedKey' in response:
            query_params['ExclusiveStartKey'] = response['LastEvaluatedKey']
            if key_condition is not None:
                response = table.query(**query_params)
            else:
                response = table.scan(**query_params)
            all_results.extend(response.get('Items', []))

        return self.__replace_decimals(all_results) if all_results else None

    def query(self, conditions: dict, **kwargs):
        """
        TODO: currently it only supports Equal conditions. Other contidions need to be implemented. and refactor mongo_db at the same time.
        :param conditions:
        :param kwargs:
        :return:
        """
        LOGGER.info('scanning items from DDB using the key')
        conditions_dict = {k: {'AttributeValueList': [v], 'ComparisonOperator': 'EQ'} for k, v in conditions.items()}
        current_tbl = self.__ddb_resource.Table(self.__props.table)
        item_result = current_tbl.scan(
            Limit=1,
            ScanFilter=conditions_dict,
            Select='ALL_ATTRIBUTES')
        all_results = item_result['Items']
        while 'LastEvaluatedKey' in item_result and item_result['LastEvaluatedKey'] is not None:  # pagination
            item_result = current_tbl.scan(
                Limit=100,
                ScanFilter=conditions_dict,
                ExclusiveStartKey=item_result['LastEvaluatedKey'],
                Select='ALL_ATTRIBUTES')
            all_results.extend(item_result['Items'])
        return self.__replace_decimals(all_results)
