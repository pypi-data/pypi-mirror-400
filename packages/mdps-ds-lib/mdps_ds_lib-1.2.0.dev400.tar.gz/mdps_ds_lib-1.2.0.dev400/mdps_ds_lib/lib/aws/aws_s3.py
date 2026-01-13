import logging
import os
from io import BytesIO
from typing import Union

from mdps_ds_lib.lib.aws.aws_cred import AwsCred
from mdps_ds_lib.lib.utils.file_utils import FileUtils

LOGGER = logging.getLogger(__name__)


class AwsS3(AwsCred):
    def __init__(self):
        super().__init__()
        self.__valid_s3_schemas = ['s3://', 's3a://', 's3s://']
        self.__s3_client = self.get_client('s3')
        self.__s3_resource = self.get_resource('s3')
        self.__target_bucket = None
        self.__target_key = None

    def __upload_to_s3(self, bucket, prefix, file_path, delete_files=False, add_size=True, other_tags={}, s3_name=None):
        """
        Uploading a file to S3
        :param bucket: string - name of bucket
        :param prefix: string - prefix. don't start and end with `/` to avoid extra unnamed dirs
        :param file_path: string - absolute path of file location
        :param delete_files: boolean - deleting original file. default: False
        :param add_size: boolean - adding the file size as tag. default: True
        :param other_tags: dict - key-value pairs as a dictionary
        :param s3_name: string - name of s3 file if the user wishes to change.
                    using the actual filename if not provided. defaulted to None
        :return: None
        """
        tags = {
            'TagSet': []
        }
        if add_size is True:
            tags['TagSet'].append({
                'Key': 'org_size',
                'Value': str(FileUtils.get_size(file_path))
            })
        for key, val in other_tags.items():
            tags['TagSet'].append({
                'Key': key,
                'Value': str(val)
            })
        if s3_name is None:
            s3_name = os.path.basename(file_path)
        s3_key = '{}/{}'.format(prefix, s3_name)
        self.__s3_client.upload_file(file_path, bucket, s3_key, ExtraArgs={'ServerSideEncryption': 'AES256'})
        if delete_files is True:  # deleting local files
            FileUtils.remove_if_exists(file_path)
        if len(tags['TagSet']) > 0:
            try:
                self.__s3_client.put_object_tagging(Bucket=bucket, Key=s3_key, Tagging=tags)
            except Exception as e:
                LOGGER.exception(f'error while adding tags: {tags} to {bucket}/{s3_key}')
                raise e
        return f's3://{bucket}/{s3_key}'

    def exists(self, base_path: str, relative_path: str):
        try:
            response = self.__s3_client.head_object(Bucket=base_path, Key=relative_path)
        except:
            return False
        return True

    def upload(self, file_path: str, base_path: str, relative_parent_path: str, delete_files: bool,
               s3_name: Union[str, None] = None, obj_tags: dict = {}, overwrite: bool = False):
        s3_url = self.__upload_to_s3(base_path, relative_parent_path, file_path, delete_files, True, obj_tags, s3_name)
        if delete_files is True:  # deleting local files
            FileUtils.remove_if_exists(file_path)
        return s3_url

    def get_s3_stream(self):
        return self.__s3_client.get_object(Bucket=self.__target_bucket, Key=self.__target_key)['Body']

    def get_s3_obj_size(self):
        # get head of the s3 file
        s3_obj_head = self.__s3_client.head_object(
            Bucket=self.__target_bucket,
            Key=self.__target_key,
        )
        # get the object size
        s3_obj_size = int(s3_obj_head['ResponseMetadata']['HTTPHeaders']['content-length'])
        if s3_obj_size is None:  # no object size found. something went wrong.
            return -1
        return s3_obj_size

    def __get_all_s3_files_under(self, bucket, prefix, with_versions=False):
        list_method_name = 'list_object_versions' if with_versions is True else 'list_objects_v2'
        page_key = 'Versions' if with_versions is True else 'Contents'
        paginator = self.__s3_client.get_paginator(list_method_name)
        operation_parameters = {
            'Bucket': bucket,
            'Prefix': prefix
        }
        page_iterator = paginator.paginate(**operation_parameters)
        for eachPage in page_iterator:
            if page_key not in eachPage:
                continue
            for fileObj in eachPage[page_key]:
                yield fileObj

    def get_child_s3_files(self, bucket, prefix, additional_checks=lambda x: True, with_versions=False):
        for fileObj in self.__get_all_s3_files_under(bucket, prefix, with_versions=with_versions):
            if additional_checks(fileObj):
                yield fileObj['Key'], fileObj['Size']

    def set_s3_url(self, s3_url):
        LOGGER.debug(f'setting s3_url: {s3_url}')
        self.__target_bucket, self.__target_key = self.split_s3_url(s3_url)
        LOGGER.debug(f'props: {self.__target_bucket}, {self.__target_key}')
        return self

    def split_s3_url(self, s3_url):
        s3_schema = [k for k in self.__valid_s3_schemas if s3_url.startswith(k)]
        if len(s3_schema) != 1:
            raise ValueError('invalid s3 url: {}'.format(s3_url))

        s3_schema_length = len(s3_schema[0])
        split_index = s3_url[s3_schema_length:].find('/')
        bucket = s3_url[s3_schema_length: split_index + s3_schema_length]
        key = s3_url[(split_index + s3_schema_length + 1):]
        return bucket, key

    def __tag_existing_obj(self, other_tags={}):
        if len(other_tags) == 0:
            return
        tags = {
            'TagSet': []
        }
        for key, val in other_tags.items():
            tags['TagSet'].append({
                'Key': key,
                'Value': str(val)
            })
        self.__s3_client.put_object_tagging(Bucket=self.__target_bucket, Key=self.__target_key, Tagging=tags)
        return

    def add_tags_to_obj(self, other_tags={}):
        """
        retrieve existing tags first and append new tags to them

        :param bucket: string
        :param s3_key: string
        :param other_tags: dict
        :return: bool
        """
        if len(other_tags) == 0:
            return False
        response = self.__s3_client.get_object_tagging(Bucket=self.__target_bucket, Key=self.__target_key)
        if 'TagSet' not in response:
            return False
        all_tags = {k['Key']: k['Value'] for k in response['TagSet']}
        for k, v in other_tags.items():
            all_tags[k] = v
            pass
        self.__tag_existing_obj(all_tags)
        return True

    def download(self, local_dir, file_name=None):

        if not FileUtils.dir_exist(local_dir):
            raise ValueError('missing directory')
        if file_name is None:
            LOGGER.debug(f'setting the downloading filename from target_key: {self.__target_key}')
            file_name = os.path.basename(self.__target_key)
        local_file_path = os.path.join(local_dir, file_name)
        LOGGER.debug(f'downloading to local_file_path: {local_file_path}')
        self.__s3_client.download_file(self.__target_bucket, self.__target_key, local_file_path)
        LOGGER.debug(f'file downloaded')
        return local_file_path

    @property
    def target_bucket(self):
        return self.__target_bucket

    @target_bucket.setter
    def target_bucket(self, val):
        """
        :param val:
        :return: None
        """
        self.__target_bucket = val
        return

    @property
    def target_key(self):
        return self.__target_key

    @target_key.setter
    def target_key(self, val):
        """
        :param val:
        :return: None
        """
        self.__target_key = val
        return

    def get_size(self):
        response = self.__s3_client.head_object(Bucket=self.target_bucket, Key=self.target_key)
        return response['ContentLength']

    def get_stream(self):
        if self.target_bucket is None or self.target_key is None:
            raise ValueError('bucket or key is None. Set them before calling this method')
        return self.__s3_client.get_object(Bucket=self.target_bucket, Key=self.target_key)['Body']

    def upload_bytes(self, content: bytes):
        self.__s3_client.put_object(Bucket=self.target_bucket,
                                    Key=self.target_key,
                                    ContentType='binary/octet-stream',
                                    Body=content,
                                    ServerSideEncryption='AES256')
        return

    def read_small_txt_file(self):
        """
        convenient method to read small text files stored in S3
        :return: text file contents
        """
        bytestream = BytesIO(self.get_stream().read())  # get the bytes stream of zipped file
        return bytestream.read().decode('UTF-8')

    def delete_one(self, version_id: str = None):
        params = {
            'Bucket': self.__target_bucket,
            'Key': self.__target_key,
        }
        # MFA='string',
        # VersionId='string',
        # RequestPayer='requester',
        # BypassGovernanceRetention=True | False,
        # ExpectedBucketOwner='string',
        # IfMatch='string',
        # IfMatchLastModifiedTime=datetime(2015, 1, 1),
        # IfMatchSize=123

        if version_id is not None:
            params['VersionId'] = version_id
        return self.__s3_client.delete_object(**params)

    def delete_multiple(self, s3_urls: list=[], s3_bucket: str='', s3_paths: list=[]):
        if len(s3_urls) < 1 and len(s3_paths) < 1:
            raise ValueError(f'unable to delete empty list of URLs or Paths')
        if len(s3_urls) < 1:
            if s3_bucket == '':
                raise ValueError(f'empty s3 bucket for paths')
        else:
            s3_splits = [self.split_s3_url(k) for k in s3_urls]
            s3_bucket = list(set([k[0] for k in s3_splits]))
            if len(s3_bucket) > 1:
                raise ValueError(f'unable to delete multiple s3 buckets: {s3_bucket}')
            s3_bucket = s3_bucket[0]
            s3_paths = list(set([k[1] for k in s3_splits]))
        s3_paths = [{'Key': k,
                     # 'VersionId': 'string',
                     # 'ETag': 'string',
                     # 'LastModifiedTime': datetime(2015, 1, 1),
                     # 'Size': 123
                     } for k in s3_paths]
        response = self.__s3_client.delete_objects(
            Bucket=s3_bucket,
            Delete={
                'Objects': s3_paths,
                'Quiet': True,  # True | False
            },
            # MFA='string',
            # VersionId='string',
            # RequestPayer='requester',
            # BypassGovernanceRetention=True | False,
            # ExpectedBucketOwner='string',
            # IfMatch='string',
            # IfMatchLastModifiedTime=datetime(2015, 1, 1),
            # IfMatchSize=123
        )
        return response

    def get_tags(self, version_id: str = None) -> Union[dict, None]:
        """
        returning all the tags in a dictionary form

        :param base_path: bucket
        :param relative_path: s3 key
        :return:
        """
        params = {
            'Bucket': self.target_bucket,
            'Key': self.target_key,
        }
        if version_id is not None:
            params['VersionId'] = version_id
        response = self.__s3_client.get_object_tagging(**params)
        if 'TagSet' not in response:
            return None
        return {k['Key']: k['Value'] for k in response['TagSet']}

    def copy_artifact(self, src_base_path: str, src_relative_path: str, dest_base_path: str, dest_relative_path: str,
                      copy_tags: float = True, update_old_metadata_style: bool = True, delete_original: bool = False):
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/head_object.html
        try:
            source_head = self.__s3_client.head_object(Bucket=src_base_path, Key=src_relative_path)
        except Exception as e:
            raise ValueError(f'missing source: {src_base_path} - {src_relative_path}')
        storage_class = self.__s3_client.get_object_attributes(Bucket=src_base_path, Key=src_relative_path,
                                                               ObjectAttributes=['StorageClass'])['StorageClass']
        src_metadata = source_head['Metadata']
        self.target_bucket, self.target_key = src_base_path, src_relative_path
        src_tagging = self.get_tags() if copy_tags else {}
        if update_old_metadata_style:
            for k, v in src_metadata.items():
                src_tagging[k] = v
            src_metadata = {}

        tags = [f'{k}={v}' for k, v in src_tagging.items()]
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/copy.html
        # /Users/wphyo/anaconda3/envs/lsmd_3.11__2/lib/python3.11/site-packages/s3transfer/manager.py#157
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/customizations/s3.html#boto3.s3.transfer.TransferConfig
        copy_source = {'Bucket': src_base_path, 'Key': src_relative_path,}  # 'VersionId': 'string'
        self.__s3_client.copy(copy_source, dest_base_path, dest_relative_path, ExtraArgs={
        })
        self.target_bucket, self.target_key = dest_base_path, dest_relative_path
        self.add_tags_to_obj(src_tagging)
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/copy_object.html
        # self.__s3_client.copy_object(
        #     # ACL='private'|'public-read'|'public-read-write'|'authenticated-read'|'aws-exec-read'|'bucket-owner-read'|'bucket-owner-full-control',
        #     Bucket=dest_base_path,
        #     Key=dest_relative_path,
        #     ServerSideEncryption='AES256',  # 'aws:kms',
        #     CopySource={'Bucket': src_base_path, 'Key': src_relative_path,},  # 'VersionId': 'string'
        #     # CacheControl='string',
        #     # ChecksumAlgorithm='CRC32'|'CRC32C'|'SHA1'|'SHA256',
        #     # ContentDisposition='string',
        #     # ContentEncoding='string',
        #     # ContentLanguage='string',
        #     # ContentType='string',
        #     # CopySourceIfMatch='string',
        #     # CopySourceIfModifiedSince=datetime(2015, 1, 1),
        #     # CopySourceIfNoneMatch='string',
        #     # CopySourceIfUnmodifiedSince=datetime(2015, 1, 1),
        #     # Expires=datetime(2015, 1, 1),
        #     # GrantFullControl='string',
        #     # GrantRead='string',
        #     # GrantReadACP='string',
        #     # GrantWriteACP='string',
        #     Metadata=src_metadata,
        #     MetadataDirective='REPLACE',  # 'COPY'|'REPLACE',
        #     TaggingDirective='REPLACE',  # 'COPY'|'REPLACE',
        #     StorageClass=storage_class,  # 'STANDARD'|'REDUCED_REDUNDANCY'|'STANDARD_IA'|'ONEZONE_IA'|'INTELLIGENT_TIERING'|'GLACIER'|'DEEP_ARCHIVE'|'OUTPOSTS'|'GLACIER_IR'|'SNOW',
        #     Tagging='&'.join(tags),
        #     # WebsiteRedirectLocation='string',
        #     # SSECustomerAlgorithm='string',
        #     # SSECustomerKey='string',
        #     # SSEKMSKeyId='string',
        #     # SSEKMSEncryptionContext='string',
        #     # BucketKeyEnabled=True|False,
        #     # CopySourceSSECustomerAlgorithm='string',
        #     # CopySourceSSECustomerKey='string',
        #     # RequestPayer='requester',
        #     # ObjectLockMode='GOVERNANCE'|'COMPLIANCE',
        #     # ObjectLockRetainUntilDate=datetime(2015, 1, 1),
        #     # ObjectLockLegalHoldStatus='ON'|'OFF',
        #     # ExpectedBucketOwner='string',
        #     # ExpectedSourceBucketOwner='string'
        # )
        if delete_original:
            self.target_bucket, self.__target_key = src_base_path, src_relative_path
            self.delete_one()
        return f's3://{dest_base_path}/{dest_relative_path}'
