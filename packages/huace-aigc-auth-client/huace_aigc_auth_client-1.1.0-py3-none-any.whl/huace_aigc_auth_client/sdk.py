"""
AIGC Auth Python SDK

提供以下功能：
1. Token 验证
2. 获取用户信息
3. 权限检查
4. FastAPI/Flask 请求拦截中间件
5. 旧系统接入支持（用户同步）
"""

import os
import time
import hashlib
import requests
import logging
from functools import wraps
from typing import Optional, List, Dict, Any, Callable, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# 尝试加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class UserInfo:
    """用户信息"""
    id: int
    username: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    roles: List[str] = None
    permissions: List[str] = None
    department: Optional[str] = None
    company: Optional[str] = None
    is_admin: Optional[bool] = None

    def __post_init__(self):
        if self.roles is None:
            self.roles = []
        if self.permissions is None:
            self.permissions = []

    def has_role(self, role: str) -> bool:
        """检查是否拥有指定角色"""
        return role in self.roles

    def has_permission(self, permission: str) -> bool:
        """检查是否拥有指定权限"""
        return permission in self.permissions

    def has_any_permission(self, permissions: List[str]) -> bool:
        """检查是否拥有任意一个权限"""
        return any(p in self.permissions for p in permissions)

    def has_all_permissions(self, permissions: List[str]) -> bool:
        """检查是否拥有所有权限"""
        return all(p in self.permissions for p in permissions)


@dataclass
class TokenVerifyResult:
    """Token 验证结果"""
    valid: bool
    user_id: Optional[str] = None
    username: Optional[str] = None
    expires_at: Optional[str] = None


