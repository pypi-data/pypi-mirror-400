"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

import tarfile
import os
import json
import base64
import click

from qalita.internal.logger import init_logging

logger = init_logging()


def safe_path_join(base_dir: str, *paths: str) -> str:
    """Safely join paths preventing directory traversal attacks.
    
    Args:
        base_dir: The base directory that paths must stay within.
        *paths: Path components to join to the base directory.
        
    Returns:
        The absolute path resulting from joining the paths.
        
    Raises:
        ValueError: If the resulting path would escape the base directory.
    """
    # Validate base_dir
    if not isinstance(base_dir, str):
        raise ValueError("Base directory must be a string")
    if "\x00" in base_dir:
        raise ValueError("Base directory contains null bytes")
    
    # Validate path components
    for p in paths:
        if not isinstance(p, str):
            raise ValueError("Path component must be a string")
        if "\x00" in p:
            raise ValueError("Path component contains null bytes")
        # Reject absolute paths in components
        if os.path.isabs(p):
            raise ValueError(f"Path component must be relative: {p}")
    
    base = os.path.realpath(os.path.abspath(base_dir))
    full_path = os.path.realpath(os.path.abspath(os.path.join(base, *paths)))
    
    # Ensure the resulting path is within the base directory
    if not full_path.startswith(base + os.sep) and full_path != base:
        raise ValueError(f"Path traversal detected: attempted to access {full_path} outside of {base}")
    return full_path


def validate_directory_path(path: str) -> str:  # lgtm[py/path-injection]
    """Validate and normalize a directory path for safe operations.
    
    This function performs security checks to ensure the path is safe to use
    for file system operations. It validates the path exists and is a directory.
    
    Security: This function acts as a sanitizer for path injection attacks by:
    - Rejecting null bytes and control characters
    - Rejecting paths with traversal sequences after normalization
    - Resolving to absolute canonical path (resolves symlinks)
    - Verifying the path exists and is a directory
    
    Args:
        path: The directory path to validate.
        
    Returns:
        The normalized absolute path.
        
    Raises:
        ValueError: If the path is invalid or contains dangerous patterns.
        FileNotFoundError: If the directory does not exist.
    """
    if not isinstance(path, str):
        raise ValueError("Path must be a string")
    if not path or not path.strip():
        raise ValueError("Path cannot be empty")
    if "\x00" in path:
        raise ValueError("Path contains null bytes")
    if any(ord(c) < 32 for c in path if c not in ('\t', '\n', '\r')):
        raise ValueError("Path contains invalid control characters")
    
    # Strip whitespace from input
    clean_path = path.strip()
    
    # Normalize path components (resolve .., ., etc.)
    normalized = os.path.normpath(clean_path)
    
    # Security check: reject paths that still contain traversal sequences after normalization
    # This explicit check helps static analyzers recognize this as a sanitizer
    if ".." in normalized.split(os.sep):
        raise ValueError("Path contains directory traversal sequences")
    
    # Get canonical absolute path (resolves symlinks)
    # Security note: This is an intentional path sanitizer for CLI operations.
    # The function validates user-provided paths with multiple security checks above.
    abs_path = os.path.realpath(os.path.abspath(normalized))  # nosec B108  # lgtm[py/path-injection]
    
    # Verify the resolved path is not empty
    if not abs_path:
        raise ValueError("Path resolves to empty string")
    
    # Security: abs_path has been sanitized above through normalization and realpath
    if not os.path.exists(abs_path):  # nosec B108  # lgtm[py/path-injection]
        raise FileNotFoundError(f"Directory does not exist: {abs_path}")
    if not os.path.isdir(abs_path):  # nosec B108  # lgtm[py/path-injection]
        raise ValueError(f"Path is not a directory: {abs_path}")
    
    return abs_path


