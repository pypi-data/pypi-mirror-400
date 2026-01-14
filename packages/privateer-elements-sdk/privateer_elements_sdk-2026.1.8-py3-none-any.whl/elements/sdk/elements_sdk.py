import os
import warnings
from dataclasses import dataclass

from elements_api import ElementsAsyncClient

from elements.sdk.api.algorithm import APIAlgorithm, APIAlgorithmVersion, APIAlgorithmConfig, APIAlgorithmComputation
from elements.sdk.api.analysis import APIAnalysis, APIAnalysisVersion, APIAnalysisConfig, APIAnalysisComputation
from elements.sdk.api.aoi import APIAOI, APIAOITransaction, APIAOIVersion, APIAOICollection
from elements.sdk.api.credit import APICredit
from elements.sdk.api.data import APIDataSource, APIDataType
from elements.sdk.api.permission import APIPermission
from elements.sdk.api.result import APIResult
from elements.sdk.api.toi import APIToi
from elements.sdk.api.user import APIUser
from elements.sdk.api.visualization import APIVisualization
from elements.sdk.api.order import APIOrder
from elements.sdk.api.tasking_order import APITaskingOrder
from elements.sdk.api.filter import APIFilter, APIProjectFilter


@dataclass
class ElementsSDK:
    """
    https://docs.terrascope.orbitalinsight.com/docs
    """
    algorithm: APIAlgorithm
    algorithm_version: APIAlgorithmVersion
    algorithm_config: APIAlgorithmConfig
    algorithm_computation: APIAlgorithmComputation

    analysis: APIAnalysis
    analysis_version: APIAnalysisVersion
    analysis_config: APIAnalysisConfig
    analysis_computation: APIAnalysisComputation

    aoi: APIAOI
    aoi_transaction: APIAOITransaction
    aoi_version: APIAOIVersion
    aoi_collection: APIAOICollection

    toi: APIToi

    credit: APICredit

    data_source: APIDataSource
    data_type: APIDataType

    permission: APIPermission

    result: APIResult

    visualization: APIVisualization

    user: APIUser

    order: APIOrder

    tasking_order: APITaskingOrder

    filter: APIFilter

    project_filter: APIProjectFilter

    client: ElementsAsyncClient

    def __init__(self, client: ElementsAsyncClient = None, timeout: int = None):
        if timeout is None:
            timeout = int(os.getenv('ELEMENTS_TIMEOUT', default='60'))
        if client is None:
            client = self.create_client()

        # Set Up Algo APIs
        self.algorithm = APIAlgorithm(client=client, timeout=timeout)
        self.algorithm_version = APIAlgorithmVersion(client=client, timeout=timeout)
        self.algorithm_config = APIAlgorithmConfig(client=client, timeout=timeout)
        self.algorithm_computation = APIAlgorithmComputation(client=client, timeout=timeout)

        # Set Up Analysis APIs
        self.analysis = APIAnalysis(client=client, timeout=timeout)
        self.analysis_version = APIAnalysisVersion(client=client, timeout=timeout)
        self.analysis_config = APIAnalysisConfig(client=client, timeout=timeout)
        self.analysis_computation = APIAnalysisComputation(client=client, timeout=timeout)

        # Set Up AOI APIs
        self.aoi = APIAOI(client=client, timeout=timeout)
        self.aoi_transaction = APIAOITransaction(client=client, timeout=timeout)
        self.aoi_version = APIAOIVersion(client=client, timeout=timeout)
        self.aoi_collection = APIAOICollection(client=client, timeout=timeout)

        # Set Up AOI APIs
        self.toi = APIToi(client=client, timeout=timeout)

        # Set Up APICredit APIs
        self.credit = APICredit(client=client, timeout=timeout)

        # Set Up Data APIs
        self.data_type = APIDataType(client=client, timeout=timeout)
        self.data_source = APIDataSource(client=client, timeout=timeout)

        # Set Up Permission APIs
        self.permission = APIPermission(client=client, timeout=timeout)

        # Set Up APIResult APIs
        self.result = APIResult(client=client, timeout=timeout)

        # Set Up Visualization APIs
        self.visualization = APIVisualization(client=client, timeout=timeout)

        # Set Up User APIs
        self.user = APIUser(client=client, timeout=timeout)

        # set up order APIs
        self.order = APIOrder(client=client, timeout=timeout)

        # Set Up Tasking Order APIs
        self.tasking_order = APITaskingOrder(client=client, timeout=timeout)

        # Set Up Filter APIs
        self.filter = APIFilter(client=client, timeout=timeout)
        self.project_filter = APIProjectFilter(client=client, timeout=timeout)

    @staticmethod
    def create_client(terrascope_host=None, terrascope_api_token=None):
        # ELEMENTS_HOST
        if not terrascope_host:
            terrascope_host = os.getenv('ELEMENTS_API_HOST')
            if not terrascope_host:
                raise ValueError("ELEMENTS_API_HOST environment variable is required")

        # ELEMENTS_API_PORT
        terrascope_port_str = os.getenv('ELEMENTS_API_PORT', '443')
        try:
            terrascope_port = int(terrascope_port_str)
        except ValueError:
            raise ValueError(f"ELEMENTS_API_PORT must be an integer, got '{terrascope_port_str}'")

        # ELEMENTS_API_TOKEN
        if not terrascope_api_token:
            terrascope_api_token = os.getenv('ELEMENTS_API_TOKEN')
            if not terrascope_api_token:
                raise ValueError("ELEMENTS_API_TOKEN environment variable is required")

        # ELEMENTS_SECURE
        secure_string = os.getenv('ELEMENTS_SECURE', 'True')
        secure = secure_string.lower() in ['true', 'yes', '1']

        # Create client
        client = ElementsAsyncClient(
            terrascope_host,
            terrascope_port,
            api_token=terrascope_api_token,
            secure=secure
        )

        return client
