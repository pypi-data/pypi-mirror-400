"""
This module provides utility functions for the GBIF image downloader application.
It includes functions for hashing images, normalizing and uploading images,
uploading metadata, checking if records exist, validating query parameters,
configuring image settings.
"""

import os
from io import BytesIO
import hashlib
import json
import logging
import pandas as pd
import random

import time
from typing import BinaryIO, Any, List, Dict

from PIL import Image, ImageFile
from anhaltai_commons_minio.bucket_utils import (
    list_paths_in_bucket,
    count_file_endings_in_bucket,
)

from minio import Minio

from anhaltai_commons_minio.io_utils import object_prefix_exists
from anhaltai_commons_minio.helper_utils import normalize_minio_object_name

from anhaltai.gbif_downloader.config import MINIO_CLIENT, BUCKET
from anhaltai.gbif_downloader.crawler.base_crawler import GBIFCrawler


def load_dataframe(path: str) -> pd.DataFrame | None:
    """
    Loads a CSV file into a pandas DataFrame.
    Args:
        path: Path to the CSV file.

    Returns: A pandas DataFrame containing the CSV data.
    Raises: SystemExit if the file cannot be read.
    """
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        logging.error("Error reading CSV file %s: %s", path, e)


def classes_with_missing_objects(
    downloader: Any,
    species_keys: List[int],
    path: str,
    query_params: Dict[str, Any],
) -> Dict[int, int]:
    """
    Prioritizes species based on the number of missing objects in MinIO compared to
    GBIF data.
    Args:
        downloader: An instance of a GBIF data downloader.
        species_keys: A list of species taxon keys to evaluate.
        path: The base path in MinIO where data is stored.
        query_params: A dictionary of query parameters for GBIF API requests.

    Returns: A tuple containing:
        - Total GBIF occurrence count.
        - Total MinIO occurrence count.
        - Average images per occurrence count.
        - Total number of objects in MinIO.
        - A dictionary mapping species keys to their priority based on missing objects.
    """

    all_paths = list_paths_in_bucket(MINIO_CLIENT, BUCKET, prefix=path)
    path_species_map = {
        pth.split("/")[-3]: "/".join(pth.split("/")[:-2]) for pth in all_paths
    }

    gbif_occurrence_count = 0
    minio_occurrence_count = 0
    average_images_per_occurrence_count = 0.0
    all_objects_minio_count = 0
    species_with_missing_object = {}

    for species_key in species_keys:

        params = query_params.copy()
        params["taxonKey"] = species_key

        try:
            crawler = GBIFCrawler(downloader=downloader, query_params=params)
            url = crawler.build_query_url()

        except Exception as e:
            logging.error("Error processing taxon key %s: %s", species_key, e)
            continue

        data = downloader.fetch_data(url)
        if not data:
            logging.warning(f"No data for taxonKey {species_key}")
            continue

        json_count = 0
        png_count = 0
        data_count = 0

        prefix = path_species_map.get(str(species_key))
        if prefix:
            minio_counts = count_file_endings_in_bucket(
                MINIO_CLIENT, BUCKET, prefix=prefix, file_endings=[".json", ".png"]
            )

            json_count = minio_counts[".json"]
            png_count = minio_counts[".png"]
            data_count = data.get("count", 0)

        species_with_missing_object[species_key] = data_count - json_count
        logging.info(
            f"{species_key}: GBIF={data_count} | MinIO={json_count} | Average "
            f"Images/Occurrence={png_count / json_count if json_count > 0 else 0}"
        )

        gbif_occurrence_count += data_count
        minio_occurrence_count += json_count
        average_images_per_occurrence_count += (
            png_count / json_count if json_count > 0.0 else 0.0
        )
        all_objects_minio_count += png_count + json_count
        time.sleep(random.uniform(1.0, 1.5))

    logging.info(f"There are {gbif_occurrence_count} GBIF-Occurrences in total.")
    logging.info(f"There are {minio_occurrence_count} MINIO-Occurrences in total.")
    logging.info(
        f"Average images per occurrence: "
        f"{average_images_per_occurrence_count / len(species_keys)}"
    )
    logging.info(f"Total objects in MinIO: {all_objects_minio_count}")
    logging.info(
        f"Total missing occurrences to download: "
        f"{gbif_occurrence_count - minio_occurrence_count}"
    )

    return species_with_missing_object


def get_image_hash(image_bytes, image_url) -> str | None:
    """
    Computes the SHA-256 hash of an image from its byte content.
    Args:
        image_bytes: BytesIO object containing the image data.
        image_url: URL of the image, used for logging errors.

    Returns:
        The SHA-256 hash of the image, or None if an error occurs.
    """
    try:
        img = Image.open(BytesIO(image_bytes))
        sha256 = hashlib.sha256()
        sha256.update(img.tobytes())
        return sha256.hexdigest()
    except (OSError, ValueError) as e:
        logging.error(
            "[image_url=%s] Error hashing image: %s",
            image_url,
            e,
        )
        return None


