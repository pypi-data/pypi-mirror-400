import fsspec
import os
import tempfile
from typing import Union, BinaryIO, Optional

class DataSourceError(Exception):
    """Custom exception for data source accessibility issues."""
    pass

class UniversalFactory:
    """
    A factory class to create file-like objects from various sources (Local, S3).
    Uses fsspec to handle protocol abstraction and caching.
    """

    @staticmethod
    def open(path: str, mode: str = "rb", **storage_options) -> BinaryIO:
        """
        Opens a file from the given path, handling S3 caching transparently.
        
        Args:
            path (str): The file path (e.g., "C:/data/file.nii" or "s3://bucket/file.nii")
            mode (str): File mode, default "rb".
            **storage_options: Additional arguments for the backend (e.g. aws_access_key_id).

        Returns:
            BinaryIO: A file-like object.
        """
        try:
            if path.startswith("s3://"):
                # Implicit Caching for S3
                # We use 'simplecache' to cache accessed chunks locally.
                # This is critical for header parsing which does many small seeks.
                
                # Construct the chained URL: simplecache::s3://bucket/key
                # Note: 's3://' is stripped by fsspec when using chaining if not careful, 
                # but 'simplecache::s3://' works.
                
                url = f"simplecache::{path}"
                
                # Configure Cache Storage
                cache_dir = os.path.join(tempfile.gettempdir(), 'neuroops_cache')
                
                # Prepare options for the 'target' protocol (s3)
                # fsspec chaining expects target options to be passed directly or in 's3' dict depending on version.
                # Usually: fsspec.open("simplecache::s3://...", s3={...}, cache_storage=...)
                
                # We pass storage_options as the S3 options
                return fsspec.open(
                    url, 
                    mode=mode, 
                    cache_storage=cache_dir,
                    s3=storage_options
                ).open()
                
            else:
                # Local file or other protocols
                return fsspec.open(path, mode=mode, **storage_options).open()

        except Exception as e:
            raise DataSourceError(f"Could not open resource at '{path}'. Check connectivity or permissions. Error: {str(e)}")
