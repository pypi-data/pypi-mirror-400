# http_model_server.py
from typing import Dict, Any, Optional
import asyncio
import json
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import threading
from contextlib import asynccontextmanager
import time

logger = logging.getLogger(__name__)


class HTTPModelServer:
    """
    HTTP模型服务，提供RESTful API供设备端调用
    """

    def __init__(self, model_adapter: 'UniversalModelAdapter', host: str = "0.0.0.0", port: int = 8080):
        """
        初始化HTTP服务

        Args:
            model_adapter: UniversalModelAdapter实例
            host: 监听地址
            port: 监听端口
        """
        self.model_adapter = model_adapter
        self.host = host
        self.port = port
        self.app = None
        self.server = None
        self._lock = threading.RLock()
        self.active_requests: Dict[str, Dict] = {}

        # 创建FastAPI应用
        self._create_app()

    def _create_app(self):
        """创建FastAPI应用"""

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # 启动时
            logger.info(f"HTTP模型服务启动在 {self.host}:{self.port}")
            yield
            # 关闭时
            logger.info("HTTP模型服务关闭")

        self.app = FastAPI(
            title="Edge Model Service API",
            description="边端模型服务HTTP接口",
            version="1.0.0",
            lifespan=lifespan
        )

        # 添加CORS中间件
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # 生产环境应限制来源
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # 注册路由
        self._register_routes()

    def _register_routes(self):
        """注册API路由"""

        @self.app.get("/health")
        async def health_check():
            """健康检查"""
            return {
                "status": "healthy",
                "service": "edge_model_service",
                "protocol_name": self.model_adapter.protocol_name,
                "timestamp": time.time()
            }

        @self.app.get("/models")
        async def get_models():
            """获取所有支持的模型信息"""
            try:
                models_info = []
                # 这里假设model_adapter有方法获取所有模型
                # 如果只有单个模型，可以这样处理
                model_info = self.model_adapter.get_model_info(self.model_adapter.protocol_name)
                if model_info:
                    models_info.append(model_info)
                return {
                    "success": True,
                    "data": models_info,
                    "count": len(models_info)
                }
            except Exception as e:
                logger.error(f"获取模型信息失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/models/{model_id}")
        async def get_model_info(model_id: str):
            """获取特定模型信息"""
            try:
                model_info = self.model_adapter.get_model_info(model_id)
                if not model_info:
                    raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
                return {
                    "success": True,
                    "data": model_info
                }
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"获取模型信息失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/models/{model_id}/execute")
        async def execute_model(
                model_id: str,
                request_data: Dict[str, Any],
                background_tasks: BackgroundTasks,
                x_session_id: Optional[str] = Header(None),
                x_mission_id: Optional[str] = Header(None)
        ):
            """
            执行模型预测

            Headers:
                X-Session-ID: 会话ID（可选）
                X-Mission-ID: 任务ID（可选）

            Body:
                {
                    "inputs": "输入数据",  # 可以是字符串、数字、列表、字典等
                    "params": {            # 可选参数
                        "param1": "value1"
                    }
                }
            """
            try:
                # 验证模型是否存在
                model_info = self.model_adapter.get_model_info()
                if not model_info:
                    raise HTTPException(status_code=404, detail=f"Model {model_id} not found")

                # 提取输入和参数
                inputs = request_data.get("inputs")
                if inputs is None:
                    raise HTTPException(status_code=400, detail="Missing 'inputs' field")

                params = request_data.get("params", {})

                # 设置会话和任务ID（如果提供）
                if x_session_id:
                    params["session_id"] = x_session_id
                if x_mission_id:
                    self.model_adapter.set_current_mission_id(x_mission_id)
                    params["mission_id"] = x_mission_id

                # 记录请求
                request_id = f"req_{int(time.time() * 1000)}_{threading.get_ident()}"
                with self._lock:
                    self.active_requests[request_id] = {
                        "model_id": model_id,
                        "start_time": time.time(),
                        "session_id": x_session_id,
                        "mission_id": x_mission_id
                    }

                logger.info(f"开始执行模型 {model_id}, 请求ID: {request_id}")

                try:
                    # 执行模型
                    result = self.model_adapter.execute_model(inputs, **params)

                    # 清理请求记录
                    with self._lock:
                        if request_id in self.active_requests:
                            elapsed = time.time() - self.active_requests[request_id]["start_time"]
                            logger.info(f"模型执行完成: {model_id}, 耗时: {elapsed:.2f}s")
                            del self.active_requests[request_id]

                    return {
                        "success": True,
                        "data": result,
                        "model_id": model_id,
                        "request_id": request_id,
                        "execution_time": elapsed
                    }

                except Exception as e:
                    logger.error(f"模型执行失败: {e}")
                    # 清理失败的请求记录
                    with self._lock:
                        if request_id in self.active_requests:
                            del self.active_requests[request_id]

                    raise HTTPException(status_code=500, detail=f"Model execution failed: {str(e)}")

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"请求处理失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/batch_execute")
        async def batch_execute(request_data: Dict[str, Any]):
            """
            批量执行模型

            Body:
                {
                    "tasks": [
                        {
                            "model_id": "model1",
                            "inputs": {...},
                            "params": {...}
                        },
                        {
                            "model_id": "model2",
                            "inputs": {...},
                            "params": {...}
                        }
                    ],
                    "parallel": true  # 是否并行执行
                }
            """
            try:
                tasks = request_data.get("tasks", [])
                parallel = request_data.get("parallel", True)

                if not tasks:
                    raise HTTPException(status_code=400, detail="No tasks provided")

                results = []

                if parallel:
                    # 并行执行
                    import asyncio
                    async def execute_single_task(task):
                        try:
                            result = self.model_adapter.execute_model(
                                task.get("inputs"),
                                **task.get("params", {})
                            )
                            return {
                                "model_id": task.get("model_id"),
                                "success": True,
                                "data": result
                            }
                        except Exception as e:
                            return {
                                "model_id": task.get("model_id"),
                                "success": False,
                                "error": str(e)
                            }

                    # 创建协程任务
                    coroutines = [execute_single_task(task) for task in tasks]
                    task_results = await asyncio.gather(*coroutines, return_exceptions=True)
                    results = list(task_results)

                else:
                    # 串行执行
                    for task in tasks:
                        try:
                            result = self.model_adapter.execute_model(
                                task.get("inputs"),
                                **task.get("params", {})
                            )
                            results.append({
                                "model_id": task.get("model_id"),
                                "success": True,
                                "data": result
                            })
                        except Exception as e:
                            results.append({
                                "model_id": task.get("model_id"),
                                "success": False,
                                "error": str(e)
                            })

                return {
                    "success": True,
                    "results": results,
                    "total": len(tasks),
                    "successful": sum(1 for r in results if r.get("success", False))
                }

            except Exception as e:
                logger.error(f"批量执行失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/requests/active")
        async def get_active_requests():
            """获取活跃请求列表"""
            with self._lock:
                return {
                    "success": True,
                    "data": self.active_requests,
                    "count": len(self.active_requests)
                }

        @self.app.get("/status")
        async def get_service_status():
            """获取服务状态"""
            return {
                "status": "running",
                "protocol_name": self.model_adapter.protocol_name,
                "http_server": f"{self.host}:{self.port}",
                "active_requests": len(self.active_requests),
                "uptime": getattr(self, '_start_time', 0),
                "timestamp": time.time()
            }

    async def start(self):
        """启动HTTP服务器"""
        try:
            config = uvicorn.Config(
                app=self.app,
                host=self.host,
                port=self.port,
                loop="asyncio",
                log_level="info",
                access_log=True
            )

            self.server = uvicorn.Server(config)
            self._start_time = time.time()

            # 在后台启动服务器
            server_task = asyncio.create_task(self.server.serve())
            logger.info(f"HTTP模型服务启动成功: http://{self.host}:{self.port}")

            return server_task

        except Exception as e:
            logger.error(f"启动HTTP服务失败: {e}")
            raise

    async def stop(self):
        """停止HTTP服务器"""
        if self.server:
            self.server.should_exit = True
            logger.info("HTTP服务正在停止...")