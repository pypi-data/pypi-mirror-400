from abc import ABC, abstractmethod
from typing import Union


class NoSqlProps:
    def __init__(self):
        self.__host = None
        self.__port = -1
        self.__db_name = None
        self.__table = None
        self.__primary_key = None
        self.__secondary_key = None
        self.__primary_key_type = 'S'  # DDB only
        self.__secondary_key_type = 'S'  # DDB only
        self.__ttl_key = None
        self.__ttl_in_second = None

    @property
    def ttl_key(self):
        return self.__ttl_key

    @ttl_key.setter
    def ttl_key(self, val):
        """
        :param val:
        :return: None
        """
        self.__ttl_key = val
        return

    @property
    def ttl_in_second(self):
        return self.__ttl_in_second

    @ttl_in_second.setter
    def ttl_in_second(self, val):
        """
        :param val:
        :return: None
        """
        self.__ttl_in_second = val
        return

    @property
    def primary_key_type(self):
        return self.__primary_key_type

    @primary_key_type.setter
    def primary_key_type(self, val):
        """
        :param val:
        :return: None
        """
        self.__primary_key_type = val
        return

    @property
    def secondary_key_type(self):
        return self.__secondary_key_type

    @secondary_key_type.setter
    def secondary_key_type(self, val):
        """
        :param val:
        :return: None
        """
        self.__secondary_key_type = val
        return

    @property
    def primary_key(self):
        return self.__primary_key

    @primary_key.setter
    def primary_key(self, val):
        """
        :param val:
        :return: None
        """
        self.__primary_key = val
        return

    @property
    def secondary_key(self):
        return self.__secondary_key

    @secondary_key.setter
    def secondary_key(self, val):
        """
        :param val:
        :return: None
        """
        self.__secondary_key = val
        return

    def to_json(self):
        return {
            'host': self.host,
            'port': self.port,
            'db_name': self.db_name,
            'table': self.table,
            'primary_key': self.primary_key,
            'secondary_key': self.secondary_key,
        }

    def load_from_json(self, input_json: dict):
        if 'host' in input_json:
            self.host = input_json['host']
        if 'port' in input_json:
            self.port = int(input_json['port'])
        if 'db_name' in input_json:
            self.db_name = input_json['db_name']
        if 'table' in input_json:
            self.table = input_json['table']
        if 'primary_key' in input_json:
            self.primary_key = input_json['primary_key']
        if 'secondary_key' in input_json:
            self.secondary_key = input_json['secondary_key']
        return self

    @property
    def host(self):
        return self.__host

    @host.setter
    def host(self, val):
        """
        :param val:
        :return: None
        """
        self.__host = val
        return

    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, val):
        """
        :param val:
        :return: None
        """
        self.__port = val
        return

    @property
    def db_name(self):
        return self.__db_name

    @db_name.setter
    def db_name(self, val):
        """
        :param val:
        :return: None
        """
        self.__db_name = val
        return

    @property
    def table(self):
        return self.__table

    @table.setter
    def table(self, val):
        """
        :param val:
        :return: None
        """
        self.__table = val
        return


class NoSqlAbstract(ABC):

    @abstractmethod
    def __init__(self, **kwargs) -> None:
        super().__init__()

    @abstractmethod
    def generate_set_stmt(self, updating_obj: dict):
        return

    @abstractmethod
    def generate_add_stmt(self, updating_obj: dict):
        return

    @abstractmethod
    def has_table(self):
        return

    @abstractmethod
    def create_tbl(self, gsi: list):
        return

    @abstractmethod
    def get(self, primary_key: object, secondary_key: object, **kwargs):
        return

    @abstractmethod
    def delete(self, primary_key: object, secondary_key: object, **kwargs) -> object:
        return

    @abstractmethod
    def add(self, primary_key: object, secondary_key: object, item: dict, replace:bool, **kwargs):
        return

    @abstractmethod
    def update(self, primary_key: object, secondary_key: object, item: Union[list, dict], **kwargs):
        return

    @abstractmethod
    def query(self, conditions: dict, **kwargs):
        return

    @abstractmethod
    def query_gsi(self, index_name: str, key_condition: object = None, **kwargs):
        return
