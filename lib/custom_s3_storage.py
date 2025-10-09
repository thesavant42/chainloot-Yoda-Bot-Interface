# lib/custom_s3_storage.py

import os
from typing import Any, Dict, Union

import boto3  # type: ignore

from chainlit import make_async
from chainlit.data.storage_clients.s3 import S3StorageClient
from chainlit.logger import logger


class FixedS3StorageClient(S3StorageClient):
    """
    Custom S3StorageClient that fixes the close() method issue.
    
    The original S3StorageClient tries to call await self.client.close() but
    boto3 S3 clients don't have an async close() method. This class overrides
    the close() method to handle shutdown properly.
    """

    async def close(self) -> None:
        """
        Properly close the S3 client without trying to await a non-async method.
        
        Boto3 clients are synchronous and don't need explicit async closing.
        The client will be garbage collected when the instance is destroyed.
        """
        try:
            # Boto3 clients don't have an async close() method
            # Just log that we're closing and let Python's garbage collector handle it
            logger.info("FixedS3StorageClient closing - client will be garbage collected")
            
            # If the client has a close method (some versions might), call it synchronously
            if hasattr(self.client, 'close') and callable(getattr(self.client, 'close')):
                # Call the synchronous close method if it exists
                self.client.close()
                logger.info("FixedS3StorageClient - synchronous close() called")
        except Exception as e:
            # Log any errors but don't raise them during shutdown
            logger.warning(f"FixedS3StorageClient close error (non-fatal): {e}")