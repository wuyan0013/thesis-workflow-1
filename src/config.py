"""
配置管理模块
负责加载和管理所有配置
"""

import os
from pathlib import Path
from typing import Any, Optional
import yaml
from dotenv import load_dotenv


class Config:
    """配置管理器"""

    def __init__(self, config_path: Optional[str] = None):
        # 加载环境变量（override=True 确保 .env 文件优先于系统环境变量）
        load_dotenv(override=True)

        # 确定配置文件路径
        if config_path is None:
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config" / "config.yaml"

        self._config: dict = {}
        self._load_config(config_path)

    def _load_config(self, config_path: Path) -> None:
        """加载YAML配置文件"""
        config_path = Path(config_path)

        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}
        else:
            # 尝试加载示例配置
            example_path = config_path.parent / "config.example.yaml"
            if example_path.exists():
                with open(example_path, "r", encoding="utf-8") as f:
                    self._config = yaml.safe_load(f) or {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值，支持点号分隔的嵌套键
        例如: config.get("claude.api_key")
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    @property
    def claude_api_key(self) -> str:
        """获取Claude API密钥，优先从环境变量读取"""
        return os.getenv("ANTHROPIC_API_KEY") or self.get("claude.api_key", "")

    @property
    def claude_base_url(self) -> Optional[str]:
        """获取Claude API基础URL（支持代理）"""
        return os.getenv("ANTHROPIC_BASE_URL") or self.get("claude.base_url")

    @property
    def claude_model(self) -> str:
        """获取Claude模型名称，优先从环境变量读取"""
        return os.getenv("CLAUDE_MODEL") or self.get("claude.model", "claude-3-5-sonnet-20241022")

    @property
    def max_tokens(self) -> int:
        """获取最大token数"""
        return self.get("claude.max_tokens", 4096)

    @property
    def output_dir(self) -> Path:
        """获取输出目录"""
        output_path = self.get("output.directory", "./output")
        return Path(output_path)

    @property
    def thesis_config(self) -> dict:
        """获取论文相关配置"""
        return self.get("thesis", {})


# 全局配置实例
_config: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置实例"""
    global _config
    if _config is None:
        _config = Config()
    return _config
