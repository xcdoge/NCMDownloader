from rich import print
from .utils import Utils
import os

class IdListManager:
    def __init__(self, file_type):
        self.utils = Utils()
        self.file_type = file_type
        self.file_path = self.utils.config['path'][f'{self.file_type}_file']

    def has_valid_ids(self):
        """检查文件中是否有有效ID"""
        ids = self.read_ids()
        if not ids:
            print("\n[bold red]错误: 文件中没有有效的ID[/bold red]")
            return False
        return True

    def read_ids(self):
        """获取ID列表"""
        if not os.path.exists(self.file_path):
            print(f"[bold red]错误: 文件不存在 - {self.file_path}[/bold red]")
            return []

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except Exception as e:
            print(f"[bold red]读取文件时出错: {str(e)}[/bold red]")
            return []