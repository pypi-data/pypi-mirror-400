from copy import deepcopy
from typing import Union

from pymongo import MongoClient
from pymongo.collection import Collection

from mdps_ds_lib.lib.aws.no_sql_abstract import NoSqlAbstract, NoSqlProps


class NoSqlMongoDb(NoSqlAbstract):
    def __init__(self, **kwargs) -> None:
        self.__props = NoSqlProps().load_from_json(kwargs)
        mongo_client = MongoClient(self.__props.host, self.__props.port)
        self.__table: Collection = mongo_client[self.__props.db_name][self.__props.table]

    def generate_set_stmt(self, updating_obj: dict):
        return {'$set': updating_obj}

    def generate_add_stmt(self, updating_obj: dict):
        return {'$inc': updating_obj}

    def has_table(self):
        return True

    def create_tbl(self, gsi: list):
        raise NotImplementedError('not yet')

    def get(self, primary_key: object, secondary_key: object, **kwargs):
        return self.__table.find_one(self.__generate_id(primary_key, secondary_key))

    def __generate_id(self, primary_key, secondary_key):
        unique_dict = {self.__props.primary_key: primary_key}
        if secondary_key is not None:
            unique_dict[self.__props.secondary_key] = secondary_key
        return unique_dict

    def delete(self, primary_key: object, secondary_key: object, **kwargs) -> object:
        unique_dict = self.__generate_id(primary_key, secondary_key)
        deleting_item = self.get(primary_key, secondary_key)
        delete_result = self.__table.delete_many(unique_dict)
        if delete_result.deleted_count > 0:
            return deleting_item
        return None

    def add(self, primary_key: object, secondary_key: object, item: dict, replace: bool, **kwargs):
        adding_item = deepcopy(item)
        unique_dict = self.__generate_id(primary_key, secondary_key)
        adding_item[self.__props.primary_key] = primary_key
        if secondary_key is not None:
            adding_item[self.__props.secondary_key] = secondary_key
        if replace:
            update_result = self.__table.update_one(unique_dict, {'$set': adding_item}, upsert=True)
            return update_result.acknowledged
        insert_result = self.__table.insert_one(adding_item)
        return insert_result.inserted_id

    def update(self, primary_key: object, secondary_key: object, item: Union[list, dict], **kwargs):
        if len(item) < 1:
            return None
        updating_item = deepcopy(item)
        unique_dict = self.__generate_id(primary_key, secondary_key)
        if isinstance(updating_item, list):
            temp = {}
            for each in updating_item:
                for k, v in each.items():
                    temp[k] = v
            # updating_item = updating_item if len(updating_item) > 1 else updating_item[0]
            updating_item = temp
        update_result = self.__table.update_one(unique_dict, updating_item, upsert=False)
        return update_result.acknowledged

    def query(self, conditions: dict, **kwargs):
        result = self.__table.find(conditions)
        return [k for k in result]

    def query_gsi(self, index_name: str, key_condition: object = None, **kwargs):
        raise NotImplementedError('GSI querying is not applicable for MongoDB')
