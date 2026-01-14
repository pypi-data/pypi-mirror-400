from .plugin import GetHbarInUsdTool, GET_HBAR_IN_USD_TOOL
from hedera_agent_kit.shared.plugin import Plugin

conincap_h_plugin = Plugin(
    name="get_hbar_price_in_usd-query-plugin",
    version="1.0.0",
    description="A plugin to get the price of HBAR in USD",
    tools=lambda context: [
        GetHbarInUsdTool(context),
    ],
)

conincap_h_plugin_tool_names = {
    "GET_HBAR_IN_USD_TOOL": GET_HBAR_IN_USD_TOOL,
}

__all__ = [
    "GetHbarInUsdTool",
    "conincap_h_plugin_tool_names",
]
