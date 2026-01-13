import json
import base64
import os
from pathlib import Path
from urllib.parse import urlparse


class AppConfig:
    def __init__(self, app_name="oss-cleaner"):
        # Simple cross-platform path logic
        base_dir = Path(os.getenv('APPDATA') or Path.home() / ".config")
        self.config_dir = base_dir / app_name
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "settings.json"
        self.data = self._load()

    def _load(self):
        if self.config_file.exists():
            try:
                return json.loads(self.config_file.read_text(encoding='utf-8'))
            except Exception:
                return {}
        return {}

    def save(self):
        self.config_file.write_text(json.dumps(self.data, indent=4), encoding='utf-8')

    def get_secret(self, key):
        val = self.data.get(key)
        if val:
            try:
                return base64.b64decode(val.encode()).decode()
            except Exception:
                return None
        return None

    def set_secret(self, key, value):
        self.data[key] = base64.b64encode(value.encode()).decode()
        self.save()

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    @staticmethod
    def validate_and_fix_config(config_data):
        """验证并修复配置数据，返回修复后的配置和错误信息列表"""
        fixed = config_data.copy()
        errors = []

        # 验证和修复 ENDPOINT
        endpoint = fixed.get('ENDPOINT', '').strip()
        if endpoint:
            # 移除末尾的 /
            endpoint = endpoint.rstrip('/')
            # 确保有协议头
            if not endpoint.startswith('http://') and not endpoint.startswith('https://'):
                endpoint = 'https://' + endpoint
            # 优先使用 https
            endpoint = endpoint.replace('http://', 'https://', 1)
            fixed['ENDPOINT'] = endpoint
        else:
            errors.append('ENDPOINT 不能为空')

        # 验证和修复 OSS_DOMAIN
        oss_domain = fixed.get('OSS_DOMAIN', '').strip()
        if oss_domain:
            # 移除末尾的 /
            oss_domain = oss_domain.rstrip('/')
            # 移除协议头（如果有的话）
            if oss_domain.startswith('http://'):
                oss_domain = oss_domain.replace('http://', '', 1)
            if oss_domain.startswith('https://'):
                oss_domain = oss_domain.replace('https://', '', 1)
            fixed['OSS_DOMAIN'] = oss_domain
        else:
            errors.append('OSS_DOMAIN 不能为空')

        # 验证 BUCKET_NAME
        bucket_name = fixed.get('BUCKET_NAME', '').strip()
        if not bucket_name:
            errors.append('BUCKET_NAME 不能为空')
        else:
            fixed['BUCKET_NAME'] = bucket_name

        # 验证 PREFIX - 应该以 / 结尾
        prefix = fixed.get('PREFIX', '').strip()
        if prefix:
            if not prefix.endswith('/'):
                prefix = prefix + '/'
            fixed['PREFIX'] = prefix
        else:
            errors.append('PREFIX 不能为空')

        # 验证 MARKDOWN_PATH - 应该是有效的路径
        markdown_path = fixed.get('MARKDOWN_PATH', '').strip()
        if markdown_path:
            markdown_path = os.path.normpath(markdown_path)
            fixed['MARKDOWN_PATH'] = markdown_path
            if not os.path.exists(markdown_path):
                errors.append(f'Markdown 路径不存在: {markdown_path}')
        else:
            errors.append('MARKDOWN_PATH 不能为空')

        # 验证密钥不为空
        if not fixed.get('ACCESS_KEY_ID', '').strip():
            errors.append('ACCESS_KEY_ID 不能为空')
        if not fixed.get('ACCESS_KEY_SECRET', '').strip():
            errors.append('ACCESS_KEY_SECRET 不能为空')

        return fixed, errors
