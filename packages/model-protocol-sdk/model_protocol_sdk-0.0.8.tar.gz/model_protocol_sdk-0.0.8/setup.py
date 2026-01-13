from setuptools import setup, find_packages
from pathlib import Path

# 使用 UTF-8 编码读取 README.md
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8")

setup(
    name="model_protocol_sdk",
    version="0.0.8",
    packages=find_packages(include=["sdk_model*", "model_protocol_sdk*"]),
    install_requires=[
        "grpcio>=1.48.2",  # gRPC 运行时依赖
        "grpcio-tools>=1.48.2",  # gRPC 工具，用于生成 Protobuf 文件
        "paho-mqtt>=1.6.1",  # MQTT 客户端
        "fastapi>=0.111.1",
        "uvicorn>=0.24.0",
        "pydantic>=2.5.0",
        "aiohttp>=3.9.0"
    ],
    python_requires=">=3.8",
    author="fuhl",
    description="模型协议开发SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",  # 确保 PyPI 正确渲染 Markdown
)