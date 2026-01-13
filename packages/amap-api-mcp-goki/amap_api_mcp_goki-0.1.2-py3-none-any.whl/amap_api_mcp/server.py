"""Amap API MCP Server implementation."""

import os
from typing import Annotated

import requests
from dotenv import load_dotenv
from mcp.server import FastMCP
from mcp.types import TextContent
from pydantic import Field

# Load environment variables
load_dotenv()

# Get API configuration from environment variables
AMAP_KEY = os.getenv("AMAP_KEY")
ADCODE_URL = os.getenv("ADCODE_URL", "https://restapi.amap.com/v3/geocode/geo?")
WEATHER_URL = os.getenv("WEATHER_URL", "https://restapi.amap.com/v3/weather/weatherInfo?")

# Create FastMCP server instance
server = FastMCP(name="amap-api-mcp-server")


async def get_adcode(city: str) -> str | None:
    """Get the administrative code (adcode) for a given city.
    
    Args:
        city: The name of the city to look up
        
    Returns:
        The adcode string if found, None otherwise
    """
    try:
        params = {"address": city, "key": AMAP_KEY}
        res = requests.get(ADCODE_URL, params=params, timeout=10)
        res.raise_for_status()  # Trigger HTTP errors (like 400/500)
        data = res.json()

        # Check if the returned result is valid
        if data.get("status") != "1" or not data.get("geocodes"):
            return None

        return data["geocodes"][0]["adcode"]
    except Exception as e:
        print(f"Failed to get adcode: {str(e)}")
        return None


@server.tool(title="天气查询", description="根据输入的地名使用高德api查询实时天气。")
async def get_weather(
    city: Annotated[str, Field(description="输入具体的城市，最好带上\"市\"、\"区\"防止重名")]
) -> list[TextContent]:
    """Query real-time weather information for a given city using Amap API.
    
    Args:
        city: The name of the city to query weather for
        
    Returns:
        A list containing TextContent with weather information or error message
    """
    # Check API Key
    if not AMAP_KEY:
        return [TextContent(type="text", text="错误：未配置高德地图API Key")]

    # Get adcode
    adcode = await get_adcode(city)
    if not adcode:
        return [TextContent(type="text", text=f"错误：无法获取{city}的adcode，请检查城市名称是否正确")]

    # Call weather API
    try:
        params = {"city": adcode, "key": AMAP_KEY, "extensions": "base"}  # extensions=base returns basic weather
        res = requests.get(WEATHER_URL, params=params, timeout=10)
        res.raise_for_status()
        weather_data = res.json()

        # Parse weather result
        if weather_data.get("status") != "1" or not weather_data.get("lives"):
            return [TextContent(type="text", text=f"错误：未查询到{city}的天气数据")]

        live_weather = weather_data["lives"][0]
        weather_text = (
            f"{city}实时天气：\n"
            f"温度：{live_weather['temperature']}℃\n"
            f"天气：{live_weather['weather']}\n"
            f"风向：{live_weather['winddirection']}\n"
            f"风力：{live_weather['windpower']}级\n"
            f"湿度：{live_weather['humidity']}%"
        )
        return [TextContent(type="text", text=weather_text)]

    except Exception as e:
        return [TextContent(type="text", text=f"查询天气失败：{str(e)}")]


def main() -> None:
    """Entry point for the MCP server."""
    server.run(transport="stdio")


if __name__ == "__main__":
    main()