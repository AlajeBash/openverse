import os
from collections import namedtuple
from unittest import mock

from airflow.models import TaskInstance

from common.constants import IMAGE
from common.loader.sql import TSV_COLUMNS, create_column_definitions
from common.storage import columns as col
from common.storage.db_columns import IMAGE_TABLE_COLUMNS


POSTGRES_CONN_ID = os.getenv("TEST_CONN_ID")
POSTGRES_TEST_URI = os.getenv("AIRFLOW_CONN_POSTGRES_OPENLEDGER_TESTING")
S3_LOCAL_ENDPOINT = os.getenv("S3_LOCAL_ENDPOINT")
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
SECRET_KEY = os.getenv("AWS_SECRET_KEY")


LOADING_TABLE_COLUMN_DEFINITIONS = create_column_definitions(
    TSV_COLUMNS[IMAGE], is_loading=True
)

CREATE_LOAD_TABLE_QUERY = f"""CREATE TABLE public.{{}} (
  {LOADING_TABLE_COLUMN_DEFINITIONS}
);"""

IMAGE_TABLE_COLUMN_DEFINITIONS = create_column_definitions(IMAGE_TABLE_COLUMNS)

CREATE_IMAGE_TABLE_QUERY = f"""CREATE TABLE public.{{}} (
  {IMAGE_TABLE_COLUMN_DEFINITIONS}
);"""

UNIQUE_CONDITION_QUERY = (
    "CREATE UNIQUE INDEX {table}_provider_fid_idx"
    " ON public.{table}"
    " USING btree (provider, md5(foreign_identifier));"
    "CREATE UNIQUE INDEX {table}_identifier_key"
    " ON public.{table}"
    " USING btree (identifier);"
    "CREATE UNIQUE INDEX {table}_url_key"
    " ON public.{table}"
    " USING btree (url);"
)


PostgresRef = namedtuple("PostgresRef", ["cursor", "connection"])
ti = mock.Mock(spec=TaskInstance)
ti.xcom_pull.return_value = None

COLUMN_NAMES = [column.db_name for column in IMAGE_TABLE_COLUMNS]

# ids for main database columns
updated_idx = COLUMN_NAMES.index(col.UPDATED_ON.db_name)
ingestion_idx = COLUMN_NAMES.index(col.INGESTION_TYPE.db_name)
provider_idx = COLUMN_NAMES.index(col.PROVIDER.db_name)
source_idx = COLUMN_NAMES.index(col.SOURCE.db_name)
fid_idx = COLUMN_NAMES.index(col.FOREIGN_ID.db_name)
land_url_idx = COLUMN_NAMES.index(col.LANDING_URL.db_name)
url_idx = COLUMN_NAMES.index(col.DIRECT_URL.db_name)
thm_idx = COLUMN_NAMES.index(col.THUMBNAIL.db_name)
filesize_idx = COLUMN_NAMES.index(col.FILESIZE.db_name)
license_idx = COLUMN_NAMES.index(col.LICENSE.db_name)
version_idx = COLUMN_NAMES.index(col.LICENSE_VERSION.db_name)
creator_idx = COLUMN_NAMES.index(col.CREATOR.db_name)
creator_url_idx = COLUMN_NAMES.index(col.CREATOR_URL.db_name)
title_idx = COLUMN_NAMES.index(col.TITLE.db_name)
metadata_idx = COLUMN_NAMES.index(col.META_DATA.db_name)
tags_idx = COLUMN_NAMES.index(col.TAGS.db_name)
synced_idx = COLUMN_NAMES.index(col.LAST_SYNCED.db_name)
removed_idx = COLUMN_NAMES.index(col.REMOVED.db_name)
watermarked_idx = COLUMN_NAMES.index(col.WATERMARKED.db_name)
width_idx = COLUMN_NAMES.index(col.WIDTH.db_name)
height_idx = COLUMN_NAMES.index(col.HEIGHT.db_name)
standardized_popularity_idx = COLUMN_NAMES.index(col.STANDARDIZED_POPULARITY.db_name)


def create_query_values(
    column_values: dict,
    columns=None,
):
    if columns is None:
        columns = TSV_COLUMNS[IMAGE]
    result = []
    for column in columns:
        val = column_values.get(column.db_name)
        if val is None:
            val = "null"
        else:
            val = f"'{str(val)}'"
        result.append(val)
    return ",".join(result)