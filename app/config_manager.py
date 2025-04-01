import os
import yaml
from pathlib import Path
from typing import Dict, Any



class GlobalConfig:
    _config: Dict[str, Any] = None
    _config_loaded = False
    _env = os.getenv("env", "local")

    def __new__(cls, *args, **kwargs):
        # 禁用实例化，强制使用类方法
        raise TypeError("GlobalConfig cannot be instantiated")
    @classmethod
    def load_config(cls, env: str = "local"):
        if cls._config_loaded and env == cls._env:
            return

        config_file = {
            "local": "localconfig.yml",
            "remote": "remoteconfig.yml"
        }.get(env, "localconfig.yml")

        config_path = Path(__file__).parent / "resources" / config_file

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                cls._config = yaml.safe_load(f) or {}
                cls._config["runtime_env"] = env
                cls._env = env
                cls._config_loaded = True
        except FileNotFoundError:
            raise RuntimeError(f"Config file {config_file} not found")
        except yaml.YAMLError as e:
            raise RuntimeError(f"Error parsing YAML: {str(e)}")

    @classmethod
    def get(cls, key: str, default=None):
        return cls._config.get(key, default) if cls._config else default

    @classmethod
    def get_all(cls):
        return cls._config.copy() if cls._config else {}




# 使用示例
if __name__ == "__main__":
    # 通常从命令行参数或环境变量获取
    GlobalConfig.load_config('local')
    print(GlobalConfig.get_all())
    print(GlobalConfig.get("smtp")["file_path"])
