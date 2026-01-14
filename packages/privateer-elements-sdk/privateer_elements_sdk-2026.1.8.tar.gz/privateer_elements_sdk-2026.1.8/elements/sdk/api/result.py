# flake8: noqa: E501
import os
import re
import logging
import tempfile
from zipfile import ZipFile
from collections import defaultdict
from typing import AsyncIterator, Dict, List, Optional

import boto3
import httpx
from google.protobuf.timestamp_pb2 import Timestamp

from elements_api import ElementsAsyncClient
from elements_api.models.common_models_pb2 import Pagination
from elements_api.models.result_pb2 import ResultGetRequest, ResultGetResponse


class APIResult:
    def __init__(self, client: ElementsAsyncClient, timeout):
        self.__timeout = timeout
        self.__client = client
        # External HTTP endpoints (overridable via environment)
        self.__results_api_base_url = os.getenv(
            "RESULT_DATA_SOURCE_API_URL",
            "https://results.orbitalinsight.com"
        )
        self.__app_api_base_url = os.getenv(
            "ELEMENTS_API_URL",
            "https://terrascope-app.orbitalinsight.com/api/v1"
        )
        self.__api_token = os.getenv("ELEMENTS_API_TOKEN")
        self.__httpx_timeout = httpx.Timeout(
            float(self.__timeout), read=300.0
        )

    @staticmethod
    async def merge_download_files(
        algorithm_computation_id_to_data_type_to_downloaded_paths: 
            Dict[str, Dict[str, List[str]]],
        download_dir: str = None
    ) -> Dict[str, Dict[str, str]]:
        download_dir = os.getcwd() if not download_dir else download_dir
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        algorithm_computation_id_to_data_type_to_merged_file =             defaultdict(lambda: defaultdict(str))
        for (algorithm_computation_id,
                data_type_to_downloaded_paths) in algorithm_computation_id_to_data_type_to_downloaded_paths.items():
            for data_type, downloaded_paths in data_type_to_downloaded_paths.items():
                merged_file_dir = os.path.join(download_dir, algorithm_computation_id)
                os.makedirs(merged_file_dir, exist_ok=True)
                merged_file = os.path.join(merged_file_dir, f'{data_type}.csv')
                logging.info(
                    f"Merging files for algorithm_computation_id {algorithm_computation_id} "
                    f"and data_type {data_type} to {merged_file}"
                )

                header_written = False
                with open(merged_file, 'w') as output_csv:
                    for idx, downloaded_path in enumerate(downloaded_paths):
                        with tempfile.TemporaryDirectory() as working_dir:
                            interim_path = f'{working_dir}/{idx}'
                            os.mkdir(interim_path)
                            with ZipFile(downloaded_path, 'r') as zip_ref:
                                zip_ref.extractall(interim_path)
                            csv_path = f'{interim_path}/{data_type}.csv'
                            with open(csv_path, 'r') as input_csv:
                                if header_written:
                                    next(input_csv)
                                output_csv.write(input_csv.read())
                                header_written = True
                algorithm_computation_id_to_data_type_to_merged_file[algorithm_computation_id][data_type] = merged_file
        return algorithm_computation_id_to_data_type_to_merged_file

    async def download(
        self, algorithm_computation_ids: List[str] = None,
        analysis_computation_ids: List[str] = None,
        source_aoi_version: int = None, dest_aoi_version: int = None,
        algo_config_class: str = None,
        algo_config_subclass: str = None, created_on: Timestamp = None,
        observation_start_ts: Timestamp = None,
        max_observation_start_ts: Timestamp = None, data_type: str = None,
        download_dir: str = None
    ) -> Dict[str, Dict[str, List[str]]]:
        """
        algorithm_computation_ids: [Required] List[str] - Algorithm computation IDs

        :return: Dict[str, Dict[str, List[str]]]: mapping of algorithm_computation_id_to_data_type_to_downloaded_paths
        """
        download_dir = os.getcwd() if not download_dir else download_dir

        result_get_responses = await self.get(
            algorithm_computation_ids=algorithm_computation_ids,
            analysis_computation_ids=analysis_computation_ids,
            source_aoi_version=source_aoi_version,
            dest_aoi_version=dest_aoi_version,
            algo_config_class=algo_config_class,
            algo_config_subclass=algo_config_subclass,
            created_on=created_on,
            observation_start_ts=observation_start_ts,
            max_observation_start_ts=max_observation_start_ts,
            include_export_files=True, data_type=data_type
        )

        result_export_credentials = result_get_responses[0].export_credentials
        credentials = result_export_credentials.credentials
        s3 = boto3.client(
            's3',
            aws_access_key_id=credentials.fields['AccessKeyId'].string_value,
            aws_session_token=credentials.fields['SessionToken'].string_value,
            aws_secret_access_key=credentials.fields['SecretAccessKey'].string_value
        )
        pattern = r"https://(.*?)\.s3"
        container_name = re.search(pattern, result_export_credentials.base_url_template).group(1)
        algorithm_computation_id_to_data_type_to_downloaded_paths =             defaultdict(lambda: defaultdict(list))

        for result_get_response in result_get_responses:
            for result in result_get_response.results:
                data_type = result.data_type
                algorithm_computation_id = result.algorithm_computation_id
                for observation in result.observations:
                    key_path = observation.export_file.url
                    if not key_path:
                        continue
                    full_download_path = download_dir + os.path.split(key_path)[0]
                    filename = 'results.zip'
                    os.makedirs(full_download_path)
                    downloaded_path = os.path.join(full_download_path, filename)
                    s3.download_file(container_name, key_path[1:], downloaded_path)
                    algorithm_computation_id_to_data_type_to_downloaded_paths[
                        algorithm_computation_id][data_type].append(downloaded_path)

        logging.info(
            f"Downloaded results for algorithm_computation_ids and data_types: "
            f"{algorithm_computation_id_to_data_type_to_downloaded_paths}"
        )
        return algorithm_computation_id_to_data_type_to_downloaded_paths

    async def get(
        self, algorithm_computation_ids: List[str] = None,
        analysis_computation_ids: List[str] = None,
        source_aoi_version: int = None, dest_aoi_version: int = None,
        algo_config_class: str = None,
        algo_config_subclass: str = None, created_on: Timestamp = None,
        observation_start_ts: Timestamp = None,
        max_observation_start_ts: Timestamp = None,
        include_export_files: bool = None, data_type: str = None
    ) -> List[ResultGetResponse]:
        """
            required: algorithm_computation_ids or analysis_computation_ids
        """
        # Query all GetResultResponses
        result_get_responses = []
        pagination = Pagination(page_size=1000)
        has_next_result = True
        while has_next_result:
            request = ResultGetRequest(
                algorithm_computation_ids=algorithm_computation_ids,
                analysis_computation_ids=analysis_computation_ids,
                source_aoi_version=source_aoi_version,
                dest_aoi_version=dest_aoi_version,
                algo_config_class=algo_config_class,
                algo_config_subclass=algo_config_subclass,
                created_on=created_on,
                observation_start_ts=observation_start_ts,
                max_observation_start_ts=max_observation_start_ts,
                include_export_files=include_export_files,
                data_type=data_type,
                pagination=Pagination(
                    page_token=pagination.next_page_token, page_size=1000
                )
            )
            result_get_response = await self.__client.api.result.get(request, timeout=self.__timeout)
            result_get_responses.append(result_get_response)
            pagination = result_get_response.pagination
            has_next_result = pagination and pagination.next_page_token
        return result_get_responses

    # ---------------------------
    # Results Data Source methods
    # ---------------------------
    async def list_available_collections(self, project_id: str) -> List[str]:
        """
        List available collection IDs for a Terrascope project via the app API.

        Returns a list of strings formatted as "<algorithm_computation_id>---<data_type>".
        """
        if not self.__api_token:
            logging.error("ELEMENTS_API_TOKEN not set; cannot list collections")
            return []
        url = f"{self.__app_api_base_url}/projects/{project_id}/summary"
        try:
            async with httpx.AsyncClient(timeout=self.__httpx_timeout) as client:
                r = await client.get(url, headers=self.get_headers())
                if r.status_code != 200:
                    logging.error(
                        "Failed to fetch project summary for %s: %s %s",
                        project_id,
                        r.status_code,
                        r.text,
                    )
                    return []
                summary_info = r.json()
        except Exception as e:
            logging.exception("Exception fetching project summary for %s: %s", project_id, e)
            return []

        collection_ids: List[str] = []
        analysis_info = summary_info.get(
            "data", {}
        ).get("analysis_computation_info", {})
        for _, computations in analysis_info.items():
            for computation_info in computations:
                computation_id = computation_info.get("algorithm_computation_id")
                output_types = computation_info.get(
                    "algorithm_config_details", {}
                ).get("output_data_types", [])
                for data_type in output_types:
                    collection_ids.append(f"{computation_id}---{data_type}")
        return collection_ids

    async def iter_arrow_batches(
        self,
        collection_id: str,
        start_time: Optional[object] = None,
        end_time: Optional[object] = None,
        params: dict = None,
    ) -> AsyncIterator[object]:
        """
        Stream Arrow RecordBatches for a given collection_id from the Results Data Source API.

        Optional time filtering can be specified using RFC 3339 datetimes:
        - start_time and end_time may be strings already formatted per RFC 3339 or
          Python datetime instances. If only one bound is provided, an open range is used
          for the other bound as per RFC 3339 section 5.6 (".." for open).
        """
        try:
            import pyarrow.ipc as ipc  # type: ignore
        except ImportError as e:
            raise ImportError(
                "pyarrow is required for iter_arrow_batches; install elements-sdk with pyarrow."
            ) from e

        if not self.__api_token:
            raise ValueError("ELEMENTS_API_TOKEN not set; cannot fetch arrow stream")

        feature_url = f"{self.__results_api_base_url}/features/{collection_id}"

        # Build optional datetime range query param
        def _to_rfc3339(value: object) -> str:
            from datetime import datetime, timezone
            if isinstance(value, str):
                return value
            if isinstance(value, datetime):
                # If naive, assume UTC. If tz-aware, convert to UTC and use Z suffix
                if value.tzinfo is None:
                    return value.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
                return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
            raise TypeError("start_time/end_time must be str or datetime if provided")

        params = params or {}
        if start_time is not None and end_time is not None:
            start_str = _to_rfc3339(start_time)
            end_str = _to_rfc3339(end_time)
            params["datetime"] = f"{start_str}/{end_str}"

        async with httpx.AsyncClient(timeout=self.__httpx_timeout) as client:
            try:
                async with client.stream("GET", feature_url, headers=self.get_headers(), params=params) as response:
                    if response.status_code != 200:
                        body = await response.aread()
                        logging.error(
                            "Failed to get Arrow stream for %s: %s, body: %s",
                            collection_id,
                            response.status_code,
                            body.decode(errors="ignore"),
                        )
                        return
                    with tempfile.SpooledTemporaryFile() as tmp:
                        async for chunk in response.aiter_bytes():
                            tmp.write(chunk)
                        if tmp.tell() == 0:
                            return
                        tmp.seek(0)
                        try:
                            with ipc.open_stream(tmp) as reader:
                                for batch in reader:
                                    yield batch
                        except Exception:
                            logging.exception("Failed to parse Arrow stream for %s", collection_id)
                            return
            except Exception:
                logging.exception("Exception fetching Arrow stream for %s", collection_id)
                return

    async def download_parquet(
            self, collection_id: str, dest_path: str, start_time: Optional[object] = None,
            end_time: Optional[object] = None, params: dict = None) -> int:
        """
        Download a collection as Parquet to dest_path. Returns total rows written.
        """
        try:
            import pyarrow.parquet as pq  # type: ignore
        except ImportError as e:
            raise ImportError(
                "pyarrow is required for download_parquet; install elements-sdk with pyarrow."
            ) from e

        total_rows = 0
        writer = None
        try:
            async for batch in self.iter_arrow_batches(
                    collection_id, start_time=start_time, end_time=end_time, params=params):
                if batch is None:
                    continue
                if writer is None:
                    writer = pq.ParquetWriter(dest_path, batch.schema)  # type: ignore
                writer.write_batch(batch)
                total_rows += batch.num_rows
        finally:
            try:
                if writer is not None:
                    writer.close()  # type: ignore
            except Exception:
                pass
        return total_rows

    def get_headers(self):
        _ = self.__client.api.refresh_access_token()
        access_token = self.__client.api.access_token
        return {"Authorization": f"Bearer {access_token}"}

    async def get_collection_info(self, collection_id: str) -> Optional[dict]:
        """
        Retrieve collection info metadata from the Results Data Source API.
        """
        if not self.__api_token:
            logging.error("ELEMENTS_API_TOKEN not set; cannot get collection info")
            return None
        url = f"{self.__results_api_base_url}/collections/{collection_id}"
        try:
            async with httpx.AsyncClient(timeout=self.__httpx_timeout) as client:
                response = await client.get(url, headers=self.get_headers())
                if response.status_code != 200:
                    logging.error(
                        "Failed to get collection info for %s: %s %s",
                        collection_id,
                        response.status_code,
                        await response.aread(),
                    )
                    return None
                return response.json()
        except Exception:
            logging.exception("Exception fetching collection info for %s", collection_id)
            return None
