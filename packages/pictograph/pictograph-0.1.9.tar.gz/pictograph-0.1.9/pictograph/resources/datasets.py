"""
Dataset operations
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from tqdm import tqdm

logger = logging.getLogger(__name__)


class Datasets:
    """
    Dataset operations for the Pictograph API.

    Datasets are projects containing images and annotations.
    """

    def __init__(self, http_client):
        self.http = http_client

    def list(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List all datasets in the organization.

        Args:
            limit: Maximum number of datasets to return (default: 100, max: 1000)

        Returns:
            List of dataset objects

        Example:
            >>> datasets = client.datasets.list()
            >>> for dataset in datasets:
            ...     print(dataset['name'], dataset['image_count'])
        """
        response = self.http.get(
            "/api/v1/developer/datasets/",
            params={"limit": limit}
        )
        return response.get("datasets", [])

    def get(
        self,
        dataset_id: str,
        images_limit: int = 1000
    ) -> Dict[str, Any]:
        """
        Get detailed information about a dataset including images.

        Args:
            dataset_id: UUID of the dataset
            images_limit: Maximum number of images to include (default: 1000)

        Returns:
            Dataset object with images list

        Example:
            >>> dataset = client.datasets.get("dataset-uuid-123")
            >>> print(dataset['name'], dataset['completed_image_count'])
            >>> for img in dataset['images']:
            ...     print(img['filename'], img['image_url'])
        """
        params = {
            "images_limit": images_limit
        }
        response = self.http.get(f"/api/v1/developer/datasets/{dataset_id}", params=params)
        return response.get("dataset")

    def download(
        self,
        dataset_name: str,
        output_dir: Optional[str] = None,
        mode: str = "full",
        status_filter: Optional[str] = None,
        max_workers: int = 10,
        show_progress: bool = True
    ) -> Dict[str, Any]:
        """
        Download a complete dataset with parallel downloads.

        Args:
            dataset_name: Name of the dataset (unique within organization)
            output_dir: Local directory to save files (default: ~/.pictograph/datasets/{dataset_name})
            mode: Download mode - 'full', 'images_only', or 'annotations_only'
            status_filter: Only download images with this status
            max_workers: Number of parallel download threads (default: 10)
            show_progress: Show progress bar (default: True)

        Returns:
            Summary dict with download statistics

        Example:
            >>> # Download everything to default location
            >>> result = client.datasets.download("my-dataset")
            >>> print(f"Downloaded {result['images_downloaded']} images")

            >>> # Download to custom directory
            >>> result = client.datasets.download(
            ...     "my-dataset",
            ...     output_dir="./my_dataset",
            ...     mode="full",
            ...     max_workers=20
            ... )

            >>> # Download only annotations
            >>> result = client.datasets.download(
            ...     "my-dataset",
            ...     output_dir="./annotations",
            ...     mode="annotations_only"
            ... )
        """
        # Validate mode
        if mode not in ["full", "images_only", "annotations_only"]:
            raise ValueError("mode must be 'full', 'images_only', or 'annotations_only'")

        # Compute default output directory if not specified
        if output_dir is None:
            output_dir = f"~/.pictograph/datasets/{dataset_name}"

        # Expand ~ in path and create output directory
        output_dir = os.path.expanduser(output_dir)
        os.makedirs(output_dir, exist_ok=True)

        # Get download URLs using by-name endpoint
        logger.info(f"Fetching download URLs for dataset '{dataset_name}'...")
        params = {"mode": mode, "limit": 10000}
        if status_filter:
            params["status_filter"] = status_filter

        response = self.http.get(
            f"/api/v1/developer/datasets/by-name/{dataset_name}/download",
            params=params
        )

        items = response.get("items", [])
        dataset_id = response.get("dataset_id", "unknown")
        total_items = len(items)

        if total_items == 0:
            logger.warning("No items to download")
            return {
                "success": True,
                "images_downloaded": 0,
                "annotations_downloaded": 0,
                "errors": []
            }

        # Print informative download message
        print()
        print(f'Downloading Pictograph CE dataset "{dataset_name}" (ID: {dataset_id}) '
              f'({total_items} images) to location: "{output_dir}"')

        logger.info(f"Downloading {total_items} items with {max_workers} workers...")

        # Download files in parallel
        download_results = {
            "images_downloaded": 0,
            "annotations_downloaded": 0,
            "errors": []
        }

        def download_file(url: str, filepath: str, is_api_endpoint: bool = False) -> bool:
            """Download a single file from signed GCS URL or API endpoint"""
            try:
                if is_api_endpoint:
                    # API endpoint - use authenticated request via HTTP client
                    response_data = self.http.get(url)
                    # Write JSON response to file with proper formatting
                    with open(filepath, 'w') as f:
                        json.dump(response_data, f, indent=2)
                else:
                    # Direct GCS URL - stream download
                    response = requests.get(url, timeout=60, stream=True)
                    response.raise_for_status()

                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                return True
            except Exception as e:
                logger.error(f"Failed to download {url}: {e}")
                return False

        # Prepare download tasks
        tasks = []
        for item in items:
            filename = item['filename']

            # Image download (always a signed GCS URL)
            if mode in ["full", "images_only"] and item.get("image_url"):
                image_path = os.path.join(output_dir, filename)
                tasks.append(("image", item["image_url"], image_path, filename, False))

            # Annotation download - API endpoint for processed annotations
            if mode in ["full", "annotations_only"] and item.get("annotation_url"):
                annotation_path = os.path.join(output_dir, f"{filename}.json")
                # Check if it's an API endpoint (starts with /api/)
                is_api = item["annotation_url"].startswith("/api/")
                tasks.append(("annotation", item["annotation_url"], annotation_path, filename, is_api))

        # Execute downloads in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(download_file, url, filepath, is_api): (file_type, filename)
                for file_type, url, filepath, filename, is_api in tasks
            }

            # Progress bar
            if show_progress:
                progress = tqdm(total=len(futures), desc="Downloading", unit="file")

            for future in as_completed(futures):
                file_type, filename = futures[future]
                success = future.result()

                if success:
                    if file_type == "image":
                        download_results["images_downloaded"] += 1
                    else:
                        download_results["annotations_downloaded"] += 1
                else:
                    download_results["errors"].append({
                        "filename": filename,
                        "type": file_type
                    })

                if show_progress:
                    progress.update(1)

            if show_progress:
                progress.close()

        download_results["success"] = len(download_results["errors"]) == 0
        download_results["total_items"] = total_items

        logger.info(
            f"Download complete: {download_results['images_downloaded']} images, "
            f"{download_results['annotations_downloaded']} annotations, "
            f"{len(download_results['errors'])} errors"
        )

        return download_results
