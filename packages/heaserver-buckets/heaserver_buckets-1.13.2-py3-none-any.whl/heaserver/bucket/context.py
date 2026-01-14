from heaserver.service.db.aws import AWSPermissionContext
from heaserver.service.db.awsaction import S3_LIST_BUCKET, S3_DELETE_BUCKET, S3_PUT_BUCKET_TAGGING
from heaobject.bucket import AWSDesktopObject, AWSBucket
from aiohttp.web import Request


class S3BucketPermissionsContext(AWSPermissionContext):
    """
    Calculates permissions on a bucket, including attribute-level permissions. The bucket's bucket_id attribute must
    be populated. Read-only buckets need S3_LIST_BUCKET and S3_GET_BUCKET_TAGGING permissions. Read-write buckets
    also need S3_PUT_BUCKET_TAGGING and S3_DELETE_BUCKET permissions.
    """
    def __init__(self, request: Request, **kwargs):
        """
        Creates the context object.

        :param request: the HTTP request (required). It must have a volume_id path parameter.
        :param volume_id: the ID of the volume being accessed (required)
        """
        # S3_GET_BUCKET_TAGGING is needed to read tags; S3_PUT_BUCKET_TAGGING is needed to write tags.
        # S3_GET_BUCKET_TAGGING is a requirement for reading buckets, and the bucket service will raise a 400 error
        # if the user lacks that permission, so don't bother checking for it.
        actions = [S3_LIST_BUCKET, S3_PUT_BUCKET_TAGGING, S3_DELETE_BUCKET]
        super().__init__(request=request, actions=actions, **kwargs)

    def _caller_arn(self, obj: AWSDesktopObject):
        """
        Returns a bucket's ARN. Requires the bucket's bucket_id attribute to be populated.
        """
        return f'arn:aws:s3:{obj.region if isinstance(obj, AWSBucket) and obj.region else ""}::{obj.resource_type_and_id}'
