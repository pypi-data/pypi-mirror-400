import os

from httpx import AsyncClient, Client

from ..shared.schemas import ResearchAgentConfig, ResearchAgentResponse


class ResearchKitAsyncClient:
    def __init__(self, base_url: str, timeout: float = 600.0, api_key: str | None = None) -> None:
        normalized_base_url = base_url.rstrip("/")
        resolved_api_key = api_key or os.environ.get("RESEARCHKIT_API_KEY")

        if not resolved_api_key:
            raise ValueError("RESEARCHKIT_API_KEY is required.")

        headers = {"X-API-Key": resolved_api_key}
        self._client = AsyncClient(base_url=normalized_base_url, timeout=timeout, headers=headers)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def status(self) -> dict[str, str]:
        response = await self._client.get("/")
        response.raise_for_status()

        return response.json()

    async def generate(
        self,
        research_agent_config: ResearchAgentConfig,
        timeout: float | None = None,
    ) -> ResearchAgentResponse:
        payload = research_agent_config.model_dump()
        response = await self._client.post("/generate", json=payload, timeout=timeout)
        response.raise_for_status()

        return ResearchAgentResponse.model_validate(response.json())


class ResearchKitClient:
    def __init__(self, base_url: str, timeout: float = 600.0, api_key: str | None = None) -> None:
        normalized_base_url = base_url.rstrip("/")
        resolved_api_key = api_key or os.environ.get("RESEARCHKIT_API_KEY")

        if not resolved_api_key:
            raise ValueError("RESEARCHKIT_API_KEY is required.")

        headers = {"X-API-Key": resolved_api_key}
        self._client = Client(base_url=normalized_base_url, timeout=timeout, headers=headers)

    def close(self) -> None:
        self._client.close()

    def status(self) -> dict[str, str]:
        response = self._client.get("/")
        response.raise_for_status()

        return response.json()

    def generate(
        self,
        research_agent_config: ResearchAgentConfig,
        timeout: float | None = None,
    ) -> ResearchAgentResponse:
        payload = research_agent_config.model_dump()
        response = self._client.post("/generate", json=payload, timeout=timeout)
        response.raise_for_status()

        return ResearchAgentResponse.model_validate(response.json())
