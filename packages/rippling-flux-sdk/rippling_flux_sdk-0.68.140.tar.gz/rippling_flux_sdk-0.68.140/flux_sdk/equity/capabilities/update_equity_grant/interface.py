from abc import ABC, abstractmethod
from io import StringIO

from flux_sdk.equity.capabilities.update_equity_grant.data_models import EquityGrant
from flux_sdk.equity.capabilities.update_equity_grant.strategies import (
    InputGenerationStrategy,
    MergeResponseStrategy,
    PaginatedRequestStrategy,
    PollingPayloadStrategy,
)


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
