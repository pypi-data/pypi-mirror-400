"""
AIGC Auth Legacy System Adapter

提供旧系统接入支持，包括：
1. 字段映射配置
2. 用户数据同步
3. 密码处理策略
4. Webhook 推送支持
"""

import os
import hmac
import hashlib
import json
import logging
import requests
from typing import Optional, List, Dict, Any, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class PasswordMode(Enum):
    """密码处理模式"""
    UNIFIED = "unified"  # 统一初始密码
    CUSTOM_MAPPING = "custom_mapping"  # 自定义映射函数


class SyncDirection(Enum):
    """同步方向"""
    AUTH_TO_LEGACY = "auth_to_legacy"  # aigc-auth → 旧系统
    LEGACY_TO_AUTH = "legacy_to_auth"  # 旧系统 → aigc-auth
    BIDIRECTIONAL = "bidirectional"  # 双向同步


@dataclass
class FieldMapping:
    """字段映射配置"""
    auth_field: str  # aigc-auth 字段名
    legacy_field: str  # 旧系统字段名
    transform_to_legacy: Optional[Callable[[Any], Any]] = None  # auth → legacy 转换函数
    transform_to_auth: Optional[Callable[[Any], Any]] = None  # legacy → auth 转换函数
    required: bool = False  # 是否必填
    default_value: Any = None  # 默认值


@dataclass
class SyncConfig:
    """同步配置"""
    # 基本配置
    enabled: bool = True
    direction: SyncDirection = SyncDirection.AUTH_TO_LEGACY
    
    # 字段映射
    field_mappings: List[FieldMapping] = field(default_factory=list)
    
    # 唯一标识字段（用于匹配用户）
    unique_field: str = "username"
    
    # 密码处理
    password_mode: PasswordMode = PasswordMode.UNIFIED
    unified_password: str = "Abc@123456"  # 统一初始密码
    password_mapper: Optional[Callable[[str], str]] = None  # 自定义密码映射函数
    
    # Webhook 配置
    webhook_enabled: bool = False
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    webhook_retry_count: int = 3
    webhook_timeout: int = 10


@dataclass
class LegacyUserData:
    """旧系统用户数据"""
    data: Dict[str, Any]
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        return self.data.copy()


@dataclass
class SyncResult:
    """同步结果"""
    success: bool
    user_id: Optional[int] = None
    auth_user_id: Optional[int] = None
    legacy_user_id: Optional[Any] = None
    message: str = ""
    errors: List[str] = field(default_factory=list)


class LegacySystemAdapter(ABC):
    """
    旧系统适配器抽象基类
    
    接入系统需要继承此类并实现以下方法：
    - get_user_by_unique_field: 通过唯一字段获取用户
    - create_user: 创建用户
    - update_user: 更新用户（可选）
    - get_all_users: 获取所有用户（用于初始化同步）
    """
    
    def __init__(self, sync_config: SyncConfig):
        self.config = sync_config
    
    @abstractmethod
    def get_user_by_unique_field(self, value: Any) -> Optional[LegacyUserData]:
        """通过唯一字段获取旧系统用户"""
        pass
    
    @abstractmethod
    def create_user(self, user_data: Dict[str, Any]) -> Optional[Any]:
        """在旧系统创建用户，返回用户ID"""
        pass
    
    def update_user(self, unique_value: Any, user_data: Dict[str, Any]) -> bool:
        """更新旧系统用户（可选实现）"""
        return False
    
    def get_all_users(self) -> List[LegacyUserData]:
        """获取所有旧系统用户（用于初始化同步）"""
        return []
    
    def transform_auth_to_legacy(self, auth_user: Dict[str, Any]) -> Dict[str, Any]:
        """将 aigc-auth 用户数据转换为旧系统格式"""
        result = {}
        
        for mapping in self.config.field_mappings:
            auth_value = auth_user.get(mapping.auth_field)
            
            if auth_value is None:
                if mapping.required and mapping.default_value is None:
                    raise ValueError(f"Required field '{mapping.auth_field}' is missing")
                auth_value = mapping.default_value
            
            if mapping.transform_to_legacy:
                auth_value = mapping.transform_to_legacy(auth_value)
            
            if auth_value is not None:
                result[mapping.legacy_field] = auth_value
        
        return result
    
    def transform_legacy_to_auth(self, legacy_user: LegacyUserData) -> Dict[str, Any]:
        """将旧系统用户数据转换为 aigc-auth 格式"""
        result = {}
        
        for mapping in self.config.field_mappings:
            legacy_value = legacy_user.get(mapping.legacy_field)
            
            if legacy_value is None:
                if mapping.required and mapping.default_value is None:
                    raise ValueError(f"Required field '{mapping.legacy_field}' is missing")
                legacy_value = mapping.default_value
            
            if mapping.transform_to_auth:
                legacy_value = mapping.transform_to_auth(legacy_value)
            
            if legacy_value is not None:
                result[mapping.auth_field] = legacy_value
        
        return result
    
    def get_password_for_sync(self, legacy_user: Optional[LegacyUserData] = None) -> str:
        """获取同步时使用的密码"""
        if self.config.password_mode == PasswordMode.UNIFIED:
            return self.config.unified_password
        elif self.config.password_mode == PasswordMode.CUSTOM_MAPPING:
            if self.config.password_mapper and legacy_user:
                return self.config.password_mapper(legacy_user.data)
            return self.config.unified_password
        return self.config.unified_password


