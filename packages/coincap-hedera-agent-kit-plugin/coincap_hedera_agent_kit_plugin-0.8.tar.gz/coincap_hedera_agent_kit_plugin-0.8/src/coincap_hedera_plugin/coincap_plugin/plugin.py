from __future__ import annotations

from hiero_sdk_python import Client

from hedera_agent_kit.shared.configuration import Context
from hedera_agent_kit.shared.models import ToolResponse
from hedera_agent_kit.shared.parameter_schemas import AccountQueryParameters
from hedera_agent_kit.shared.tool import Tool
from hedera_agent_kit.shared.utils.default_tool_output_parsing import (
    untyped_query_output_parser,
)
from hedera_agent_kit.shared.utils.prompt_generator import PromptGenerator

from coincap_hedera_plugin.coincap_plugin.tool import get_hbar_price_from_coincap


def get_hbar_price_in_usd_prompt(context: Context = {}) -> str:
    """Generate a human-readable description of the get hbar price in usd query tool.

    Args:
        context: Optional contextual configuration that may influence the prompt.

    Returns:
        A string describing the tool, its parameters, and usage instructions.
    """
    context_snippet: str = PromptGenerator.get_context_snippet(context)
    usage_instructions: str = PromptGenerator.get_parameter_usage_instructions()

    return f"""
{context_snippet}

This tool will return the current price in USD of HBAR

Parameters:
- account_id (str, required): The account ID to query
{usage_instructions}
"""


async def get_hbar_price_in_usd_query(
    client: Client,
    context: Context,
    params: None,
) -> ToolResponse:
    """Execute a get hbar price in usd request to coincap API.

    Args:
        client: Hedera client used to determine the network.
        context: Runtime context providing configuration and defaults.

    Returns:
        The current price in USD for HBAR

    Notes:
        This function captures exceptions and returns a failure ToolResponse
        rather than raising, to keep tool behavior consistent for callers.
    """
    try:
        current_price_of_hbar_in_usd = get_hbar_price_from_coincap()
        print(
            f"coincap said that the price in USD of one HBAR is {current_price_of_hbar_in_usd}"
        )
        return ToolResponse(
            human_message=str(current_price_of_hbar_in_usd),
        )
    except Exception as e:
        message: str = f"Failed to get hbar price in usd: {str(e)}"
        print("[get_hbar_price_in_usd_tool]", message)
        return ToolResponse(
            human_message=message,
            error=message,
        )


GET_HBAR_IN_USD_TOOL: str = "get_hbar_price_in_usd_tool"


class GetHbarInUsdTool(Tool):
    """Tool wrapper that exposes the get hbar price in usd capability to the Agent runtime."""

    def __init__(self, context: Context):
        """Initialize the tool metadata and parameter specification.

        Args:
            context: Runtime context used to tailor the tool description.
        """
        self.method: str = GET_HBAR_IN_USD_TOOL
        self.name: str = "get hbar price in usd"
        self.description: str = get_hbar_price_in_usd_prompt(context)
        self.parameters: type[AccountQueryParameters] = AccountQueryParameters
        self.outputParser = untyped_query_output_parser

    async def execute(
        self, client: Client, context: Context, params: AccountQueryParameters
    ) -> ToolResponse:
        """Execute the get hbar price in usd using the provided client, context, and params.

        Args:
            client: Hedera client used to determine the network.
            context: Runtime context providing configuration and defaults.

        Returns:
            The result of the get hbar price in usd as a ToolResponse, including a human-readable
            message and error information if applicable.
        """
        return await get_hbar_price_in_usd_query(client, context, params)