def normalize_and_upload_image(
    image_bytes,
    img_path,
):
    """
    Normalizes an image by converting it to RGB format and uploading it to MinIO.
    This function ensures that the image is in a standard format (RGB) and saves it
    as a PNG.
    Args:
        image_bytes: BytesIO object containing the image data.
        img_path: The path where the image will be uploaded in MinIO.
    """

    try:
        with Image.open(BytesIO(image_bytes)) as img:

            if img.mode != "RGB":
                img = img.convert("RGB")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            upload_with_retry(
                object_name=img_path,
                data_bytes=buffer,
                data_length=len(buffer.getvalue()),
                content_type="image/png",
            )

    except (OSError, ValueError) as e:
        logging.error(
            "Error validating/saving normalized image at %s: %s",
            img_path,
            e,
        )


def upload_json(
    record,
    base_dir,
    file_name,
):
    """
    Uploads metadata for a GBIF record to MinIO in JSON format.
    Args:
        record: The GBIF record to be uploaded.
        base_dir: The path in MinIO where the metadata will be stored.
        file_name: The name of the file to which the metadata will be saved (without
        extension).
    """

    metadata_path = os.path.join(base_dir, f"{file_name}.json")

    try:
        json_bytes = json.dumps(record).encode("utf-8")
        byte_stream = BytesIO(json_bytes)

        upload_with_retry(
            object_name=metadata_path,
            data_bytes=byte_stream,
            data_length=len(json_bytes),
            content_type="application/json",
        )

    except (OSError, TypeError, ValueError) as e:
        logging.error(
            "Error saving metadata: %s; error: %s",
            metadata_path,
            e,
        )


def does_record_exists(taxonomy_path, file_name):
    """
    Checks if a record exists in MinIO by looking for a specific file.
    Args:
        taxonomy_path: The path in MinIO where the record is expected to be stored.
        file_name: The name of the file to check (without extension).

    Returns:
        True if the record exists, False otherwise.
        Logs an error if there is an issue checking for the record.
    """
    object_path = os.path.join(taxonomy_path, f"{file_name}.json")

    try:
        exists = object_prefix_exists(MINIO_CLIENT, BUCKET, object_path)
        return exists
    except OSError as e:
        logging.error(
            "Error checking if record exists in: %s; error: %s", object_path, e
        )
        return False


def validate_query_params(params):
    """
    Validates the query parameters for GBIF API requests.
    Args:
        params: A dictionary of query parameters to validate.

    Raises:
        ValueError: If an invalid query parameter is found.
    """
    valid_gbif_params = {
        "mediaType",
        "taxonKey",
        "datasetKey",
        "country",
        "hasCoordinate",
        "year",
        "month",
        "basisOfRecord",
        "recordedBy",
        "institutionCode",
        "collectionCode",
        "limit",
        "offset",
    }

    for key in params:
        if key not in valid_gbif_params:
            logging.error("Invalid GBIF query parameter: %s", key)
            raise ValueError(f"Invalid GBIF query parameter: {key}")


def configure_image_settings():
    """
    Configures the image settings to handle large images and truncated images.
    """
    Image.MAX_IMAGE_PIXELS = None
    ImageFile.LOAD_TRUNCATED_IMAGES = True


def upload_with_retry(
    object_name,
    data_bytes,
    data_length,
    content_type,
    retries=3,
    delay=15,
):  # pylint: disable=too-many-arguments, too-many-positional-arguments
    """
    Uploads an object to MinIO with retry logic in case of failure.
    This function attempts to upload the object multiple times if an OSError occurs.
    It uses a semaphore to limit the number of concurrent uploads.
    Args:
        object_name: The name of the object to be uploaded in MinIO.
        data_bytes: BytesIO object containing the data to be uploaded.
        data_length: The length of the data in bytes.
        content_type: The content type of the data being uploaded.
        retries: The number of retry attempts in case of failure.
        delay: The delay in seconds between retry attempts.

    Raises:
        OSError: If the upload fails after all retry attempts.
    """
    for attempt in range(1, retries + 1):
        try:
            upload_object(
                minio_client=MINIO_CLIENT,
                bucket_name=BUCKET,
                object_name=object_name,
                data_bytes=data_bytes,
                data_length=data_length,
                content_type=content_type,
            )
            return

        except OSError as e:

            if attempt == retries:
                logging.error("Upload failed after %s attempts: %s", retries, e)

                raise

            time.sleep(delay)


def upload_object(
    minio_client: Minio,
    bucket_name: str,
    object_name: str,
    data_bytes: BinaryIO,
    data_length: int = -1,
    content_type: str = "application/octet-stream",
    **kwargs,
):  # pylint: disable=too-many-arguments, too-many-positional-arguments
    """Uploads an object to a MinIO bucket.
    Args:
        minio_client: An instance of the Minio client.
        bucket_name: The name of the bucket to upload the object to.
        object_name: The name of the object in the bucket.
        data_bytes: A binary stream containing the data to upload.
        data_length: The length of the data in bytes. If -1, determined automatically.
        content_type: The MIME type of the object being uploaded.
        **kwargs: Additional keyword arguments to pass to the put_object method.
    """

    object_name = normalize_minio_object_name(object_name)

    minio_client.put_object(
        bucket_name=bucket_name,
        object_name=object_name,
        data=data_bytes,
        length=data_length,
        content_type=content_type,
        **kwargs,
    )
