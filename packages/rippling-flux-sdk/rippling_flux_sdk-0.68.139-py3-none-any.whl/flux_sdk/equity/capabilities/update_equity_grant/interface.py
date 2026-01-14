from abc import ABC, abstractmethod
from io import StringIO

from pydantic import BaseModel

from flux_sdk.equity.capabilities.update_equity_grant.data_models import EquityGrant, PollingPayload


class InputGenerationStrategy(ABC):
    @staticmethod
    @abstractmethod
    def generate(spoke_owner_id: str, *args, **kwargs) -> BaseModel | None:
        """
        This method generates initial input data for update equity grant workflow.
        """


class NoOpInputGenerationStrategy(InputGenerationStrategy):
    """
    No-op implementation of `InputGenerationStrategy`.

    This strategy explicitly indicates that no initial workflow data is required
    for the given provider. It is used when the workflow can be started without
    any provider-specific initialization step.
    """

    @staticmethod
    def generate(spoke_owner_id: str, *args, **kwargs) -> BaseModel | None:
        """
        Return `None` to signal that no initial input data should be generated.
        """
        return None


class PollingPayloadStrategy(ABC):
    @staticmethod
    @abstractmethod
    def get_handle_key(*args, **kwargs) -> str | None:
        """
        Return the field name in the initial provider response that holds the
        async operation handle (if any).
        For example, if the initial async request returns
        {
            "operation_id": 641
        },
        the handle key is "operation_id".

        It can return different handle keys based on the input, if necessary.
        """

    @staticmethod
    @abstractmethod
    def generate_payload(handle: str | None, *args, **kwargs) -> PollingPayload | None:
        """
        Generate the `PollingPayload` used to poll and fetch results for an async
        operation. The returned model should specify:
          - `in_progress_condition`: how to detect that the operation is still running
          - `success_condition`: how to detect that the operation is complete/successful
          - `polling_payload`: request metadata for polling (e.g., URL/method/headers/body)
          - `results_payload`: request metadata to fetch final results when successful

        The `handle` parameter is the async operation identifier (e.g., "641" in the
        example above) that can be used to construct polling and results requests.

        It may return different payloads based on inputs when necessary.
        """


class NoOpPollingPayloadStrategy(PollingPayloadStrategy):
    """
    No-op implementation of `PollingPayloadStrategy`.

    This strategy indicates that the provider does not require status polling.
    It is used when workflow execution is synchronous or when results are
    available immediately without polling.
    """

    @staticmethod
    def get_handle_key(*args, **kwargs) -> str | None:
        """
        Return `None` to indicate that no polling handle key is required.
        """
        return None

    @staticmethod
    def generate_payload(handle: str | None, *args, **kwargs) -> PollingPayload | None:
        """
        Return `None` to signal that no polling payload should be generated.
        """
        return None


class MergeResponseStrategy(ABC):
    @staticmethod
    @abstractmethod
    def merge(response_list: list[str], *args, **kwargs) -> str | None:
        """
        This method merges the response list into a single str.
        """


class NoOpMergeResponseStrategy(MergeResponseStrategy):
    @staticmethod
    def merge(response_list: list[str], *args, **kwargs) -> str | None:
        """
        Return `None` to signal that no merged response should be generated.
        """
        return None


class PaginatedRequestStrategy(ABC):
    @staticmethod
    @abstractmethod
    def get_next_request(request: BaseModel, previous_response: BaseModel | None, *args, **kwargs) -> BaseModel | None:
        """
        This method returns the next request to fetch more pages.
        """


class NoOpPaginatedRequestStrategy(PaginatedRequestStrategy):
    @staticmethod
    def get_next_request(request: BaseModel, previous_response: BaseModel | None, *args, **kwargs) -> BaseModel | None:
        """
        Return `None` to signal that no next request should be generated.
        """
        return None


class UpdateEquityGrant(ABC):
    input_generation_strategy: InputGenerationStrategy
    polling_payload_strategy: PollingPayloadStrategy
    merge_response_strategy: MergeResponseStrategy
    paginated_request_strategy: PaginatedRequestStrategy

    """
    Update equity grant data from third party cap table providers.

    This class represents the "update_equity_grant" capability. The developer is supposed to implement
    update_equity_grant method in their implementation. For further details regarding their
    implementation details, check their documentation.
    
    Behavior that varies by provider is supplied via composition:

    - `input_generation_strategy` defines how initial workflow data is generated.
    - `polling_payload_strategy` defines how payloads for status polling requests are generated.
    - `merge_response_strategy` defines how the response list is merged into a single str.
    - `paginated_request_strategy` defines how to generate the next page request.
    """
    @staticmethod
    @abstractmethod
    def update_equity_grant(company_id: str, stream: StringIO) -> dict[str, EquityGrant]:
        """
        This method parses the equity data stream and returns a dictionary of equity grant unique identifier to equity
        grant
        """