class WebhookSender:
    """Webhook 发送器"""
    
    def __init__(self, config: SyncConfig):
        self.config = config
    
    def generate_signature(self, payload: str) -> str:
        """生成 HMAC-SHA256 签名"""
        if not self.config.webhook_secret:
            return ""
        
        return hmac.new(
            self.config.webhook_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def send(self, event_type: str, data: Dict[str, Any]) -> bool:
        """发送 webhook 通知"""
        if not self.config.webhook_enabled or not self.config.webhook_url:
            return False
        
        payload = json.dumps({
            "event": event_type,
            "data": data
        }, ensure_ascii=False)
        
        signature = self.generate_signature(payload)
        
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Event": event_type
        }
        
        for attempt in range(self.config.webhook_retry_count):
            try:
                response = requests.post(
                    self.config.webhook_url,
                    data=payload,
                    headers=headers,
                    timeout=self.config.webhook_timeout
                )
                
                if response.status_code == 200:
                    logger.info(f"Webhook sent successfully: {event_type}")
                    return True
                else:
                    logger.warning(f"Webhook failed with status {response.status_code}: {response.text}")
                    
            except requests.RequestException as e:
                logger.error(f"Webhook request failed (attempt {attempt + 1}): {e}")
        
        return False


class UserSyncService:
    """
    用户同步服务
    
    提供以下功能：
    1. 登录时自动同步（auth → legacy）
    2. 初始化批量同步（legacy → auth）
    3. Webhook 增量推送
    """
    
    def __init__(
        self,
        auth_client,  # AigcAuthClient
        legacy_adapter: LegacySystemAdapter
    ):
        self.auth_client = auth_client
        self.adapter = legacy_adapter
        self.config = legacy_adapter.config
        self.webhook_sender = WebhookSender(self.config)
    
    def sync_on_login(self, auth_user_info) -> SyncResult:
        """
        登录时同步用户到旧系统
        
        当用户通过 aigc-auth 登录成功后调用，
        如果旧系统没有该用户则自动创建。
        
        Args:
            auth_user_info: aigc-auth 返回的 UserInfo 对象
            
        Returns:
            SyncResult: 同步结果
        """
        if not self.config.enabled:
            return SyncResult(success=True, message="Sync disabled")
        
        if self.config.direction == SyncDirection.LEGACY_TO_AUTH:
            return SyncResult(success=True, message="Direction is legacy_to_auth, skip")
        
        try:
            # 获取唯一标识值
            unique_value = getattr(auth_user_info, self.config.unique_field, None)
            if not unique_value:
                return SyncResult(
                    success=False, 
                    message=f"Unique field '{self.config.unique_field}' not found in auth user"
                )
            
            # 检查旧系统是否已有该用户
            legacy_user = self.adapter.get_user_by_unique_field(unique_value)
            
            if legacy_user:
                # 用户已存在，可选更新
                if self.config.direction == SyncDirection.BIDIRECTIONAL:
                    auth_data = self._user_info_to_dict(auth_user_info)
                    legacy_data = self.adapter.transform_auth_to_legacy(auth_data)
                    self.adapter.update_user(unique_value, legacy_data)
                
                return SyncResult(
                    success=True,
                    auth_user_id=auth_user_info.id,
                    legacy_user_id=legacy_user.get("id"),
                    message="User already exists in legacy system"
                )
            
            # 创建新用户
            auth_data = self._user_info_to_dict(auth_user_info)
            legacy_data = self.adapter.transform_auth_to_legacy(auth_data)
            
            # 添加密码
            legacy_data["password"] = self.adapter.get_password_for_sync()
            
            legacy_user_id = self.adapter.create_user(legacy_data)
            
            if legacy_user_id:
                return SyncResult(
                    success=True,
                    auth_user_id=auth_user_info.id,
                    legacy_user_id=legacy_user_id,
                    message="User synced to legacy system"
                )
            else:
                return SyncResult(
                    success=False,
                    auth_user_id=auth_user_info.id,
                    message="Failed to create user in legacy system"
                )
                
        except Exception as e:
            logger.exception("Error syncing user on login")
            return SyncResult(success=False, message=str(e), errors=[str(e)])
    
    def _user_info_to_dict(self, user_info) -> Dict[str, Any]:
        """将 UserInfo 对象转换为字典"""
        return {
            "id": user_info.id,
            "username": user_info.username,
            "nickname": user_info.nickname,
            "email": user_info.email,
            "phone": user_info.phone,
            "avatar": user_info.avatar,
            "roles": user_info.roles,
            "permissions": user_info.permissions,
            "department": user_info.department,
            "company": user_info.company,
            "is_admin": user_info.is_admin
        }
    
    def batch_sync_to_auth(
        self, 
        users: List[LegacyUserData],
        on_progress: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, Any]:
        """
        批量同步旧系统用户到 aigc-auth
        
        Args:
            users: 旧系统用户列表
            on_progress: 进度回调函数 (current, total)
            
        Returns:
            Dict: 同步结果统计
        """
        results = {
            "total": len(users),
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "errors": []
        }
        
        for i, user in enumerate(users):
            try:
                auth_data = self.adapter.transform_legacy_to_auth(user)
                
                # 添加密码
                auth_data["password"] = self.adapter.get_password_for_sync(user)
                
                # 调用 SDK 同步接口
                result = self.auth_client.sync_user_to_auth(auth_data)
                
                if result.get("success"):
                    if result.get("created"):
                        results["success"] += 1
                    else:
                        results["skipped"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append({
                        "user": user.get(self.config.unique_field),
                        "error": result.get("message")
                    })
                    
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "user": user.get(self.config.unique_field),
                    "error": str(e)
                })
            
            if on_progress:
                on_progress(i + 1, len(users))
        
        return results
    
    def send_user_created_webhook(self, auth_user_data: Dict[str, Any]) -> bool:
        """发送用户创建 webhook"""
        return self.webhook_sender.send("user.created", auth_user_data)
    
    def send_user_updated_webhook(self, auth_user_data: Dict[str, Any]) -> bool:
        """发送用户更新 webhook"""
        return self.webhook_sender.send("user.updated", auth_user_data)


