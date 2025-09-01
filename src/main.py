from .playlist_manager import PlaylistManager
from .album_manager import AlbumManager
from .track_manager import TrackManager
from .download_manager import DownloadManager
from .lyric_manager import LyricManager
from .id_list_manager import IdListManager
from .utils import Utils
from tqdm import tqdm
import time
from rich import print

class NCMDownloader:
    def __init__(self):
        self.pm = PlaylistManager()
        self.am = AlbumManager()
        self.tm = TrackManager()
        self.dm = DownloadManager()
        self.lm = LyricManager()
        self.utils = Utils()

    def run(self):
        """程序主流程"""
        while True:
            self.show_info()
            choice =input("")
            try:
                choice = int(choice)
            except Exception:
                pass
            else:
                if choice == 1:
                    self.run_list("playlist")
                elif choice == 2:
                    self.run_list("album")
                elif choice == 3:
                    self.run_track()
                elif choice == 0:
                    break

    def run_list(self, file_type):
        """下载列表歌曲主流程"""
        self.ilm = IdListManager(file_type)
        failed = []
        # 检查文件是否有有效内容
        if not self.ilm.read_ids():
            self.utils.create_file(self.utils.config['path'][f'{file_type}_file'])
            self.show_usage_instructions(file_type)
            return

        # 获取所有歌单或专辑
        if file_type == "playlist":
            lists = self.pm.get_all_playlists()
        elif file_type == "album":
            lists = self.am.get_all_albums()
        if not lists:
            return

        # 处理每个列表
        for list in lists:
            print(f"\n[bold]开始处理: {list['name']}[/bold]")

            # 处理列表中的每首歌曲
            for track_id in tqdm(list['song_ids'], desc="下载进度"):
                track_info = self.tm.get_track_info(track_id)
                if not track_info:
                    print(f"跳过无法获取信息的歌曲: {track_id}")
                    failed.append(track_id)
                    continue

                # 下载封面和歌曲
                if file_type == "album" and track_id != list['song_ids'][0]:
                    pass
                else:
                    self.dm.download_cover(track_info)
                self.dm.download_track(track_info, list['name'], file_type)

                # 避免请求过于频繁
                time.sleep(self.utils.config['download']['request_delay'])

        print("\n[bold green]全部处理完成![/bold green]")

    def run_track(self):
        """下载单首歌曲主流程"""

    def show_info(self):
        """显示循环文本"""
        print("\n" + "=" * 50)
        print("[bold]欢迎使用NCMdownloader! [/bold]")
        print("请选择下载方式: ")
        print("1. 歌单歌曲下载")
        print("2. 专辑歌曲下载")
        print("3. 单曲下载")
        print("0. 退出程序")
        print("=" * 50)

    def show_usage_instructions(self, file_type):
        """显示使用说明"""
        print("\n" + "=" * 50)
        print("[bold]NCMDownloader使用说明[/bold]")
        print("=" * 50)
        print(f"1. 请编辑文件: {self.utils.config['path'][f'{file_type}_file']}")
        print("2. 每行添加一个网易云ID（纯数字，不要包含包括'#'在内的任何其它文字）")
        print("3. 以'#'开头的行被视为注释")
        print("4. 示例:")
        print("   # 我的收藏")
        print("   27182818")
        print("   314159265")
        print("=" * 50)
        print("程序将在您添加有效ID后运行")
        print("=" * 50)