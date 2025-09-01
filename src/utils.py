import os
import time
import json
import requests
import tomllib
from rich import print
from functools import wraps

class Utils:
    def __init__(self):
        self.config = self._load_config()

    def create_directory(self, path):
        """创建目录(如果不存在)"""
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                print(f"创建目录: {path}")
                return True
            except OSError as e:
                print(f"创建目录 {path} 失败: {e}")
        return False

    def create_file(self, file_path):
        """创建文件(如果不存在)"""
        if not os.path.exists(file_path):
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    pass
                print(f"[bold]创建文件: {file_path}[/bold]")
                return True
            except OSError as e:
                print(f"[bold red]创建文件 {file_path} 失败: {e}[/bold red]")
        return False

    def write_file(self, file_path, content):
        """写入文件"""
        self.create_file(file_path)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def fetch_api_data(self, url, is_json=True):
        """通用API访问函数(无重试机制)"""
        return requests.get(url, headers=self.config['headers'], timeout=10)

    def sanitize_filename(self, filename):
        """清理文件名中的非法字符"""
        valid_chars = "-_.() %s%s,，：:" % (chr(10), chr(13))
        return ''.join(c for c in filename if c.isalnum() or c in valid_chars).strip()


    def _load_config(self):
        current_file_path = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(current_file_path))
        config_path = os.path.join(project_root, "config", "config.toml")

        try:
            with open(config_path, "rb") as f:
                config = tomllib.load(f)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"[bold red]配置文件未找到，请检查路径：{config_path}[/bold red]")
        except Exception as e:
            raise RuntimeError(f"[bold red]读取配置文件失败：{e}[/bold red]")