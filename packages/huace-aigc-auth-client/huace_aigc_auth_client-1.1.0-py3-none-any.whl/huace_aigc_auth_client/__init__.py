"""
AIGC Auth Python SDK

使用方法:
    from sdk import AigcAuthClient, require_auth

    # 创建客户端
    client = AigcAuthClient(app_id="your_app_id", app_secret="your_app_secret")

    # 验证 token
    result = client.verify_token(token)

    # 获取用户信息
    user_info = client.get_user_info(token)

    # FastAPI 中间件使用
    @app.get("/protected")
    @require_auth(client)
    def protected_route(user_info: dict):
        return {"user": user_info}
        
旧系统接入:
    from sdk import AigcAuthClient
    from sdk.legacy_adapter import (
        LegacySystemAdapter,
        SyncConfig,
        UserSyncService,
        FieldMapping,
        create_sync_config,
        create_default_field_mappings
    )
    
    # 创建自定义字段映射（根据接入系统的用户表定制）
    field_mappings = create_default_field_mappings()
    # 或自定义: field_mappings = [FieldMapping(...), ...]
    
    sync_config = create_sync_config(
        field_mappings=field_mappings,
        webhook_url="https://your-domain.com/webhook"
    )
    
    # 实现适配器并创建同步服务
    adapter = YourLegacyAdapter(sync_config)
    sync_service = UserSyncService(client, adapter)
"""

from .sdk import (
    AigcAuthClient,
    require_auth,
    AuthMiddleware,
    UserInfo,
    TokenVerifyResult,
    AigcAuthError,
    create_fastapi_auth_dependency
)

from .legacy_adapter import (
    LegacySystemAdapter,
    LegacyUserData,
    SyncConfig,
    SyncDirection,
    PasswordMode,
    FieldMapping,
    UserSyncService,
    WebhookSender,
    SyncResult,
    create_sync_config,
    create_default_field_mappings,
)

__all__ = [
    # 核心类
    "AigcAuthClient",
    "require_auth",
    "AuthMiddleware",
    "UserInfo",
    "TokenVerifyResult",
    "AigcAuthError",
    "create_fastapi_auth_dependency",
    # 旧系统接入
    "LegacySystemAdapter",
    "LegacyUserData",
    "SyncConfig",
    "SyncDirection",
    "PasswordMode",
    "FieldMapping",
    "UserSyncService",
    "WebhookSender",
    "SyncResult",
    "create_sync_config",
    "create_default_field_mappings",
]
__version__ = "1.1.0"
