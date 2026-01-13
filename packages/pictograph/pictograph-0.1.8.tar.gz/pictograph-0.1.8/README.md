# Pictograph Python SDK

Official Python SDK for [Pictograph Context Engine](https://pictograph.cloud) - a powerful computer vision annotation platform for creating high-quality training datasets.

## Features

- **Simple, intuitive API** - Get started with just a few lines of code
- **Dataset management** - List, download, and manage annotation datasets
- **Image operations** - Upload images, retrieve metadata, and manage assets
- **Annotation tools** - Get, save, and delete annotations in Pictograph JSON format
- **Batch operations** - Download entire datasets with parallel processing
- **Automatic retries** - Built-in retry logic for transient failures
- **Rate limiting** - Automatic handling of API rate limits
- **Type hints** - Full type annotations for better IDE support

## Installation

```bash
pip install pictograph
```

## Quick Start

```python
from pictograph import Client

# Initialize the client with your API key
client = Client(api_key="pk_live_your_key_here")

# List all datasets
datasets = client.datasets.list()
for dataset in datasets:
    print(f"{dataset['name']}: {dataset['image_count']} images")

# Download a complete dataset
client.datasets.download(
    "dataset-uuid",
    output_dir="./my_dataset",
    mode="full"  # Download images + annotations
)

# Upload an image
result = client.images.upload(
    "dataset-uuid",
    "/path/to/image.jpg",
    folder_path="/train/images"
)
print(f"Uploaded: {result['image_id']}")

# Get annotations for an image
annotations = client.annotations.get("image-uuid")
for ann in annotations:
    print(f"{ann['class']}: {ann['type']}")

# Save annotations
client.annotations.save("image-uuid", [
    {
        "id": "ann-1",
        "class": "person",
        "type": "bbox",
        "bbox": [100, 200, 50, 80],  # [x, y, width, height]
        "confidence": 1.0
    }
])
```

## Authentication

Get your API key from the [Pictograph dashboard](https://pictograph.cloud/settings/api-keys).

```python
from pictograph import Client

client = Client(api_key="pk_live_your_key_here")
```

You can also configure the base URL and timeout:

```python
client = Client(
    api_key="pk_live_your_key_here",
    base_url="https://your-instance.pictograph.cloud",
    timeout=60,
    max_retries=5
)
```

## Usage

### Working with Datasets

#### List Datasets

```python
# List all datasets
datasets = client.datasets.list()

# With pagination
datasets = client.datasets.list(limit=50, offset=0)
```

#### Get Dataset Details

```python
# Get basic info
dataset = client.datasets.get("dataset-uuid")
print(dataset['name'], dataset['image_count'])

# Get with images included
dataset = client.datasets.get(
    "dataset-uuid",
    include_images=True,
    images_limit=1000
)
for img in dataset['images']:
    print(img['filename'], img['image_url'])
```

#### List Images in Dataset

```python
# List all images
images = client.datasets.list_images("dataset-uuid")

# Filter by annotation status
completed_images = client.datasets.list_images(
    "dataset-uuid",
    status="complete",
    limit=500
)
```

#### Download Dataset

```python
# Download everything (images + annotations)
result = client.datasets.download(
    "dataset-uuid",
    output_dir="./dataset",
    mode="full",
    max_workers=20,  # Parallel downloads
    show_progress=True
)
print(f"Downloaded {result['images_downloaded']} images")

# Download only annotations
result = client.datasets.download(
    "dataset-uuid",
    output_dir="./annotations",
    mode="annotations_only"
)

# Download only completed images
result = client.datasets.download(
    "dataset-uuid",
    output_dir="./completed",
    mode="full",
    status_filter="complete"
)
```

### Working with Images

#### Get Image Metadata

```python
image = client.images.get("image-uuid")
print(image['filename'])
print(image['image_url'])  # CDN URL for viewing
print(image['annotation_count'])
```

#### Upload Image

```python
# Simple upload
result = client.images.upload(
    "dataset-uuid",
    "/path/to/image.jpg"
)

# Upload to specific folder
result = client.images.upload(
    "dataset-uuid",
    "/path/to/image.jpg",
    folder_path="/train/images",
    filename="custom_name.jpg"
)

print(result['image_id'])
```

#### Delete Image

```python
# Archive (soft delete)
client.images.delete("image-uuid")

# Permanent delete
client.images.delete("image-uuid", permanent=True)
```

### Working with Annotations

Pictograph uses a JSON format that supports multiple annotation types:
- **bbox** - Bounding boxes `[x, y, width, height]`
- **polygon** - Polygons `[[x1, y1], [x2, y2], ...]`
- **polyline** - Polylines `[[x1, y1], [x2, y2], ...]`
- **keypoint** - Single points `[x, y]`

#### Get Annotations

```python
annotations = client.annotations.get("image-uuid")
for ann in annotations:
    print(ann['id'], ann['class'], ann['type'])
    if ann['type'] == 'bbox':
        x, y, width, height = ann['bbox']
        print(f"  Bbox: ({x}, {y}) - {width}x{height}")
```

#### Save Annotations

```python
# Bounding box
annotations = [
    {
        "id": "ann-1",
        "class": "person",
        "type": "bbox",
        "bbox": [100, 200, 50, 80],
        "confidence": 1.0
    }
]
result = client.annotations.save("image-uuid", annotations)
print(result['new_count'])

# Polygon
annotations = [
    {
        "id": "ann-2",
        "class": "car",
        "type": "polygon",
        "polygon": [[10, 20], [30, 40], [50, 60], [10, 20]],
        "confidence": 1.0
    }
]
client.annotations.save("image-uuid", annotations)

# Multiple annotations
annotations = [
    {"id": "ann-1", "class": "person", "type": "bbox", "bbox": [100, 200, 50, 80]},
    {"id": "ann-2", "class": "car", "type": "polygon", "polygon": [[10,20], [30,40], [50,60], [10,20]]},
    {"id": "ann-3", "class": "road", "type": "polyline", "polyline": [[0,100], [50,100], [100,100]]},
    {"id": "ann-4", "class": "landmark", "type": "keypoint", "keypoint": [150, 200]}
]
client.annotations.save("image-uuid", annotations)
```

#### Helper Methods

```python
# Create properly formatted annotations
bbox = client.annotations.create_bbox(
    "ann-1",
    "person",
    [100, 200, 50, 80],
    confidence=0.95
)

polygon = client.annotations.create_polygon(
    "ann-2",
    "car",
    [[10, 20], [30, 40], [50, 60], [10, 20]]
)

polyline = client.annotations.create_polyline(
    "ann-3",
    "road",
    [[0, 100], [50, 100], [100, 100]]
)

keypoint = client.annotations.create_keypoint(
    "ann-4",
    "landmark",
    [150, 200]
)

# Save them all
client.annotations.save("image-uuid", [bbox, polygon, polyline, keypoint])
```

#### Delete Annotations

```python
# Delete all annotations for an image
result = client.annotations.delete("image-uuid")
print(result['deleted_count'])
```

## Context Manager

Use the client as a context manager to ensure proper cleanup:

```python
with Client(api_key="pk_live_your_key_here") as client:
    datasets = client.datasets.list()
    # Client session automatically closed when done
```

## Error Handling

The SDK raises specific exceptions for different error types:

```python
from pictograph import Client, AuthenticationError, RateLimitError, NotFoundError

client = Client(api_key="pk_live_your_key_here")

try:
    dataset = client.datasets.get("invalid-uuid")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except NotFoundError:
    print("Dataset not found")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Advanced Usage

### Batch Processing

```python
from concurrent.futures import ThreadPoolExecutor

# Upload multiple images in parallel
def upload_image(image_path):
    return client.images.upload("dataset-uuid", image_path)

image_paths = ["img1.jpg", "img2.jpg", "img3.jpg"]
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(upload_image, image_paths))

print(f"Uploaded {len(results)} images")
```

### Custom Metadata

```python
# Add custom metadata to annotations
annotation = client.annotations.create_bbox(
    "ann-1",
    "person",
    [100, 200, 50, 80],
    metadata={
        "annotator": "john@example.com",
        "difficulty": "easy",
        "verified": True
    }
)
client.annotations.save("image-uuid", [annotation])
```

## Rate Limits

The SDK automatically handles rate limits:
- **Free tier**: 1,000 requests/hour
- **Starter tier**: 5,000 requests/hour
- **Pro tier**: 20,000 requests/hour
- **Enterprise tier**: 100,000 requests/hour

If you hit a rate limit, the SDK will automatically wait and retry (if retry time < 2 minutes).

## Requirements

- Python 3.8+
- requests >= 2.31.0
- Pillow >= 10.0.0
- tqdm >= 4.65.0

## Support

- **Documentation**: https://pictograph.cloud/docs
- **Email**: support@pictograph.cloud
- **Issues**: https://github.com/pictograph-labs/pictograph-sdk/issues

## License

MIT License - see LICENSE file for details.
