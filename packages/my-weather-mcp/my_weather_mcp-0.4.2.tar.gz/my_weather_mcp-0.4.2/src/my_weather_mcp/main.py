import json
import os
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("WeatherServer")
USER_AGENT = 'weather-app/1.0'


async def fetch_weather(loc):
    """
    使用高德地图API查询天气函数
    :param loc: 必要参数，字符串类型，用于表示查询天气的具体城市名称（中文），
                例如：'北京市'、'上海'、'广州市'；
    :return：高德地图API查询天气的结果，具体URL请求地址为：https://restapi.amap.com/v3/weather/weatherInfo
             返回结果对象类型为解析之后的JSON格式对象，并用字符串形式进行表示，其中包含了天气信息
    """
    # Step 1.构建请求URL
    url = "https://restapi.amap.com/v3/weather/weatherInfo"

    # Step 2.设置查询参数
    params = {
        "key": 'bf2475b1a5ab3aaeafc98b5e78c06916',  # 高德地图API密钥
        "city": loc,  # 城市名称（支持中文）
        "extensions": "base",  # 气象类型：base-实况天气，all-预报天气
        "output": "JSON"  # 返回格式
    }
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()  # 返回字典类型
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP 错误: {e.response.status_code}"}
        except Exception as e:
            return {"error": f"请求失败: {str(e)}"}


def format_weather(data: dict[str, Any] | str) -> str:
    """
    将天气数据格式化易读文本。
    :param data: 天气数据(可以是字典或JSON字符串)
    :return: 格式化后的天气信息字符串
    """
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception as e:
            return f'无法解析天气数据:{e}'

    if 'error' in data:
        return data['error']
    city = data.get('lives', {})[0]['city']
    temp = data.get('lives', {})[0]['temperature']
    humidity = data.get('lives', {})[0]['humidity']
    wind_speed = data.get('lives', {})[0]['windpower']
    weather = data.get('lives', {})[0]['weather']

    return (
        f"{city}"
        f"温度{temp}"
        f'湿度{humidity}'
        f'风速{wind_speed}'
        f'天气{weather}'
    )


@mcp.tool()
async def query_weather(city: str) -> str:
    """
    输入指定城市的英文名称，返回今日天气查询结果。
    :param city: 城市名称（需使用中文）
    :return: 格式化后的天气信息
    """
    data = await fetch_weather(city)
    return format_weather(data)

# if __name__ == '__main__':
#     # 启动MCP服务，使用标准输入输出作为传输方式
#     mcp.settings.host = "0.0.0.0"
#     mcp.settings.port = 8000
#     mcp.run(transport='stdio')
#     print("MCP服务已启动，等待工具调用...")

if __name__ == '__main__':
    # 启动 MCP 服务，使用 sse 或 streamable-http 协议
    # mcp.run(transport='stdio')
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 8000
    mcp.run(transport='sse')
    # mcp.run(transport='streamable-http')
