"""
Export operations
"""

import os
import time
import logging
from typing import Dict, Any, Optional, List
import requests

logger = logging.getLogger(__name__)


class Exports:
    """
    Export operations for the Pictograph API.

    Exports allow you to create downloadable ZIP files containing
    annotations (and optionally images) from a dataset.
    """

    def __init__(self, http_client):
        self.http = http_client

    def create(
        self,
        dataset_name: str,
        name: str,
        format: str = "pictograph",
        include_images: bool = False,
        class_filter: Optional[List[str]] = None,
        status_filter: Optional[str] = None,
        wait: bool = True,
        poll_interval: float = 2.0,
        timeout: float = 300.0
    ) -> Dict[str, Any]:
        """
        Create a new export for a dataset.

        Args:
            dataset_name: Name of the dataset to export
            name: Name for this export
            format: Export format - "pictograph" or "coco" (default: "pictograph")
            include_images: Include original images in the ZIP (default: False)
            class_filter: Only include annotations for these classes
            status_filter: Only include images with this status
            wait: Wait for export to complete (default: True)
            poll_interval: Seconds between status checks when waiting (default: 2.0)
            timeout: Maximum seconds to wait for completion (default: 300.0)

        Returns:
            Export object with status and download info if completed

        Example:
            >>> # Create export and wait for completion
            >>> export = client.exports.create(
            ...     dataset_name="my-dataset",
            ...     name="Training Export v1"
            ... )
            >>> print(export['status'])  # 'completed'

            >>> # Create export with images
            >>> export = client.exports.create(
            ...     dataset_name="my-dataset",
            ...     name="Full Export",
            ...     include_images=True
            ... )

            >>> # Create export without waiting
            >>> export = client.exports.create(
            ...     dataset_name="my-dataset",
            ...     name="Background Export",
            ...     wait=False
            ... )
            >>> # Later, check status:
            >>> export = client.exports.get(export['id'])
        """
        data = {
            "dataset_name": dataset_name,
            "name": name,
            "format": format,
            "include_images": include_images
        }

        if class_filter is not None:
            data["class_filter"] = class_filter

        if status_filter is not None:
            data["status_filter"] = status_filter

        logger.info(f"Creating export '{name}' for dataset '{dataset_name}'...")
        response = self.http.post("/api/v1/developer/exports/", json=data)

        export = response.get("export")

        if not wait:
            logger.info(f"Export {export['id']} started. Poll status to check completion.")
            return export

        # Poll for completion
        export_id = export["id"]
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                logger.warning(f"Export {export_id} timed out after {timeout}s")
                raise TimeoutError(f"Export did not complete within {timeout} seconds")

            time.sleep(poll_interval)

            export = self.get(dataset_name, name)
            status = export["status"]

            if status == "completed":
                logger.info(f"Export '{name}' completed successfully")
                return export
            elif status == "failed":
                error_msg = export.get("error_message", "Unknown error")
                logger.error(f"Export '{name}' failed: {error_msg}")
                raise Exception(f"Export failed: {error_msg}")
            else:
                logger.debug(f"Export '{name}' status: {status}")

    def list(
        self,
        dataset_name: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List exports for the organization.

        Args:
            dataset_name: Filter by dataset name
            status: Filter by status ("pending", "processing", "completed", "failed")
            limit: Maximum exports to return (default: 100)
            offset: Number of exports to skip (default: 0)

        Returns:
            List of export objects

        Example:
            >>> # List all exports
            >>> exports = client.exports.list()
            >>> for exp in exports:
            ...     print(exp['name'], exp['status'])

            >>> # List completed exports for a dataset
            >>> exports = client.exports.list(
            ...     dataset_name="my-dataset",
            ...     status="completed"
            ... )
        """
        params = {"limit": limit, "offset": offset}

        if dataset_name:
            params["dataset_name"] = dataset_name
        if status:
            params["status"] = status

        response = self.http.get("/api/v1/developer/exports/", params=params)
        return response.get("exports", [])

    def get(self, dataset_name: str, export_name: str) -> Dict[str, Any]:
        """
        Get details of an export by dataset and export name.

        Use this to check export status after creating with wait=False.

        Args:
            dataset_name: Name of the dataset
            export_name: Name of the export

        Returns:
            Export object with current status

        Example:
            >>> export = client.exports.get("my-dataset", "my-export")
            >>> if export['status'] == 'completed':
            ...     print(f"Ready! Size: {export['file_size']} bytes")
        """
        response = self.http.get(
            f"/api/v1/developer/exports/{dataset_name}/{export_name}"
        )
        return response.get("export")

    def download(
        self,
        dataset_name: str,
        export_name: str,
        output_path: Optional[str] = None,
        show_progress: bool = True
    ) -> str:
        """
        Download an export ZIP file by dataset and export name.

        Args:
            dataset_name: Name of the dataset
            export_name: Name of the export
            output_path: Local path to save the file (default: ./{export_name}.zip)
            show_progress: Show download progress (default: True)

        Returns:
            Path to the downloaded file

        Example:
            >>> # Download with default name
            >>> path = client.exports.download("my-dataset", "my-export")
            >>> print(f"Downloaded to: {path}")

            >>> # Download to specific path
            >>> path = client.exports.download(
            ...     "my-dataset",
            ...     "my-export",
            ...     output_path="./exports/my_export.zip"
            ... )
        """
        # Get download URL
        response = self.http.get(
            f"/api/v1/developer/exports/{dataset_name}/{export_name}/download"
        )

        download_url = response["download_url"]

        # Determine output path
        if not output_path:
            output_path = f"./{export_name}.zip"

        # Ensure directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        logger.info(f"Downloading export to {output_path}...")

        # Download file
        dl_response = requests.get(download_url, stream=True, timeout=600)
        dl_response.raise_for_status()

        total_size = int(dl_response.headers.get('content-length', 0))
        downloaded = 0

        with open(output_path, 'wb') as f:
            for chunk in dl_response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)

                if show_progress and total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\rDownloading: {percent:.1f}%", end="", flush=True)

        if show_progress and total_size > 0:
            print()  # New line after progress

        logger.info(f"Downloaded {downloaded} bytes to {output_path}")
        return output_path

    def delete(self, dataset_name: str, export_name: str) -> Dict[str, Any]:
        """
        Delete an export by dataset and export name.

        Removes both the database record and the GCS file.
        Requires admin or owner role.

        Args:
            dataset_name: Name of the dataset
            export_name: Name of the export

        Returns:
            Success message

        Example:
            >>> client.exports.delete("my-dataset", "my-export")
            >>> print("Export deleted")
        """
        response = self.http.delete(
            f"/api/v1/developer/exports/{dataset_name}/{export_name}"
        )
        logger.info(f"Deleted export '{export_name}' from dataset '{dataset_name}'")
        return response

    def wait_for_completion(
        self,
        dataset_name: str,
        export_name: str,
        poll_interval: float = 2.0,
        timeout: float = 300.0
    ) -> Dict[str, Any]:
        """
        Wait for an export to complete.

        Useful if you created an export with wait=False and want to
        wait for it later.

        Args:
            dataset_name: Name of the dataset
            export_name: Name of the export
            poll_interval: Seconds between status checks (default: 2.0)
            timeout: Maximum seconds to wait (default: 300.0)

        Returns:
            Completed export object

        Raises:
            TimeoutError: If export doesn't complete within timeout
            Exception: If export fails

        Example:
            >>> export = client.exports.create("my-dataset", "my-export", wait=False)
            >>> # ... do other work ...
            >>> export = client.exports.wait_for_completion("my-dataset", "my-export")
        """
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"Export did not complete within {timeout} seconds")

            export = self.get(dataset_name, export_name)
            status = export["status"]

            if status == "completed":
                logger.info(f"Export '{export_name}' completed")
                return export
            elif status == "failed":
                error_msg = export.get("error_message", "Unknown error")
                raise Exception(f"Export failed: {error_msg}")

            time.sleep(poll_interval)
