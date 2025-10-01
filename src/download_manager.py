import os
from rich import print
from .utils import Utils
from .tag_manager import TagManager

class DownloadManager:
    def __init__(self):
        self.utils = Utils()

    def get_file_extension(self, url):
        """从URL获取文件扩展名"""
        if '?' in url:
            url = url.split('?')[0]
        if '.' in url:
            ext = url.split('.')[-1].lower()
            if ext in ['mp3', 'flac', 'm4a', 'wav']:
                return ext
        return 'mp3'  # 默认扩展名

    def download_file(self, url, file_path):
        """下载文件到指定路径"""
        if os.path.exists(file_path):
            print(f"[bold]文件已存在，跳过: {os.path.basename(file_path)}[/bold]")
            return True

        res = self.utils.fetch_api_data(url, is_json=False)
        if not res:
            return False

        try:
            with open(file_path, 'wb') as f:
                for chunk in res.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        except Exception as e:
            print(f"[bold red]下载失败: {file_path} - {e}[/bold red]")
            return False

    def download_track(self, track_info, list_name, file_type, index=""):
        """下载单首歌曲"""
        if not track_info or not track_info.get('url'):
            print(f"[bold red]无有效歌曲URL: {track_info.get('name') if track_info else '未知歌曲'}[/bold red]")
            return False

        # 创建目录
        if list_name:
            list_dir = os.path.join(self.utils.config['path']['download_dir'], f"{file_type}s", list_name)
        else:
            list_dir = os.path.join(self.utils.config['path']['download_dir'], f"{file_type}s")
        self.utils.create_directory(list_dir)

        # 下载歌曲
        ext = self.get_file_extension(track_info['url'])
        if index:
            file_name = f"{index}. {track_info['name']} {track_info['id']}.{ext}"
        else:
            file_name = f"{track_info['name']} {track_info['id']}.{ext}"
        file_path = os.path.join(list_dir, file_name)

        if not self.download_file(track_info['url'], file_path):
            return False
        # 设置音频标签
        if os.path.exists(file_path):
            tag_manager = TagManager(file_path, track_info['tags'])
            tag_manager.set_audio_tags()

        return True

    def download_cover(self, track_info):
        """下载歌曲封面"""
        if not track_info or not track_info.get('cover_url'):
            print(f"[bold red]无有效封面URL: {track_info.get('name') if track_info else '未知歌曲'}[/bold red]")
            return False

        # 创建封面目录
        cover_dir = self.utils.config['path']['cover_dir']
        if self.utils.create_directory(cover_dir):
            pass

        # 下载封面
        cover_ext = track_info['cover_url'].split('.')[-1].split('?')[0].lower()
        if cover_ext not in ['jpg', 'jpeg', 'png']:
            cover_ext = 'jpg'

        file_name = f"{track_info['album'] if track_info['album'] else track_info['name']}.{cover_ext}"
        file_path = os.path.join(cover_dir, file_name)
        return self.download_file(track_info['cover_url'], file_path)