# ============ 预设字段映射 ============

def create_default_field_mappings() -> List[FieldMapping]:
    """创建默认字段映射配置（通用基础映射）"""
    return [
        FieldMapping(
            auth_field="username",
            legacy_field="username",
            required=True
        ),
        FieldMapping(
            auth_field="email",
            legacy_field="email"
        ),
        FieldMapping(
            auth_field="nickname",
            legacy_field="nickname"
        ),
        FieldMapping(
            auth_field="phone",
            legacy_field="phone"
        ),
        FieldMapping(
            auth_field="avatar",
            legacy_field="avatar"
        ),
        FieldMapping(
            auth_field="company",
            legacy_field="company"
        ),
        FieldMapping(
            auth_field="department",
            legacy_field="department"
        ),
    ]


# ============ 便捷函数 ============

def create_sync_config(
    field_mappings: List[FieldMapping] = None,
    password_mode: PasswordMode = PasswordMode.UNIFIED,
    unified_password: str = "Abc@123456",
    webhook_url: Optional[str] = None,
    webhook_secret: Optional[str] = None,
    direction: SyncDirection = SyncDirection.AUTH_TO_LEGACY,
    **kwargs
) -> SyncConfig:
    """
    创建同步配置的便捷函数
    
    Args:
        field_mappings: 字段映射列表，默认使用通用映射
        password_mode: 密码处理模式
        unified_password: 统一初始密码
        webhook_url: Webhook 接收地址
        webhook_secret: Webhook 签名密钥
        direction: 同步方向
        
    Returns:
        SyncConfig: 同步配置对象
    """
    return SyncConfig(
        enabled=True,
        direction=direction,
        field_mappings=field_mappings or create_default_field_mappings(),
        password_mode=password_mode,
        unified_password=unified_password,
        webhook_enabled=bool(webhook_url),
        webhook_url=webhook_url,
        webhook_secret=webhook_secret,
        **kwargs
    )
