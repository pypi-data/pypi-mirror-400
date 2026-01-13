import asyncio
import os
from typing import List, Optional
from urllib.parse import quote

from .model import Prompt

from langfuse import Langfuse
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger


class Interactive(Langfuse):
    """
    A comprehensive manager class for InteractiveAI utilities including initialization,
    observation, scoring, dataset management, and parallel processing.
    """

    def __init__(
        self,
        public_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        host: Optional[str] = "https://app.interactive.ai",
        **kwargs
    ) -> None:
        """
        Initialize the InteractiveAI Client

        To get your keys go to https://app.interactiveai.com/settings/api-keys

        Args:
            public_key: InteractiveAI public key (defaults to INTERACTIVEAI_PUBLIC_KEY env var)
            secret_key: InteractiveAI secret key (defaults to INTERACTIVEAI_SECRET_KEY env var)
            host: InteractiveAI host (defaults to https://app.interactive.ai)
        """
        if public_key is None:
            public_key = os.environ.get("INTERACTIVEAI_PUBLIC_KEY")
            if public_key is None:
                raise ValueError("INTERACTIVEAI_PUBLIC_KEY is not set in .env nor passed as argument, please check documentation at https://docs.interactive.ai/docs/keys")
        if secret_key is None:
            secret_key = os.environ.get("INTERACTIVEAI_SECRET_KEY")
            if secret_key is None:
                raise ValueError("INTERACTIVEAI_SECRET_KEY is not set in .env nor passed as argument, please check documentation at https://docs.interactive.ai/docs/keys")
        
        # Initialize InteractiveAI client
        super().__init__(
            public_key=public_key,
            secret_key=secret_key,
            host=host,
            **kwargs
        )

    async def fetch_routines(
        self, routines_folder: str = "routines", label: str = "production"
    ) -> List[Prompt]:
        """
        Fetches routines asynchronously, filtering by folder and label.
        """
        try:
            # TODO: Implement pagination loop
            res = await self.async_api.prompts.list(page=1, limit=100)
        except Exception as e:
            logger.error(f"Failed to list prompts: {e}")
            return []

        prompts_meta = res.data

        # Filter prompts first to avoid unnecessary processing
        prompts_to_fetch = []
        for prompt_meta in prompts_meta:
            if (
                prompt_meta.name.startswith(routines_folder)
                and label in prompt_meta.labels
            ):
                prompts_to_fetch.append(prompt_meta)
        logger.debug(f"Prompts to fetch: {prompts_to_fetch}")

        # Define a helper function to fetch a single routine
        # This allows us to use asyncio.gather later
        async def fetch_routine_details(prompt_meta):
            try:
                # Safe URL double encoding to handle "/" in the prompt name
                # Example: encodes to "routine%252Fplayer-login"
                prompt_name_proc = quote(quote(prompt_meta.name, safe=""), safe="")
                routine_prompt = await self.async_api.prompts.get(
                    prompt_name=prompt_name_proc, label=label
                )
                logger.debug(f"Fetched routine: {prompt_meta.name}")

                return routine_prompt
            except Exception as e:
                logger.warning(f"Could not fetch routine '{prompt_meta.name}': {e}")
                return None

        # Execute all fetch requests concurrently
        results = await asyncio.gather(
            *[fetch_routine_details(p) for p in prompts_to_fetch]
        )

        # Filter out any None results from failed fetches
        routines = [r for r in results if r is not None]

        return routines

    def get_prompt(
        self,
        name: str,
        version: Optional[int] = None,
        label: Optional[str] = None,
        routine: Optional[bool] = False,
    ) -> ChatPromptTemplate:

        # make it so the prompt label matches the name of the environment
        if label is None:
            environment = os.getenv("ENV")
            label = environment

        logger.debug(f"Getting prompt: {name} with label: {label}")
        name = quote(
            name, safe=""
        )  # safe URL double encoding to handle "/" in the prompt name
        prompt = super().get_prompt(name=name, version=version, label=label)
        if routine:
            return prompt
        return ChatPromptTemplate.from_template(
            prompt.get_langchain_prompt(),
            metadata={"langfuse_prompt": prompt},
        )

    async def aget_prompt(
        self,
        name: str,
        version: Optional[int] = None,
        label: Optional[str] = None,
        routine: Optional[bool] = False,
    ) -> ChatPromptTemplate:

        # make it so the prompt label matches the name of the environment
        if label is None:
            environment = os.getenv("ENV")
            label = environment

        logger.debug(f"Getting prompt: {name} with label: {label}")
        name = quote(
            name, safe=""
        )  # safe URL double encoding to handle "/" in the prompt name

        # Run the blocking sync call in a separate thread
        prompt = await asyncio.to_thread(
            super().get_prompt, name=name, version=version, label=label
        )

        if routine:
            return prompt

        return ChatPromptTemplate.from_template(
            prompt.get_langchain_prompt(),
            metadata={"langfuse_prompt": prompt},
        )

    