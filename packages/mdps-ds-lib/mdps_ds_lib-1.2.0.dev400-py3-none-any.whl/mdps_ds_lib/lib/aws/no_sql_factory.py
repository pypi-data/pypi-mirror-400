from mdps_ds_lib.lib.utils.factory_abstract import FactoryAbstract


class NoSqlFactory(FactoryAbstract):
    AWS = 'AWS_DDB'
    MONGO = 'MONGO_DB'

    def get_instance_from_dict(self, env_dict: dict, **kwargs):
        raise NotImplementedError('not a need yet')

    def get_instance_from_env(self, **kwargs):
        raise NotImplementedError('Not Yet')

    def get_instance(self, file_repo, **kwargs):
        fr = file_repo.upper()
        if fr == self.AWS:
            from mdps_ds_lib.lib.aws.no_sql_ddb import NoSqlDdb
            return NoSqlDdb(**kwargs)
        raise ModuleNotFoundError(f'cannot find FileStream class for {fr}')
