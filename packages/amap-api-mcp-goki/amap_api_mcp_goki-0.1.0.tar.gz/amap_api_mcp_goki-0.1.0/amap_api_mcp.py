import os

import requests
from dotenv import load_dotenv

from mcp import Tool
from mcp.types import TextContent, TaskMetadata, Tool as MCPTool
from mcp.server import FastMCP
from mcp.server.stdio import stdio_server

from pydantic import Field
from typing import Annotated, List, Any, Dict

load_dotenv()
AMAP_KEY = os.getenv('AMAP_KEY')
ADCODE_URL = os.getenv('ADCODE_URL')
WEATHER_URL = os.getenv('WEATHER_URL')

server = FastMCP(name="amp_api-mcp-server")


# 获取地址代码，基础函数，不暴露作为工具
async def get_adcode(city):
    try:
        params = {"address": city, "key": AMAP_KEY}
        res = requests.get(ADCODE_URL, params=params, timeout=10)
        res.raise_for_status()  # 触发HTTP错误（如400/500）
        data = res.json()

        # 检查返回结果是否有效
        if data.get('status') != '1' or not data.get('geocodes'):
            return None

        return data["geocodes"][0]["adcode"]
    except Exception as e:
        print(f"获取adcode失败：{str(e)}")
        return None


@server.tool(title="天气查询", description="根据输入的地名使用高德api查询实时天气。")
async def get_weather(city: Annotated[str, Field(description="输入具体的城市，最好带上“市”、“区”防止重名")]):
    # 检查API Key
    if not AMAP_KEY:
        return [TextContent(type="text", text="错误：未配置高德地图API Key")]

    # 获取adcode
    adcode = await get_adcode(city)
    if not adcode:
        return [TextContent(type="text", text=f"错误：无法获取{city}的adcode，请检查城市名称是否正确")]

    # 调用天气API
    try:
        params = {"city": adcode, "key": AMAP_KEY, "extensions": "base"}  # extensions=base返回基础天气
        res = requests.get(WEATHER_URL, params=params, timeout=10)
        res.raise_for_status()
        weather_data = res.json()

        # 解析天气结果
        if weather_data.get('status') != '1' or not weather_data.get('lives'):
            return [TextContent(type="text", text=f"错误：未查询到{city}的天气数据")]

        live_weather = weather_data['lives'][0]
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


def main():
    server.run(transport="stdio")


if __name__ == "__main__":
    main()