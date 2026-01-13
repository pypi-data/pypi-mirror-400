import asyncio
import json
import logging
import time
from typing import Callable, Dict
import grpc
import paho.mqtt.client as mqtt
from . import model_pb2
from . import model_pb2_grpc
from json import JSONEncoder
from enum import Enum
from .http_model_server import HTTPModelServer

# 添加日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # 输出到控制台
    ]
)
logger = logging.getLogger(__name__)

class EnumEncoder(JSONEncoder):
    """自定义JSON编码器，支持枚举类型"""
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)
class ModelPusher:
    def __init__(self, model_factory: Callable[[], 'AbstractModel'], http_port: int = 8080):
        self.model_factory = model_factory
        self.models: Dict[str, 'AbstractModel'] = {}
        self.mqtt_client = None
        self.grpc_stub = None
        self.protocol_name = ""
        self.mqtt_connected = False

        # MQTT配置
        self.mqtt_broker = "192.168.1.174"
        self.mqtt_port = 1883
        self.mqtt_username = "admin"
        self.mqtt_password = "public"
        self.ee = 0.006693421622965943
        self.a = 6378137.0  # 长半轴

        # 新增：HTTP服务器实例
        self.http_port = http_port
        self.http_server = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()

    async def run(self, grpc_server_url: str, type_description: str):
        """运行设备推送器的主循环"""
        try:
            await self.connect_server(grpc_server_url, type_description)
        except asyncio.CancelledError:
            logger.info("主循环被取消")
        except Exception as e:
            logger.error(f"主循环异常: {e}")
            raise
        finally:
            await self.cleanup()

    def on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT连接回调"""
        if rc == 0:
            self.mqtt_connected = True
            logger.info("MQTT connected successfully")
            # 订阅相关主题（如果需要接收命令）
            try:
                client.subscribe([
                    (f"models/{self.protocol_name}/command", 1),
                    (f"models/{self.protocol_name}/+/command", 1)
                ])
                logger.info("MQTT订阅成功")
            except Exception as e:
                logger.error(f"MQTT订阅失败: {e}")
        else:
            self.mqtt_connected = False
            error_messages = {
                1: "Connection Refused: incorrect protocol version",
                2: "Connection Refused: identifier rejected",
                3: "Connection Refused: server unavailable",
                4: "Connection Refused: bad username or password",
                5: "Connection Refused: not authorized"
            }
            error_msg = error_messages.get(rc, f"Unknown error code: {rc}")
            logger.error(f"MQTT连接失败: {error_msg}")

    def on_mqtt_disconnect(self, client, userdata, rc):
        """MQTT断开连接回调"""
        self.mqtt_connected = False
        disconnect_messages = {
            0: "正常断开",
            1: "意外断开: 传输层错误",
            2: "意外断开: 协议错误",
            3: "意外断开: 客户端主动断开",
            4: "意外断开: 网络错误",
            5: "意外断开: 被服务器断开",
            6: "意外断开: 保活超时",
            7: "意外断开: 会话被接管"
        }
        message = disconnect_messages.get(rc, f"未知断开原因: {rc}")
        logger.warning(f"MQTT连接断开: {message}")

    def on_mqtt_message(self, client, userdata, msg):
        """MQTT消息回调"""
        try:
            # logger.debug(f"收到MQTT消息: {msg.topic}")
            # 这里可以处理接收到的MQTT命令
            payload = msg.payload.decode('utf-8')
            data = json.loads(payload)
            # logger.debug(f"消息内容: {data}")
        except Exception as e:
            logger.error(f"处理MQTT消息错误: {e}")

    def on_mqtt_log(self, client, userdata, level, buf):
        """MQTT日志回调"""
        if level == mqtt.MQTT_LOG_DEBUG:
            logger.debug(f"MQTT: {buf}")
        elif level == mqtt.MQTT_LOG_INFO:
            logger.info(f"MQTT: {buf}")
        elif level == mqtt.MQTT_LOG_WARNING:
            logger.warning(f"MQTT: {buf}")
        elif level == mqtt.MQTT_LOG_ERR:
            logger.error(f"MQTT: {buf}")

    async def setup_mqtt(self):
        """设置MQTT连接"""
        max_retries = 3
        retry_count = 0

        # 检查配置是否完整
        if not self.mqtt_broker or not self.mqtt_port:
            logger.error("MQTT配置不完整，请先完成设备注册")
            return False

        while retry_count < max_retries:
            try:
                retry_count += 1
                logger.info(f"尝试连接MQTT (尝试 {retry_count}/{max_retries})")

                # 生成唯一的客户端ID - 使用UUID避免重复
                import uuid
                unique_id = str(uuid.uuid4())[:8]  # 取前8位
                client_id = f"{self.protocol_name}_{unique_id}"

                logger.info(f"使用客户端ID: {client_id}")

                self.mqtt_client = mqtt.Client(
                    client_id=client_id,  # 使用生成的唯一ID
                    protocol=mqtt.MQTTv311,
                    transport="tcp",
                    clean_session=True
                )

                # 设置回调
                self.mqtt_client.on_connect = self.on_mqtt_connect
                self.mqtt_client.on_message = self.on_mqtt_message
                self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
                self.mqtt_client.on_log = self.on_mqtt_log

                # 设置认证信息（如果有）
                if self.mqtt_username and self.mqtt_password:
                    logger.info("使用用户名密码认证")
                    self.mqtt_client.username_pw_set(self.mqtt_username, self.mqtt_password)
                else:
                    logger.info("使用匿名连接")

                # 设置连接超时
                self.mqtt_client.connect_timeout = 10

                logger.info(f"连接到MQTT Broker: {self.mqtt_broker}:{self.mqtt_port}")

                # 连接Broker
                try:
                    result = self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)

                    if result != mqtt.MQTT_ERR_SUCCESS:
                        logger.error(f"MQTT连接失败: {mqtt.error_string(result)}")
                        if retry_count < max_retries:
                            await asyncio.sleep(2)
                            continue
                        return False
                except Exception as e:
                    logger.error(f"MQTT连接异常: {e}")
                    if retry_count < max_retries:
                        await asyncio.sleep(2)
                        continue
                    return False

                # 启动MQTT循环
                self.mqtt_client.loop_start()

                # 等待连接建立
                max_wait_time = 15
                wait_time = 0
                while not self.mqtt_connected and wait_time < max_wait_time:
                    await asyncio.sleep(0.5)
                    wait_time += 0.5

                if self.mqtt_connected:
                    logger.info(f"MQTT连接成功: {self.mqtt_broker}:{self.mqtt_port}")
                    return True
                else:
                    logger.error("MQTT连接超时")
                    try:
                        self.mqtt_client.loop_stop()
                        self.mqtt_client.disconnect()
                    except:
                        pass
                    if retry_count < max_retries:
                        await asyncio.sleep(3)
                        continue

            except Exception as e:
                logger.error(f"设置MQTT连接失败: {e}")
                if self.mqtt_client:
                    try:
                        self.mqtt_client.loop_stop()
                        self.mqtt_client.disconnect()
                    except:
                        pass
                if retry_count < max_retries:
                    await asyncio.sleep(2)
                    continue
                return False

        return False

    async def ensure_mqtt_connection(self):
        """确保MQTT连接正常"""
        if not self.mqtt_connected:
            logger.warning("MQTT连接断开，尝试重新连接...")
            return await self.setup_mqtt()
        return True


    async def send_heartbeat(self):
        """通过MQTT发送心跳"""
        while True:
            try:
                if self.mqtt_connected:
                    topic = f"models/{self.protocol_name}/heartbeat"
                    payload = json.dumps({
                        "protocol": self.protocol_name,
                        "timestamp": time.time(),
                        "status": "online"
                    })

                    result = self.mqtt_client.publish(topic, payload, qos=0)
                    if result.rc == mqtt.MQTT_ERR_SUCCESS:
                        logger.debug("心跳发送成功")
                    else:
                        logger.warning(f"心跳发送失败: {mqtt.error_string(result.rc)}")
                else:
                    logger.warning("MQTT未连接，无法发送心跳")
                    await asyncio.sleep(5)  # MQTT断开时等待更长时间
                    continue

                await asyncio.sleep(10)  # 10秒心跳间隔
            except Exception as e:
                logger.error(f"心跳发送失败: {e}")
                await asyncio.sleep(1)

    async def command_stream_handler(self):
        """处理gRPC命令流"""
        try:
            # 创建metadata包含protocol_name
            metadata = [('protocol_name', self.protocol_name)]

            # 创建双向流，携带metadata
            command_stream = self.grpc_stub.ModelCommandStream(metadata=metadata)

            async for command_request in command_stream:
                try:
                    logger.info(f"收到命令请求: {command_request}")
                    # 处理命令
                    mission_id = command_request.mission_id
                    use_models = json.loads(command_request.params)
                    result = ""
                    for use_model in use_models:
                        protocol_name = use_model['protocol_name']
                        inputs = use_model['inputs']
                        if protocol_name not in self.models:
                            logger.info(f"创建新模型实例: {protocol_name}")
                            model = self.model_factory()
                            self.models[protocol_name] = model
                            result = "创建连接成功"
                        model = self.models[protocol_name]
                        model.set_grpc_stub(self.grpc_stub)
                        try:
                            result = model.execute_model(inputs)
                        except Exception as e:
                            raise ValueError(f"命令执行失败: {e}")


                    # 发送成功确认
                    ack = model_pb2.ModelCommandAck(
                        command_id=command_request.command_id,
                        mission_id=mission_id,
                        success=True,
                        data=json.dumps(result) if result else ""
                    )
                    await command_stream.write(ack)
                    logger.info(f"命令执行成功: {command_request.command_id}")

                except Exception as e:
                    logger.error(f"处理命令失败: {e}")
                    # 发送错误确认
                    ack = model_pb2.ModelCommandAck(
                        command_id=command_request.command_id if command_request else "unknown",
                        success=False,
                        message=str(e)
                    )
                    await command_stream.write(ack)


        except grpc.aio.AioRpcError as e:
            logger.error(f"gRPC命令流错误: {e}")
            raise
        except Exception as e:
            logger.error(f"命令流处理异常: {e}")
            raise

    def _update_all_devices_grpc_stub(self):
        """更新所有设备实例的grpc_stub"""
        for device_key, device in self.models.items():
            try:
                device.set_grpc_stub(self.grpc_stub)
                logger.info(f"已更新设备 {device_key} 的grpc_stub")
            except Exception as e:
                logger.error(f"更新设备 {device_key} 的grpc_stub失败: {e}")

    async def connect_server(self, grpc_server_url: str, type_description: str,mqtt_ip=None):
        """连接到gRPC服务器并注册设备"""
        delay = 1
        max_delay = 10  # 设置最大延迟为10秒

        while True:
            try:
                # 创建gRPC通道
                async with grpc.aio.insecure_channel(grpc_server_url) as channel:
                    self.grpc_stub = model_pb2_grpc.ModelServiceStub(channel)
                    # 更新所有已存在设备的grpc_stub
                    self._update_all_devices_grpc_stub()
                    # 注册模型类
                    model = self.model_factory()
                    protocol_name = model.protocol_name()
                    self.protocol_name = protocol_name
                    model.set_grpc_stub(self.grpc_stub)
                    self.models[protocol_name] = model

                    register_request = model_pb2.ModelRegisterRequest(
                        protocol_name=protocol_name,
                        auth_token="model_token",  # 需要实现认证
                        capabilities=json.dumps(model.get_model_info(),
                                                  ensure_ascii=False,
                                                  indent=2,
                                                  cls=EnumEncoder),
                        type_description=type_description
                    )

                    response = await self.grpc_stub.ModelRegister(register_request)

                    if response.success:
                        logger.info(f"设备注册成功: {response.message}")

                        # 如果服务器返回了MQTT配置，使用服务器的配置
                        if hasattr(response, 'mqtt_broker_url') and response.mqtt_broker_url:
                            # self.mqtt_broker = response.mqtt_broker_url
                            if mqtt_ip:
                                self.mqtt_broker = mqtt_ip
                            else:
                                self.mqtt_broker = grpc_server_url.split(':')[0]
                        if hasattr(response, 'mqtt_broker_port') and response.mqtt_broker_port:
                            self.mqtt_broker_port = response.mqtt_broker_port
                        if hasattr(response, 'mqtt_username') and response.mqtt_username:
                            self.mqtt_username = response.mqtt_username
                        if hasattr(response, 'mqtt_password') and response.mqtt_password:
                            self.mqtt_password = response.mqtt_password

                        # 配置MQTT
                        mqtt_success = await self.setup_mqtt()
                        if not mqtt_success:
                            logger.error("MQTT连接失败，继续尝试gRPC连接")
                            await asyncio.sleep(delay)
                            delay = min(delay * 2, max_delay)  # 使用max_delay限制
                            continue

                        # 启动HTTP服务
                        await self.start_http_service()

                        # 启动心跳任务
                        heartbeat_task = asyncio.create_task(self.send_heartbeat())

                        # 启动命令流处理
                        await self.command_stream_handler()

                    else:
                        logger.error(f"设备注册失败: {response.message}")
                        await asyncio.sleep(delay)
                        delay = min(delay * 2, max_delay)  # 使用max_delay限制

            except Exception as e:
                logger.warning(f"gRPC连接失败，{delay}s后重试: {e}")
                await asyncio.sleep(delay)
                delay = min(delay * 2, max_delay)  # 使用max_delay限制

    async def start_http_service(self):
        """启动HTTP服务"""
        try:
            # 获取当前模型实例
            if not self.models:
                logger.warning("没有模型实例，无法启动HTTP服务")
                return

            # 使用第一个模型实例
            model_adapter = next(iter(self.models.values()))

            # 创建HTTP服务器
            self.http_server = HTTPModelServer(
                model_adapter=model_adapter,
                host="0.0.0.0",
                port=self.http_port
            )

            # 在后台启动HTTP服务器
            http_task = asyncio.create_task(self.http_server.start())

            # 可选：将HTTP服务地址注册到云端
            await self.register_http_endpoint()

            return http_task

        except Exception as e:
            logger.error(f"启动HTTP服务失败: {e}")

    async def register_http_endpoint(self):
        """将HTTP端点注册到云端"""
        try:
            if self.grpc_stub and self.protocol_name:
                # 获取本地IP地址
                import socket
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)

                # 构造HTTP端点信息
                http_endpoint = {
                    "protocol": self.protocol_name,
                    "http_url": f"http://{local_ip}:{self.http_port}",
                    "apis": [
                        "/health",
                        "/models",
                        "/models/{model_id}/execute",
                        "/batch_execute"
                    ],
                    "timestamp": time.time()
                }

                # 发送到云端（需要扩展gRPC协议）
                # 这里假设有RegisterHTTPEndpoint方法
                register_request = model_pb2.RegisterHTTPEndpointRequest(
                    protocol_name=self.protocol_name,
                    endpoint_info=json.dumps(http_endpoint)
                )

                response = await self.grpc_stub.RegisterHTTPEndpoint(register_request)
                if response.success:
                    logger.info(f"HTTP端点注册成功: {http_endpoint['http_url']}")

        except Exception as e:
            logger.warning(f"HTTP端点注册失败: {e}")

    async def cleanup(self):
        """清理资源"""
        logger.info("开始清理资源...")

        # 停止HTTP服务
        if self.http_server:
            try:
                await self.http_server.stop()
                logger.info("HTTP服务已停止")
            except Exception as e:
                logger.error(f"停止HTTP服务失败: {e}")


    async def cleanup(self):
        """清理资源"""
        logger.info("开始清理资源...")

        # 设置清理标志，防止重复清理
        if hasattr(self, '_cleaning'):
            return
        self._cleaning = True

        try:
            # 发送离线心跳消息
            if self.mqtt_client and self.mqtt_connected and self.protocol_name:
                try:
                    offline_payload = json.dumps({
                        "protocol": self.protocol_name,
                        "timestamp": time.time(),
                        "status": "offline",
                        "message": "device_disconnected"
                    })

                    topic = f"models/{self.protocol_name}/heartbeat"
                    result = self.mqtt_client.publish(topic, offline_payload, qos=1)

                    if result.rc == mqtt.MQTT_ERR_SUCCESS:
                        logger.info(f"已发送离线心跳到 {topic}")
                    else:
                        logger.warning(f"发送离线心跳失败: {mqtt.error_string(result.rc)}")

                    # 等待消息发送完成
                    await asyncio.sleep(0.1)
                except Exception as e:
                    logger.error(f"发送离线心跳时出错: {e}")

            # 清空设备字典和任务字典
            self.models.clear()

            # 关闭MQTT连接
            if self.mqtt_client:
                try:
                    self.mqtt_client.loop_stop()
                    self.mqtt_client.disconnect()
                    logger.info("MQTT连接已关闭")
                except Exception as e:
                    logger.error(f"关闭MQTT连接时出错: {e}")

            logger.info("资源清理完成")

        except Exception as e:
            logger.error(f"清理过程中发生错误: {e}")
        finally:
            self._cleaning = False