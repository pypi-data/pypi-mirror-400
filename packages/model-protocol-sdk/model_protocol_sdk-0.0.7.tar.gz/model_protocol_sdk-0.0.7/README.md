# Device Protocol SDK

无人机设备协议开发工具包，提供标准化接口实现多类型无人机设备的快速接入。

[![PyPI Version](https://img.shields.io/pypi/v/device-protocol-sdk)](https://pypi.org/project/device-protocol-sdk/)
[![Python Versions](https://img.shields.io/pypi/pyversions/device-protocol-sdk)](https://pypi.org/project/device-protocol-sdk/)

## 功能特性

- 🛠️ **协议无关抽象**：统一各类模型的控制接口
- 🔌 **连接池管理**：自动维护模型连接，支持多模型并行控制
- 🚀 **实时状态推送**：内置WebSocket状态推送工具
- 🔍 **动态协议发现**：运行时自动加载用户协议实现

## 安装

```bash
pip install model-protocol-sdk