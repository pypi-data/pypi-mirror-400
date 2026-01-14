import os
import json
import boto3
from botocore.exceptions import ClientError
import tornado
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
from ._version import __version__
from climb_jupyter_base.exceptions import AuthenticationError, ValidationError
from climb_jupyter_base.decorators import handle_api_errors
from .validators import validate_s3_uri


PLUGIN_NAME = "climb-jupyter-igv"
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
JUPYTERLAB_S3_ENDPOINT = os.environ.get("JUPYTERLAB_S3_ENDPOINT")


class S3PresignHandler(APIHandler):
    @tornado.web.authenticated
    @handle_api_errors
    def get(self):
        # Validate S3 URI
        bucket_name, key = validate_s3_uri(self.get_query_argument("uri"))

        # Validate credentials
        if not (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and JUPYTERLAB_S3_ENDPOINT):
            raise AuthenticationError(
                "Cannot connect to S3: JupyterLab environment does not have credentials"
            )

        # Retrieve presigned URL
        s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            endpoint_url=JUPYTERLAB_S3_ENDPOINT,
        )
        try:
            presigned_url = s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": bucket_name, "Key": key},
                ExpiresIn=3600,
            )
        except ClientError as e:
            self.log.error(e)
            raise ValidationError(
                f"Failed to generate presigned URL: {e.response['Error']['Code']}"
            )

        # Return the presigned url
        self.finish(json.dumps({"url": presigned_url}))


class VersionHandler(APIHandler):
    @tornado.web.authenticated
    @handle_api_errors
    def get(self):
        # Return the version of the package
        self.finish(json.dumps({"version": __version__}))


def setup_handlers(web_app):
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]

    route_pattern = url_path_join(base_url, PLUGIN_NAME, "s3-presign")
    handlers = [(route_pattern, S3PresignHandler)]
    web_app.add_handlers(host_pattern, handlers)

    route_pattern = url_path_join(base_url, PLUGIN_NAME, "version")
    handlers = [(route_pattern, VersionHandler)]
    web_app.add_handlers(host_pattern, handlers)
