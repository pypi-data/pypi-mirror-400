from typing import Optional, Literal, List
from .config import ClientConfig
from .transport import Transport
from .models import AgentDetails, InputMode, SearchRequest, SearchResponse, OutputMode


class AgentSearchClient:
    """
    Client for discovering agents via the Agent Search service.

    This client allows agents or applications to:
    - Discover other agents by semantic intent
    - Apply hard constraints (country, capability, IO modes)
    - Retrieve agent cards for invocation
    """

    def __init__(
        self,
        retries: int = 2,
        api_key: Optional[str] = None,
    ):
        self._config = ClientConfig(
            retries=retries,
        )

        self._transport = Transport(self._config)

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> "AgentSearchClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def search(
        self,
        query: str,
        *,
        max_result: Optional[int] = None,
        country: Optional[str] = None,
        capability: Optional[Literal["streaming", "push_notification"]] = None,
        default_input_mode: Optional[List[InputMode]] = None,
        default_output_mode: Optional[List[OutputMode]] = None,
    ) -> SearchResponse:
        """
        Discover agents that can best handle a given query.

        This method performs agent discovery across registered organizations,
        applies hard filters (country, capability, IO modes),
        and ranks matching agents using semantic relevance.

        Parameters
        ----------
        query : str
            Natural language description of the task to be handled.
            Example: "Convert USD to KES" or "Analyze a power purchase agreement".

        max_result : int, optional
            Maximum number of agents to return.
            Defaults to 2.

        country : str, optional
            ISO country name or code of the agent's organization.
            Example: "KE", "Kenya".

        capability : {"streaming", "push_notification"}, optional
            Capability that the agent must support.

            - "streaming": agent can stream partial responses
            - "push_notification": agent can send async notifications

        default_input_mode : {"text", "voice", "image", "video"}, optional
            Primary input modality the agent must support.

        default_output_mode : {"text", "voice", "image", "video"}, optional
            Primary output modality the agent must support.

        Returns
        -------
        SearchResponse
            A response containing matching agents and their agent cards.

        """

        request = SearchRequest(
            query=query,
            max_result=max_result,
            country=country,
            capability=capability,
            default_input_mode=default_input_mode,
            default_output_mode=default_output_mode,
        )

        raw = self._transport.post_json(
            "/search", request.model_dump(exclude_none=True)
        )

        agents = [AgentDetails(**agent) for agent in raw.get("data", [])]

        return SearchResponse(
            success=True,
            agents=agents,
            error=None if raw.get("success") else raw.get("error"),
        )