def validate_file_path(path: str) -> str:  # lgtm[py/path-injection]
    """Validate and normalize a file path for safe operations.
    
    This function performs security checks to ensure the path is safe to use
    for file system operations. It validates the path exists and is a file.
    
    Security: This function acts as a sanitizer for path injection attacks by:
    - Rejecting null bytes and control characters
    - Rejecting paths with traversal sequences after normalization
    - Resolving to absolute canonical path (resolves symlinks)
    - Verifying the path exists and is a file
    
    Args:
        path: The file path to validate.
        
    Returns:
        The normalized absolute path.
        
    Raises:
        ValueError: If the path is invalid or contains dangerous patterns.
        FileNotFoundError: If the file does not exist.
    """
    if not isinstance(path, str):
        raise ValueError("Path must be a string")
    if not path or not path.strip():
        raise ValueError("Path cannot be empty")
    if "\x00" in path:
        raise ValueError("Path contains null bytes")
    if any(ord(c) < 32 for c in path if c not in ('\t', '\n', '\r')):
        raise ValueError("Path contains invalid control characters")
    
    # Strip whitespace from input
    clean_path = path.strip()
    
    # Normalize path components (resolve .., ., etc.)
    normalized = os.path.normpath(clean_path)
    
    # Security check: reject paths that still contain traversal sequences after normalization
    # This explicit check helps static analyzers recognize this as a sanitizer
    if ".." in normalized.split(os.sep):
        raise ValueError("Path contains directory traversal sequences")
    
    # Get canonical absolute path (resolves symlinks)
    # Security note: This is an intentional path sanitizer for CLI operations.
    # The function validates user-provided paths with multiple security checks above.
    abs_path = os.path.realpath(os.path.abspath(normalized))  # nosec B108  # lgtm[py/path-injection]
    
    # Verify the resolved path is not empty
    if not abs_path:
        raise ValueError("Path resolves to empty string")
    
    # Security: abs_path has been sanitized above through normalization and realpath
    if not os.path.exists(abs_path):  # nosec B108  # lgtm[py/path-injection]
        raise FileNotFoundError(f"File does not exist: {abs_path}")
    if not os.path.isfile(abs_path):  # nosec B108  # lgtm[py/path-injection]
        raise ValueError(f"Path is not a file: {abs_path}")
    
    return abs_path


def safe_path_check(path: str) -> str:  # lgtm[py/path-injection]
    """Validate and normalize a path, preventing path injection attacks.
    
    Security: This function acts as a sanitizer for path injection attacks by:
    - Rejecting null bytes and control characters  
    - Rejecting paths with traversal sequences after normalization
    - Normalizing path components (resolve .., ., etc.)
    - Resolving to canonical absolute path
    
    Args:
        path: The path to validate.
        
    Returns:
        The normalized absolute path.
        
    Raises:
        ValueError: If the path contains dangerous patterns.
    """
    if not isinstance(path, str):
        raise ValueError("Path must be a string")
    
    # Reject null bytes which can be used for path injection
    if "\x00" in path:
        raise ValueError("Path contains null bytes")
    
    # Reject other control characters
    if any(ord(c) < 32 for c in path if c not in ('\t', '\n', '\r')):
        raise ValueError("Path contains invalid control characters")
    
    # Strip whitespace
    clean_path = path.strip() if path else path
    
    # Normalize the path to resolve any .. or . components
    normalized = os.path.normpath(clean_path)
    
    # Security check: reject paths that still contain traversal sequences after normalization
    # This explicit check helps static analyzers recognize this as a sanitizer
    if ".." in normalized.split(os.sep):
        raise ValueError("Path contains directory traversal sequences")
    
    # Get the real absolute path (resolves symlinks)
    # Security note: This is an intentional path sanitizer for CLI operations.
    # The function validates user-provided paths with multiple security checks above.
    abs_path = os.path.realpath(os.path.abspath(normalized))  # nosec B108  # lgtm[py/path-injection]
    
    # Additional check: ensure the resolved path is not empty
    if not abs_path:
        raise ValueError("Path resolves to empty string")
    
    return abs_path


def get_version():
    return "2.6.3"


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def ask_confirmation(message):
    """This function just asks for confirmation interactively from the user"""
    return click.confirm(message, default=False)


