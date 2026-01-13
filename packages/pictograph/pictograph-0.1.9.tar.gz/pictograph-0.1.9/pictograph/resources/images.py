"""
Image operations
"""

import os
import logging
from typing import Dict, Any, Optional
import requests
from PIL import Image

logger = logging.getLogger(__name__)


class Images:
    """
    Image operations for the Pictograph API.
    """

    def __init__(self, http_client):
        self.http = http_client

    def get(self, image_id: str, include_annotations: bool = False) -> Dict[str, Any]:
        """
        Get image metadata, optionally with annotations.

        Args:
            image_id: UUID of the image
            include_annotations: Include annotations in response (default: False)

        Returns:
            Image metadata dict, with optional 'annotations' key if include_annotations=True

        Example:
            >>> image = client.images.get("image-uuid-123")
            >>> print(image['filename'], image['annotation_count'])
            >>> print(image['image_width'], image['image_height'])

            >>> # Get metadata with annotations
            >>> result = client.images.get("image-uuid-123", include_annotations=True)
            >>> print(result['image']['filename'])
            >>> for ann in result.get('annotations', []):
            ...     print(ann['class'], ann['type'])
        """
        params = {}
        if include_annotations:
            params["include_annotations"] = "true"
        response = self.http.get(f"/api/v1/developer/images/{image_id}/metadata", params=params)
        if include_annotations:
            return response  # Return full response with 'image' and 'annotations' keys
        return response.get("image")

    def download(self, image_id: str, output_path: str) -> str:
        """
        Download image file to local disk.

        Args:
            image_id: UUID of the image
            output_path: Local path to save the image file

        Returns:
            The output path where the image was saved

        Example:
            >>> path = client.images.download("image-uuid-123", "./downloaded_image.jpg")
            >>> print(f"Image saved to: {path}")
        """
        # Use the raw HTTP client method to get binary data
        url = f"{self.http.base_url}/api/v1/developer/images/{image_id}"
        response = requests.get(
            url,
            headers={"X-API-Key": self.http.api_key},
            timeout=300
        )
        response.raise_for_status()

        # Write to file
        with open(output_path, 'wb') as f:
            f.write(response.content)

        logger.info(f"Downloaded image to {output_path}")
        return output_path

    def upload(
        self,
        dataset_id: str,
        file_path: str,
        folder_path: str = "/",
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload an image to a dataset.

        Args:
            dataset_id: UUID of the dataset
            file_path: Local path to the image file
            folder_path: Virtual folder path in dataset (default: "/")
            filename: Custom filename (default: use file_path basename)

        Returns:
            Uploaded image metadata

        Example:
            >>> result = client.images.upload(
            ...     "dataset-uuid",
            ...     "/path/to/image.jpg"
            ... )
            >>> print(result['image_id'])

            >>> # Upload to subfolder
            >>> result = client.images.upload(
            ...     "dataset-uuid",
            ...     "image.jpg",
            ...     folder_path="/train/images"
            ... )
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Get filename
        if not filename:
            filename = os.path.basename(file_path)

        # Detect content type
        ext = os.path.splitext(filename)[1].lower()
        content_type_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
            ".webp": "image/webp"
        }
        content_type = content_type_map.get(ext, "image/jpeg")

        # Get file size
        file_size = os.path.getsize(file_path)

        # Get image dimensions
        try:
            with Image.open(file_path) as img:
                width, height = img.size
        except:
            width, height = None, None

        # Step 1: Get upload URL
        logger.info(f"Getting upload URL for {filename}...")
        upload_url_response = self.http.post(
            "/api/v1/developer/images/upload-url",
            json={
                "dataset_id": dataset_id,
                "filename": filename,
                "folder_path": folder_path,
                "content_type": content_type
            }
        )

        upload_url = upload_url_response["upload_url"]
        gcs_bucket = upload_url_response["gcs_bucket"]
        gcs_path = upload_url_response["gcs_path"]
        gcs_uri = upload_url_response["gcs_uri"]

        # Step 2: Upload to GCS
        logger.info(f"Uploading {filename} to GCS...")
        with open(file_path, 'rb') as f:
            upload_response = requests.put(
                upload_url,
                data=f,
                headers={"Content-Type": content_type},
                timeout=300
            )

        if upload_response.status_code not in [200, 201]:
            raise Exception(f"Upload failed: {upload_response.text}")

        # Step 3: Register image in database
        logger.info(f"Registering {filename}...")
        register_response = self.http.post(
            "/api/v1/developer/images/register",
            data={
                "dataset_id": dataset_id,
                "filename": filename,
                "gcs_bucket": gcs_bucket,
                "gcs_path": gcs_path,
                "gcs_uri": gcs_uri,
                "folder_path": folder_path,
                "file_size": file_size,
                "mime_type": content_type,
                "image_width": width,
                "image_height": height
            }
        )

        logger.info(f"Successfully uploaded {filename}")
        return register_response

    def delete(self, image_id: str, permanent: bool = False) -> Dict[str, Any]:
        """
        Delete (archive) an image.

        Args:
            image_id: UUID of the image
            permanent: Permanently delete from GCS (default: False, archives only)

        Returns:
            Success message

        Example:
            >>> # Archive image (soft delete)
            >>> client.images.delete("image-uuid")

            >>> # Permanently delete
            >>> client.images.delete("image-uuid", permanent=True)
        """
        params = {"permanent": permanent}
        response = self.http.delete(f"/api/v1/developer/images/{image_id}", params=params)
        return response
