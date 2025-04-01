import jmcomic
import os
from common import EmailConfig
from ...config_manager import GlobalConfig


class JMServer:
    _option = None
    _option_loaded = False

    @classmethod
    def load_config(cls, env: str = "local"):
        if cls._option_loaded:
            return
        config_file = {
            "local": "localjmopt.yml",
            "remote": "remotejmopt.yml"
        }.get(env, "localjmopt.yml")

        config_path = os.path.join(os.path.dirname(__file__), f'../../resources/{config_file}')

        try:
            if cls._option is None:
                cls._option = jmcomic.create_option_by_file(config_path)
                cls._option_loaded = True
        except FileNotFoundError:
            raise FileNotFoundError("JMComic config file not found")

    @classmethod
    def download_photo(cls, comic_id):
        try:
            download_path = cls._option.dir_rule.base_dir
            if not os.path.exists(f"{download_path}/{comic_id}.pdf"):
                jmcomic.download_photo(comic_id, cls._option)
        except Exception as e:
            raise Exception(f"Failed to download photo: {e}")

    @classmethod
    def get_download_path(cls):
        return JMServer._option.dir_rule.base_dir


def init_JMServer(env: str):
    JMServer.load_config(env)


if __name__ == "__main__":
    init_JMServer("local")
    print(JMServer._option)
