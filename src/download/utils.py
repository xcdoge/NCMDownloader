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

    def retry(max_retries, delay, error_msg="操作失败"):
        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                mr = max_retries(self) if callable(max_retries) else max_retries
                de = delay(self) if callable(delay) else delay
                em = error_msg(self, args, kwargs) if callable(error_msg) else error_msg
                for attempt in range(mr):
                    try:
                        result = func(self, *args, **kwargs) # 执行原函数
                        return result
                    except Exception as e:
                        if attempt == mr - 1:
                            print(f"[bold red] {em}（错误：{str(e)}）[/bold red]")
                            return None
                        # 否则重试
                        print(f"[yellow] {em}，重试中...（剩余{mr - attempt - 1}次）[/yellow]")
                        time.sleep(de)
            return wrapper
        return decorator


    @retry(
    max_retries=lambda self: self.config['retry']['max_retries'],  # 用lambda延迟获取self
    delay=lambda self: self.config['retry']['delay'],
    error_msg=lambda self, args, kwargs: f'请求{args[0]}失败'
    )
    def fetch_api_data(self, url, is_json=True):
        """通用API请求函数"""
        res = requests.get(url, headers=self.config['headers'], timeout=10)
        if res.status_code == 200:
            return res.json() if is_json else res


    def sanitize_filename(self, filename):
        """清理文件名中的非法字符"""
        valid_chars = "-_.() %s%s/,，" % (chr(10), chr(13))
        return ''.join(c for c in filename if c.isalnum() or c in valid_chars).strip()


    def _load_config(self):
        current_file_path = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
        config_path = os.path.join(project_root, "config", "config.toml")

        try:
            with open(config_path, "rb") as f:
                config = tomllib.load(f)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"[bold red]配置文件未找到，请检查路径：{config_path}[/bold red]")
        except Exception as e:
            raise RuntimeError(f"[bold red]读取配置文件失败：{e}[/bold red]")

        
        
        
"""        for attempt in range(self.config['retry']['max_retries']):
            try:
                res = requests.get(url, headers=self.config['headers'], timeout=10)
                if res.status_code == 200:
                    return res.json() if is_json else res
            except (requests.RequestException, json.JSONDecodeError) as e:
                print(f"请求{url}失败 ({attempt+1}/{self.config['retry']['max_retries']}): {e}")

            if attempt < self.config['retry']['max_retries'] - 1:
                time.sleep(self.config['retry']['retry_delay'] * (attempt + 1))

        print(f"[bold red]重试{self.config['retry']['max_retries']}次后仍失败: {url}[/bold red]")
        return None"""