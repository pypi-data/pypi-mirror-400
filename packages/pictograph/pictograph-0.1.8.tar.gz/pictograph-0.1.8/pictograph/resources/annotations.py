"""
Annotation operations using Pictograph JSON format
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class Annotations:
    """
    Annotation operations for the Pictograph API.

    Uses Pictograph JSON format for annotations.
    Supported types: bbox, polygon, polyline, keypoint
    """

    def __init__(self, http_client):
        self.http = http_client

    def get(self, image_id: str) -> List[Dict[str, Any]]:
        """
        Get annotations for an image.

        Returns annotations in Pictograph JSON format.

        Args:
            image_id: UUID of the image

        Returns:
            List of annotation objects

        Example:
            >>> annotations = client.annotations.get("image-uuid")
            >>> for ann in annotations:
            ...     print(ann['class'], ann['type'])
            ...     if ann['type'] == 'bbox':
            ...         print(ann['bbox'])  # [x, y, width, height]
        """
        response = self.http.get(f"/api/v1/developer/annotations/{image_id}")
        return response.get("annotations", [])

    def save(
        self,
        image_id: str,
        annotations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Save annotations for an image.

        Annotations must be in Pictograph JSON format.

        Args:
            image_id: UUID of the image
            annotations: List of annotation objects

        Returns:
            Save result with annotation count

        Example:
            >>> # Bounding box
            >>> annotations = [
            ...     {
            ...         "id": "ann-1",
            ...         "class": "person",
            ...         "type": "bbox",
            ...         "bbox": [100, 200, 50, 80],
            ...         "confidence": 1.0
            ...     }
            ... ]
            >>> result = client.annotations.save("image-uuid", annotations)
            >>> print(result['new_count'])

            >>> # Polygon
            >>> annotations = [
            ...     {
            ...         "id": "ann-2",
            ...         "class": "car",
            ...         "type": "polygon",
            ...         "polygon": [[10, 20], [30, 40], [50, 60], [10, 20]],
            ...         "confidence": 1.0
            ...     }
            ... ]
            >>> client.annotations.save("image-uuid", annotations)

            >>> # Multiple annotations
            >>> annotations = [
            ...     {"id": "ann-1", "class": "person", "type": "bbox", "bbox": [100, 200, 50, 80]},
            ...     {"id": "ann-2", "class": "car", "type": "polygon", "polygon": [[10,20], [30,40], [50,60], [10,20]]}
            ... ]
            >>> client.annotations.save("image-uuid", annotations)
        """
        # Validate annotations format
        for i, ann in enumerate(annotations):
            if "id" not in ann:
                raise ValueError(f"Annotation {i} missing 'id' field")
            if "class" not in ann:
                raise ValueError(f"Annotation {i} missing 'class' field")
            if "type" not in ann:
                raise ValueError(f"Annotation {i} missing 'type' field")

            ann_type = ann["type"]
            if ann_type not in ["bbox", "polygon", "polyline", "keypoint"]:
                raise ValueError(
                    f"Annotation {i} has invalid type '{ann_type}'. "
                    f"Must be bbox, polygon, polyline, or keypoint"
                )

            # Validate type-specific fields
            if ann_type == "bbox" and "bbox" not in ann:
                raise ValueError(f"Annotation {i} of type 'bbox' must have 'bbox' field")
            elif ann_type == "polygon" and "polygon" not in ann:
                raise ValueError(f"Annotation {i} of type 'polygon' must have 'polygon' field")
            elif ann_type == "polyline" and "polyline" not in ann:
                raise ValueError(f"Annotation {i} of type 'polyline' must have 'polyline' field")
            elif ann_type == "keypoint" and "keypoint" not in ann:
                raise ValueError(f"Annotation {i} of type 'keypoint' must have 'keypoint' field")

        # Save annotations
        response = self.http.post(
            f"/api/v1/developer/annotations/{image_id}",
            json={
                "image_id": image_id,
                "annotations": annotations
            }
        )

        return response

    def delete(self, image_id: str) -> Dict[str, Any]:
        """
        Delete all annotations for an image.

        Args:
            image_id: UUID of the image

        Returns:
            Deletion result

        Example:
            >>> result = client.annotations.delete("image-uuid")
            >>> print(result['deleted_count'])
        """
        response = self.http.delete(f"/api/v1/developer/annotations/{image_id}")
        return response

    def create_bbox(
        self,
        ann_id: str,
        class_name: str,
        bbox: List[float],
        confidence: float = 1.0,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Helper to create a bounding box annotation.

        Args:
            ann_id: Unique annotation ID
            class_name: Class label
            bbox: Bounding box [x, y, width, height]
            confidence: Confidence score (default: 1.0)
            metadata: Optional metadata dict

        Returns:
            Annotation dict in Pictograph format

        Example:
            >>> ann = client.annotations.create_bbox(
            ...     "ann-1",
            ...     "person",
            ...     [100, 200, 50, 80]
            ... )
        """
        return {
            "id": ann_id,
            "class": class_name,
            "type": "bbox",
            "bbox": bbox,
            "confidence": confidence,
            "metadata": metadata
        }

    def create_polygon(
        self,
        ann_id: str,
        class_name: str,
        polygon: List[List[float]],
        confidence: float = 1.0,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Helper to create a polygon annotation.

        Args:
            ann_id: Unique annotation ID
            class_name: Class label
            polygon: List of [x, y] points forming polygon
            confidence: Confidence score (default: 1.0)
            metadata: Optional metadata dict

        Returns:
            Annotation dict in Pictograph format

        Example:
            >>> ann = client.annotations.create_polygon(
            ...     "ann-2",
            ...     "car",
            ...     [[10, 20], [30, 40], [50, 60], [10, 20]]
            ... )
        """
        return {
            "id": ann_id,
            "class": class_name,
            "type": "polygon",
            "polygon": polygon,
            "confidence": confidence,
            "metadata": metadata
        }

    def create_polyline(
        self,
        ann_id: str,
        class_name: str,
        polyline: List[List[float]],
        confidence: float = 1.0,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Helper to create a polyline annotation.

        Args:
            ann_id: Unique annotation ID
            class_name: Class label
            polyline: List of [x, y] points forming polyline
            confidence: Confidence score (default: 1.0)
            metadata: Optional metadata dict

        Returns:
            Annotation dict in Pictograph format

        Example:
            >>> ann = client.annotations.create_polyline(
            ...     "ann-3",
            ...     "road",
            ...     [[0, 100], [50, 100], [100, 100]]
            ... )
        """
        return {
            "id": ann_id,
            "class": class_name,
            "type": "polyline",
            "polyline": polyline,
            "confidence": confidence,
            "metadata": metadata
        }

    def create_keypoint(
        self,
        ann_id: str,
        class_name: str,
        keypoint: List[float],
        confidence: float = 1.0,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Helper to create a keypoint annotation.

        Args:
            ann_id: Unique annotation ID
            class_name: Class label
            keypoint: [x, y] coordinates
            confidence: Confidence score (default: 1.0)
            metadata: Optional metadata dict

        Returns:
            Annotation dict in Pictograph format

        Example:
            >>> ann = client.annotations.create_keypoint(
            ...     "ann-4",
            ...     "landmark",
            ...     [150, 200]
            ... )
        """
        return {
            "id": ann_id,
            "class": class_name,
            "type": "keypoint",
            "keypoint": keypoint,
            "confidence": confidence,
            "metadata": metadata
        }
