"""
Token 管理模块

负责 token 的存储、读取、刷新和验证。
"""

import json
import time
import secrets
import hashlib
import base64
import webbrowser
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
import httpx

from ..config import settings


@dataclass
class Credentials:
    """存储的认证信息"""
    access_token: str
    refresh_token: str
    expires_at: int  # Unix timestamp
    token_type: str = "Bearer"
    
    def is_expired(self, buffer_seconds: int = 60) -> bool:
        """检查 token 是否过期（提前 buffer_seconds 秒判定为过期）"""
        return time.time() >= (self.expires_at - buffer_seconds)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Credentials":
        """从字典创建"""
        return cls(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_at=data["expires_at"],
            token_type=data.get("token_type", "Bearer")
        )


class TokenManager:
    """Token 管理器"""
    
    def __init__(self):
        self._credentials: Optional[Credentials] = None
        self._credentials_path = settings.get_credentials_path()
    
    def _log(self, message: str):
        """输出日志到 stderr（避免干扰 stdio 通信）"""
        import sys
        if settings.debug:
            print(f"[TokenManager] {message}", file=sys.stderr)
    
    def load_credentials(self) -> Optional[Credentials]:
        """从文件加载 credentials"""
        if self._credentials:
            return self._credentials
        
        if not self._credentials_path.exists():
            self._log(f"Credentials 文件不存在: {self._credentials_path}")
            return None
        
        try:
            with open(self._credentials_path, "r") as f:
                data = json.load(f)
            self._credentials = Credentials.from_dict(data)
            self._log(f"已加载 credentials，过期时间: {self._credentials.expires_at}")
            return self._credentials
        except Exception as e:
            self._log(f"加载 credentials 失败: {e}")
            return None
    
    def save_credentials(self, credentials: Credentials):
        """保存 credentials 到文件"""
        self._credentials = credentials
        
        # 确保目录存在
        self._credentials_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self._credentials_path, "w") as f:
            json.dump(credentials.to_dict(), f, indent=2)
        
        self._log(f"已保存 credentials 到: {self._credentials_path}")
    
    def clear_credentials(self):
        """清除 credentials"""
        self._credentials = None
        if self._credentials_path.exists():
            self._credentials_path.unlink()
            self._log("已清除 credentials")
    
    async def get_valid_token(self) -> Optional[str]:
        """
        获取有效的 access_token
        
        如果 token 过期，尝试刷新。
        返回 None 表示需要重新认证。
        """
        credentials = self.load_credentials()
        
        if not credentials:
            return None
        
        # 检查是否过期
        if credentials.is_expired():
            self._log("Token 已过期，尝试刷新...")
            refreshed = await self.refresh_token(credentials.refresh_token)
            if refreshed:
                return refreshed.access_token
            else:
                self._log("刷新失败，需要重新认证")
                self.clear_credentials()
                return None
        
        return credentials.access_token
    
    async def refresh_token(self, refresh_token: str) -> Optional[Credentials]:
        """使用 refresh_token 刷新 access_token"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{settings.mcpmarket_url}/oauth/token",
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                        "client_id": settings.oauth_client_id
                    },
                    headers={"Accept": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    credentials = Credentials(
                        access_token=data["access_token"],
                        refresh_token=data.get("refresh_token", refresh_token),
                        expires_at=int(time.time()) + data.get("expires_in", 3600),
                        token_type=data.get("token_type", "Bearer")
                    )
                    self.save_credentials(credentials)
                    self._log("Token 刷新成功")
                    return credentials
                else:
                    self._log(f"Token 刷新失败: {response.status_code} {response.text}")
                    return None
                    
        except Exception as e:
            self._log(f"Token 刷新异常: {e}")
            return None
    
    async def exchange_code_for_token(
        self, 
        code: str, 
        code_verifier: str, 
        redirect_uri: str
    ) -> Optional[Credentials]:
        """用 authorization code 交换 token"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{settings.mcpmarket_url}/oauth/token",
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": redirect_uri,
                        "client_id": settings.oauth_client_id,
                        "code_verifier": code_verifier
                    },
                    headers={"Accept": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    credentials = Credentials(
                        access_token=data["access_token"],
                        refresh_token=data.get("refresh_token", ""),
                        expires_at=int(time.time()) + data.get("expires_in", 3600),
                        token_type=data.get("token_type", "Bearer")
                    )
                    self.save_credentials(credentials)
                    self._log("Token 交换成功")
                    return credentials
                else:
                    self._log(f"Token 交换失败: {response.status_code} {response.text}")
                    return None
                    
        except Exception as e:
            self._log(f"Token 交换异常: {e}")
            return None
    
    @staticmethod
    def generate_pkce() -> tuple[str, str]:
        """
        生成 PKCE code_verifier 和 code_challenge
        
        Returns:
            (code_verifier, code_challenge)
        """
        # 生成 code_verifier (43-128 字符)
        code_verifier = secrets.token_urlsafe(64)[:128]
        
        # 生成 code_challenge (SHA256 + base64url)
        digest = hashlib.sha256(code_verifier.encode()).digest()
        code_challenge = base64.urlsafe_b64encode(digest).decode().rstrip("=")
        
        return code_verifier, code_challenge
    
    @staticmethod
    def generate_state() -> str:
        """生成 OAuth state 参数"""
        return secrets.token_urlsafe(32)
    
    def build_auth_url(self, redirect_uri: str, state: str, code_challenge: str) -> str:
        """构建 OAuth 认证 URL"""
        from urllib.parse import urlencode
        
        params = {
            "response_type": "code",
            "client_id": settings.oauth_client_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "scope": "openid profile"
        }
        
        return f"{settings.mcpmarket_url}/oauth/authorize?{urlencode(params)}"
    
    def open_auth_url(self, url: str) -> bool:
        """尝试在浏览器中打开认证 URL"""
        try:
            webbrowser.open(url)
            return True
        except Exception as e:
            self._log(f"无法打开浏览器: {e}")
            return False


# 全局实例
token_manager = TokenManager()

