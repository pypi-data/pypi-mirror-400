"""
Main entry point for the GBIF image downloader application.
This script initializes logging, validates query parameters, configures image settings,
and processes a list of tree species to download images from GBIF if necessary.
"""

import logging

from anhaltai.gbif_downloader.config import (
    LOG_DIR,
    QUERY_PARAMS,
    ALREADY_PREPROCESSED,
    TREE_LIST_INPUT_PATH,
    PROCESSED_TREE_LIST_PATH,
    OUTPUT_PATH,
)

from anhaltai.gbif_downloader.utils import (
    validate_query_params,
    configure_image_settings,
    load_dataframe,
    prioritize_classes_with_most_missing_objects,
)
from anhaltai.gbif_downloader.crawler.base_crawler import GBIFCrawler
from anhaltai.gbif_downloader.local_log_handler import LocalLogHandler
from anhaltai.gbif_downloader.downloader import GBIFImageDownloader
from anhaltai.gbif_downloader.tree_list_processor import TreeListProcessor

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers.clear()

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

local_handler = LocalLogHandler(base_dir=LOG_DIR)
local_handler.setLevel(logging.WARNING)
local_handler.setFormatter(formatter)
logger.addHandler(local_handler)

logger.info("MinIO-Logging started.")

validate_query_params(QUERY_PARAMS)
configure_image_settings()

if not ALREADY_PREPROCESSED:
    processor = TreeListProcessor(
        input_path=TREE_LIST_INPUT_PATH,
        sheet_name="Gehölzarten",
        taxon="speciesKey",
    )
    processor.process_tree_list(PROCESSED_TREE_LIST_PATH)

df = load_dataframe(PROCESSED_TREE_LIST_PATH)

downloader = GBIFImageDownloader()

species_keys = df["species_key"].dropna().astype(int).unique().tolist()

(
    gbif_occurrence_count,
    minio_occurrence_count,
    average_images_per_occurrence_count,
    all_objects_minio_count,
    species_priority,
) = prioritize_classes_with_most_missing_objects(
    downloader, species_keys, OUTPUT_PATH, QUERY_PARAMS
)

logger.info(f"There are {gbif_occurrence_count} GBIF-Occurrences in total.")
logger.info(f"There are {minio_occurrence_count} MINIO-Occurrences in total.")
logger.info(
    f"Average images per occurrence: "
    f"{average_images_per_occurrence_count / len(species_keys)}"
)
logger.info(f"Total objects in MinIO: {all_objects_minio_count}")
logger.info(
    f"Total missing occurrences to download: "
    f"{gbif_occurrence_count - minio_occurrence_count}"
)

species_keys_priority = sorted(
    species_priority.items(), key=lambda item: item[1], reverse=True
)

logger.info(f"Priority species keys: {species_keys_priority}")

for species_key, _ in species_keys_priority:

    params = QUERY_PARAMS.copy()
    params["taxonKey"] = species_key

    try:
        crawler = GBIFCrawler(downloader=downloader, query_params=params)
        crawler.crawl()

    except (ValueError, KeyError) as e:
        logger.error("Error processing taxon key %s: %s", species_key, e)
        continue

logger.info("MinIO-Logging finished successfully.")
