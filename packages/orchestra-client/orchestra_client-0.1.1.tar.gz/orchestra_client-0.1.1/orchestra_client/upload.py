"""Upload files/directories to a session's MorphCloud instance."""

import os
import sys
import tarfile
import tempfile
from pathlib import Path

import requests
from morphcloud.api import MorphCloudClient

from orchestra_client.lib.config import get_auth_headers
from orchestra_client.lib.logger import get_logger

logger = get_logger(__name__)


def upload(local_path: str, session_name: str | None, server_url: str) -> int:
    """Upload a local file or directory to a session's instance.

    Args:
        local_path: Local file or directory path to upload
        session_name: Target session name (None to use root session)
        server_url: Orchestra backend URL (e.g., http://localhost:8000)

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Validate local path
        local_path = os.path.abspath(local_path)
        if not os.path.exists(local_path):
            logger.error(f"Local path does not exist: {local_path}")
            return 1

        # If no session_name provided, find the root session
        if session_name is None:
            response = requests.get(f"{server_url}/agents", headers=get_auth_headers())
            if response.status_code != 200:
                logger.error(f"Failed to list sessions: {response.status_code}")
                return 1

            sessions = response.json().get("sessions", [])
            root_sessions = [s for s in sessions if s.get("parent_session_name") is None]

            if not root_sessions:
                logger.error("No root session found. Please specify a session_name.")
                return 1
            elif len(root_sessions) > 1:
                logger.error(f"Multiple root sessions found: {[s['session_name'] for s in root_sessions]}. Please specify a session_name.")
                return 1

            session_name = root_sessions[0]["session_name"]
            logger.info(f"Using root session: {session_name}")

        # Get session info from backend API
        response = requests.get(f"{server_url}/agents/{session_name}", headers=get_auth_headers())
        if response.status_code == 404:
            logger.error(f"Session '{session_name}' not found")
            return 1
        elif response.status_code != 200:
            logger.error(f"Failed to get session info: {response.status_code}")
            return 1

        session_data = response.json()
        instance_id = session_data.get("instance_id")

        if not instance_id:
            logger.error(f"Session '{session_name}' has no instance_id")
            return 1

        # Get MorphCloud instance
        morph_client = MorphCloudClient()
        instance = morph_client.instances.get(instance_id)

        # Determine remote path (~/code/<basename>)
        basename = os.path.basename(local_path)
        remote_path = f"~/code/{basename}"

        # Ensure ~/code directory exists on remote
        logger.info(f"Ensuring ~/code directory exists on instance {instance_id}")
        instance.exec("mkdir -p ~/code")

        # Handle directories vs files differently
        if os.path.isdir(local_path):
            logger.info(f"Uploading directory {local_path} to {remote_path}")
            success = upload_directory(instance, local_path, remote_path)
        else:
            logger.info(f"Uploading file {local_path} to {remote_path}")
            instance.upload(local_path, remote_path)
            success = True

        if success:
            logger.info(f"Successfully uploaded {local_path} to {remote_path} on session '{session_name}'")
            return 0
        else:
            logger.error(f"Failed to upload {local_path}")
            return 1

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        return 1


def upload_directory(instance, local_dir: str, remote_path: str) -> bool:
    """Upload a directory by creating a tarball, uploading it, and extracting.

    Args:
        instance: MorphCloud instance object
        local_dir: Local directory path
        remote_path: Remote destination path (e.g., ~/code/myproject)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create temporary tar file
        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp_file:
            tar_path = tmp_file.name

        logger.info(f"Creating tarball of {local_dir}")

        # Create tarball of the directory
        with tarfile.open(tar_path, "w:gz") as tar:
            # Add all contents of the directory, preserving structure
            for root, dirs, files in os.walk(local_dir):
                # Calculate relative path from local_dir
                rel_root = os.path.relpath(root, local_dir)
                if rel_root == ".":
                    rel_root = ""

                for file in files:
                    file_path = os.path.join(root, file)
                    # Archive name should be relative to the directory
                    arcname = os.path.join(rel_root, file) if rel_root else file
                    tar.add(file_path, arcname=arcname)

        # Upload tarball to remote temp location
        remote_tar = "/tmp/upload.tar.gz"
        logger.info(f"Uploading tarball ({os.path.getsize(tar_path)} bytes)")
        instance.upload(tar_path, remote_tar)

        # Extract tarball at destination
        # First ensure parent directory exists
        remote_parent = os.path.dirname(remote_path)
        instance.exec(f"mkdir -p {remote_parent}")

        # Create target directory and extract
        logger.info(f"Extracting tarball to {remote_path}")
        instance.exec(f"mkdir -p {remote_path}")
        instance.exec(f"tar -xzf {remote_tar} -C {remote_path}")

        # Clean up remote tarball
        instance.exec(f"rm {remote_tar}")

        # Clean up local tarball
        os.unlink(tar_path)

        logger.info(f"Directory uploaded and extracted successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to upload directory: {e}")
        # Try to clean up
        try:
            if os.path.exists(tar_path):
                os.unlink(tar_path)
        except:
            pass
        return False