class AigcAuthError(Exception):
    """AIGC Auth SDK 异常"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


class AigcAuthClient:
    """
    AIGC Auth 客户端

    使用方法:
        client = AigcAuthClient(
            app_id="your_app_id",
            app_secret="your_app_secret",
            base_url="https://aigc-auth.huacemedia.com/api/v1"  # 可选
        )

        # 验证 token
        result = client.verify_token(token)

        # 获取用户信息
        user = client.get_user_info(token)

        # 检查权限
        results = client.check_permissions(token, ["user:read", "user:write"])
    """

    def __init__(
        self,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
        cache_ttl: int = 300  # 缓存有效期（秒），默认 5 分钟
    ):
        """
        初始化客户端

        Args:
            app_id: 应用 ID，可从环境变量 AIGC_AUTH_APP_ID 读取
            app_secret: 应用密钥，可从环境变量 AIGC_AUTH_APP_SECRET 读取
            base_url: API 基础 URL，可从环境变量 AIGC_AUTH_BASE_URL 读取
            timeout: 请求超时时间（秒）
            cache_ttl: 缓存有效期（秒），默认 300 秒（5 分钟）
        """
        self.app_id = app_id or os.getenv("AIGC_AUTH_APP_ID")
        self.app_secret = app_secret or os.getenv("AIGC_AUTH_APP_SECRET")
        self.base_url = (
            base_url or
            os.getenv("AIGC_AUTH_BASE_URL") or
            "https://aigc-auth.huacemedia.com/api/v1"
        )
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        
        # 缓存存储: {cache_key: (data, timestamp)}
        self._cache: Dict[str, Tuple[Dict, float]] = {}

        if not self.app_id or not self.app_secret:
            raise ValueError(
                "必须提供 app_id 和 app_secret，"
                "可通过参数传入或设置环境变量 AIGC_AUTH_APP_ID 和 AIGC_AUTH_APP_SECRET"
            )

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Content-Type": "application/json",
            "X-App-ID": self.app_id,
            "X-App-Secret": self.app_secret
        }

    def _generate_cache_key(self, token: str, url: str, method: str, extra_data: Dict = None) -> str:
        """
        生成缓存键
        
        Args:
            token: 用户 token
            url: 请求 URL
            method: 请求方法
            extra_data: 额外的请求参数（会被排序后拼接到 key 中）
            
        Returns:
            str: 缓存键（使用 hash 以节省内存）
        """
        key_string = f"{token}:{url}:{method}"
        
        # 如果有额外参数，将其排序后拼接到 key 中
        if extra_data:
            # 对参数进行排序并转换为字符串
            import json
            sorted_data = json.dumps(extra_data, sort_keys=True, ensure_ascii=False)
            key_string = f"{key_string}:{sorted_data}"
        
        return hashlib.md5(key_string.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """
        从缓存中获取数据
        
        Args:
            cache_key: 缓存键
            
        Returns:
            Optional[Dict]: 缓存的数据，如果缓存不存在或已过期则返回 None
        """
        if cache_key not in self._cache:
            return None
        
        data, timestamp = self._cache[cache_key]
        current_time = time.time()
        
        # 检查缓存是否过期
        if current_time - timestamp > self.cache_ttl:
            # 清理过期缓存
            del self._cache[cache_key]
            return None
        
        return data

    def _set_cache(self, cache_key: str, data: Dict):
        """
        设置缓存
        
        Args:
            cache_key: 缓存键
            data: 要缓存的数据
        """
        self._cache[cache_key] = (data, time.time())
        
        # 简单的缓存清理：如果缓存数量过多，清理所有过期的缓存
        if len(self._cache) > 1000:
            self._clean_expired_cache()

    def _clean_expired_cache(self):
        """清理所有过期的缓存"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if current_time - timestamp > self.cache_ttl
        ]
        for key in expired_keys:
            del self._cache[key]

    def clear_cache(self):
        """清空所有缓存"""
        self._cache.clear()

    def _request(self, method: str, endpoint: str, data: Dict = None, token: str = None) -> Dict:
        """
        发送请求
        
        Args:
            method: 请求方法
            endpoint: 端点路径
            data: 请求数据
            token: 用户 token（用于缓存键）
            
        Returns:
            Dict: 响应数据
        """
        url = f"{self.base_url}/sdk{endpoint}"
        
        # 如果提供了 token，尝试从缓存中获取
        if token:
            # 从 data 中提取 token 之外的参数作为额外的缓存键信息
            extra_data = None
            if data:
                extra_data = {k: v for k, v in data.items() if k != 'token'}
            
            cache_key = self._generate_cache_key(token, url, method, extra_data)
            cached_data = self._get_from_cache(cache_key)
            if cached_data is not None:
                return cached_data
        
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()

            if result.get("code") != 0:
                raise AigcAuthError(
                    result.get("code", -1),
                    result.get("message", "未知错误")
                )

            response_data = result.get("data", {})
            
            # 如果请求成功且提供了 token，缓存响应数据
            if token:
                self._set_cache(cache_key, response_data)
            
            return response_data

        except requests.exceptions.RequestException as e:
            raise AigcAuthError(-1, f"请求失败: {str(e)}")

    def verify_token(self, token: str) -> TokenVerifyResult:
        """
        验证 Token

        Args:
            token: 用户的 access_token

        Returns:
            TokenVerifyResult: 验证结果
        """
        data = self._request("POST", "/token/verify", {"token": token}, token=token)
        return TokenVerifyResult(
            valid=data.get("valid", False),
            user_id=data.get("userId"),
            username=data.get("username"),
            expires_at=data.get("expiresAt")
        )

    def get_user_info(self, token: str) -> UserInfo:
        """
        获取用户信息

        Args:
            token: 用户的 access_token

        Returns:
            UserInfo: 用户信息

        Raises:
            AigcAuthError: 当 token 无效或用户不存在时
        """
        data = self._request("POST", "/user/info", {"token": token}, token=token)
        return UserInfo(
            id=data.get("id"),
            username=data.get("username"),
            nickname=data.get("nickname"),
            email=data.get("email"),
            phone=data.get("phone"),
            avatar=data.get("avatar"),
            roles=data.get("roles", []),
            permissions=data.get("permissions", []),
            department=data.get("department"),
            company=data.get("company"),
            is_admin=data.get("is_admin")
        )

    def check_permissions(
        self,
        token: str,
        permission_codes: List[str]
    ) -> Dict[str, bool]:
        """
        批量检查权限

        Args:
            token: 用户的 access_token
            permission_codes: 权限代码列表

        Returns:
            Dict[str, bool]: 权限检查结果，key 为权限代码，value 为是否拥有
        """
        data = self._request("POST", "/permission/check", {
            "token": token,
            "permissionCodes": permission_codes
        }, token=token)
        return data.get("results", {})

    def get_user_info_from_header(self, authorization: str) -> Optional[UserInfo]:
        """
        从 Authorization header 获取用户信息

        Args:
            authorization: Authorization header 的值，格式为 "Bearer {token}"

        Returns:
            UserInfo: 用户信息，如果验证失败返回 None
        """
        if not authorization:
            return None

        if not authorization.startswith("Bearer "):
            return None

        token = authorization[7:]  # 移除 "Bearer " 前缀

        try:
            return self.get_user_info(token)
        except AigcAuthError:
            return None

    # ============ 用户同步相关方法 ============

    def sync_user_to_auth(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        同步用户到 aigc-auth（用于旧系统初始化同步）

        Args:
            user_data: 用户数据，必须包含 username 和 password

        Returns:
            Dict: 同步结果
                - success: bool 是否成功
                - created: bool 是否新建（False 表示已存在）
                - user_id: int 用户ID
                - message: str 消息
        """
        return self._request("POST", "/sync/user", user_data)

    def batch_sync_users_to_auth(self, users: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量同步用户到 aigc-auth

        Args:
            users: 用户数据列表

        Returns:
            Dict: 批量同步结果
                - total: int 总数
                - success: int 成功数
                - failed: int 失败数
                - skipped: int 跳过数（已存在）
                - errors: List[Dict] 错误详情
        """
        return self._request("POST", "/sync/batch", {"users": users})

    def register_webhook(self, webhook_url: str, events: List[str], secret: Optional[str] = None) -> Dict[str, Any]:
        """
        注册 webhook 接收增量用户

        Args:
            webhook_url: webhook 接收地址
            events: 订阅的事件列表，如 ["user.created", "user.updated"]
            secret: webhook 签名密钥

        Returns:
            Dict: 注册结果
                - webhook_id: str webhook ID
                - success: bool 是否成功
        """
        return self._request("POST", "/webhook/register", {
            "url": webhook_url,
            "events": events,
            "secret": secret
        })

    def unregister_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """
        注销 webhook

        Args:
            webhook_id: webhook ID

        Returns:
            Dict: 注销结果
        """
        return self._request("POST", "/webhook/unregister", {"webhookId": webhook_id})


def require_auth(
    client: AigcAuthClient,
    permissions: List[str] = None,
    any_permission: bool = False
):
    """
    FastAPI 路由装饰器，要求用户登录

    Args:
        client: AigcAuthClient 实例
        permissions: 需要的权限列表（可选）
        any_permission: 是否只需要任意一个权限，默认需要全部

    使用方法:
        @app.get("/protected")
        @require_auth(client)
        def protected_route(user_info: UserInfo):
            return {"user": user_info.username}

        @app.get("/admin")
        @require_auth(client, permissions=["admin:access"])
        def admin_route(user_info: UserInfo):
            return {"admin": True}
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 尝试从 FastAPI 获取 request
            request = kwargs.get("request")
            if request is None:
                for arg in args:
                    if hasattr(arg, "headers"):
                        request = arg
                        break

            if request is None:
                raise AigcAuthError(401, "无法获取请求对象")

            authorization = request.headers.get("Authorization")
            user_info = client.get_user_info_from_header(authorization)

            if user_info is None:
                raise AigcAuthError(401, "未登录或 Token 已过期")

            # 检查权限
            if permissions:
                if any_permission:
                    if not user_info.has_any_permission(permissions):
                        raise AigcAuthError(403, "权限不足")
                else:
                    if not user_info.has_all_permissions(permissions):
                        raise AigcAuthError(403, "权限不足")

            # 将用户信息注入到 kwargs
            kwargs["user_info"] = user_info
            return func(*args, **kwargs)

        return wrapper
    return decorator


class AuthMiddleware:
    """
    通用认证中间件

    支持 FastAPI 和 Flask

    FastAPI 使用方法:
        from fastapi import FastAPI, Request
        from sdk import AigcAuthClient, AuthMiddleware

        app = FastAPI()
        client = AigcAuthClient(app_id="xxx", app_secret="xxx")
        auth_middleware = AuthMiddleware(client)

        @app.middleware("http")
        async def auth_middleware_handler(request: Request, call_next):
            return await auth_middleware.fastapi_middleware(request, call_next)

    Flask 使用方法:
        from flask import Flask
        from sdk import AigcAuthClient, AuthMiddleware

        app = Flask(__name__)
        client = AigcAuthClient(app_id="xxx", app_secret="xxx")
        auth_middleware = AuthMiddleware(client)

        @app.before_request
        def before_request():
            return auth_middleware.flask_before_request()
    """

    def __init__(
        self,
        client: AigcAuthClient,
        exclude_paths: List[str] = None,
        exclude_prefixes: List[str] = None
    ):
        """
        初始化中间件

        Args:
            client: AigcAuthClient 实例
            exclude_paths: 排除的路径列表（精确匹配）
            exclude_prefixes: 排除的路径前缀列表
        """
        self.client = client
        self.exclude_paths = exclude_paths or []
        self.exclude_prefixes = exclude_prefixes or []

    def _should_skip(self, path: str) -> bool:
        """检查是否应该跳过验证"""
        if path in self.exclude_paths:
            return True
        for prefix in self.exclude_prefixes:
            if path.startswith(prefix):
                return True
        return False

    def _extract_token(self, authorization: str) -> Optional[str]:
        """从 Authorization header 提取 token"""
        if not authorization:
            return None
        if not authorization.startswith("Bearer "):
            return None
        return authorization[7:]

    async def fastapi_middleware(self, request, call_next):
        """
        FastAPI 中间件

        使用方法:
            @app.middleware("http")
            async def auth(request: Request, call_next):
                return await auth_middleware.fastapi_middleware(request, call_next)
        """
        from fastapi.responses import JSONResponse

        path = request.url.path

        # 检查是否跳过
        if self._should_skip(path):
            return await call_next(request)

        # 获取 Authorization header
        authorization = request.headers.get("Authorization")
        token = self._extract_token(authorization)

        if not token:
            return JSONResponse(
                status_code=401,
                content={"code": 401, "message": "未提供认证信息", "data": None}
            )

        # 验证 token
        try:
            user_info = self.client.get_user_info(token)
            # 将用户信息存储到 request.state
            request.state.user_info = user_info
            # 处理代理头部，确保重定向（如果有）使用正确的协议
            forwarded_proto = request.headers.get("x-forwarded-proto")
            if forwarded_proto:
                request.scope["scheme"] = forwarded_proto
        except AigcAuthError as e:
            return JSONResponse(
                status_code=401,
                content={"code": e.code, "message": e.message, "data": None}
            )

        return await call_next(request)

    def flask_before_request(self):
        """
        Flask before_request 处理器

        使用方法:
            @app.before_request
            def before_request():
                return auth_middleware.flask_before_request()
        """
        from flask import request, jsonify, g

        path = request.path

        # 检查是否跳过
        if self._should_skip(path):
            return None

        # 获取 Authorization header
        authorization = request.headers.get("Authorization")
        token = self._extract_token(authorization)

        if not token:
            return jsonify({
                "code": 401,
                "message": "未提供认证信息",
                "data": None
            }), 401

        # 验证 token
        try:
            user_info = self.client.get_user_info(token)
            # 将用户信息存储到 flask.g
            g.user_info = user_info
        except AigcAuthError as e:
            return jsonify({
                "code": e.code,
                "message": e.message,
                "data": None
            }), 401

        return None

    def get_current_user_fastapi(self, request) -> Optional[UserInfo]:
        """
        FastAPI 中获取当前用户

        Args:
            request: FastAPI Request 对象

        Returns:
            UserInfo: 用户信息，如果未登录返回 None
        """
        return getattr(request.state, "user_info", None)

    def get_current_user_flask(self) -> Optional[UserInfo]:
        """
        Flask 中获取当前用户

        Returns:
            UserInfo: 用户信息，如果未登录返回 None
        """
        from flask import g
        return getattr(g, "user_info", None)


# 便捷函数：创建 FastAPI 依赖
def create_fastapi_auth_dependency(client: AigcAuthClient):
    """
    创建 FastAPI 认证依赖

    使用方法:
        from fastapi import Depends
        from sdk import AigcAuthClient, create_fastapi_auth_dependency

        client = AigcAuthClient(app_id="xxx", app_secret="xxx")
        get_current_user = create_fastapi_auth_dependency(client)

        @app.get("/me")
        async def get_me(user: UserInfo = Depends(get_current_user)):
            return {"username": user.username}
    """
    from fastapi import Request, HTTPException

    async def get_current_user(request: Request) -> UserInfo:
        authorization = request.headers.get("Authorization")
        user_info = client.get_user_info_from_header(authorization)

        if user_info is None:
            raise HTTPException(status_code=401, detail="未登录或 Token 已过期")

        return user_info

    return get_current_user