def validate_token(token: str):
    try:
        # Step 1: Split the token
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid token format")

        # Step 2: Decode base64 (adding padding if necessary)
        payload_encoded = parts[1]
        missing_padding = len(payload_encoded) % 4
        if missing_padding:
            payload_encoded += "=" * (4 - missing_padding)

        payload_json = base64.urlsafe_b64decode(payload_encoded).decode("utf-8")

        # Step 3: Parse as JSON
        payload = json.loads(payload_json)

        # Step 4: Extract the user ID
        user_id = payload.get("sub")

        # Step 5: Check if role is "admin" or "dataengineer"
        role = payload.get("role")
        valid_roles = {"admin", "dataengineer"}
        has_valid_role = role in valid_roles

        # Step 6: Check if scopes contain required permissions
        required_scopes = {"agent.get", "pack.create", "source.create"}
        scopes = set(payload.get("scopes", []))
        has_required_scopes = required_scopes.issubset(scopes)

        return {
            "user_id": user_id,
            "role_valid": has_valid_role,
            "scopes_valid": has_required_scopes,
        }

    except Exception as e:
        return {"error": str(e)}


def test_connection(config, type_):
    """Test connectivity for a given source type. Returns True if OK, False otherwise."""
    try:
        if type_ in ["mysql"]:
            import pymysql
            conn = pymysql.connect(
                host=config["host"],
                port=int(config["port"]),
                user=config["username"],
                password=config["password"],
                database=config["database"],
                connect_timeout=5
            )
            conn.close()
        elif type_ in ["postgresql"]:
            import psycopg2
            conn = psycopg2.connect(
                host=config["host"],
                port=int(config["port"]),
                user=config["username"],
                password=config["password"],
                dbname=config["database"],
                connect_timeout=5
            )
            conn.close()
        elif type_ == "sqlite":
            import sqlite3
            conn = sqlite3.connect(config["file_path"], timeout=5)
            conn.close()
        elif type_ == "mongodb":
            from pymongo import MongoClient
            uri = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
            client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            client.server_info()
        elif type_ == "s3":
            import boto3
            s3 = boto3.client(
                's3',
                aws_access_key_id=config["access_key"],
                aws_secret_access_key=config["secret_key"],
                region_name=config["region"]
            )
            s3.head_bucket(Bucket=config["bucket"])
        elif type_ == "gcs":
            from google.cloud import storage
            client = storage.Client.from_service_account_json(config["credentials_json"])
            bucket = client.get_bucket(config["bucket"])
            # Optionally check prefix exists
        elif type_ == "azure_blob":
            from azure.storage.blob import BlobServiceClient
            blob_service_client = BlobServiceClient.from_connection_string(config["connection_string"])
            container_client = blob_service_client.get_container_client(config["container"])
            container_client.get_container_properties()
        elif type_ == "hdfs":
            from hdfs import InsecureClient
            url = f"http://{config['namenode_host']}:{config['port']}"
            client = InsecureClient(url, user=config["user"])
            client.status(config["path"], strict=False)
        elif type_ == "folder":
            # Security: validate_directory_path sanitizes the path before use
            folder_path = validate_directory_path(config["path"])  # lgtm[py/path-injection]
            if not os.access(folder_path, os.R_OK):  # nosec B108  # lgtm[py/path-injection]
                raise Exception(f"No read access to folder {folder_path}")
        elif type_ == "oracle":
            # Use python-oracledb in thin mode (no Instant Client required)
            import oracledb
            conn = oracledb.connect(
                user=config["username"],
                password=config["password"],
                host=config["host"],
                port=int(config["port"]),
                service_name=config["database"],
            )
            conn.close()
        # FTP support removed for security reasons
        elif type_ == "file":
            # Security: validate_file_path sanitizes the path before use
            file_path = validate_file_path(config["path"])  # lgtm[py/path-injection]
            if not os.access(file_path, os.R_OK):  # nosec B108  # lgtm[py/path-injection]
                raise Exception(f"No read access to file {file_path}")
        else:
            logger.warning(f"Connection test not implemented for type {type_}")
            return None
        return True
    except Exception as e:
        logger.error(f"Connection test failed for type {type_}: {e}")
        return False
