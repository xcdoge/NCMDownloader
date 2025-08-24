from .playlist_manager import PlaylistManager
from .track_manager import TrackManager
from .download_manager import DownloadManager
from .utils import Utils
from tqdm import tqdm
import time
from rich import print

class NCMDownloader:
    def __init__(self):
        self.playlist_manager = PlaylistManager()
        self.track_manager = TrackManager()
        self.download_manager = DownloadManager()
        self.utils = Utils()

    def run(self):
        """程序主流程"""
        while True:
            self.show_info()
            choice =input("")
            try:
                choice = int(choice)
            except Exception:
                print("请输入正确的选项! ")
            else:
                if choice == 1:
                    self.run_playlist()
                elif choice == 2:
                    self.run_track()
                elif choice == 0:
                    break

        input("点击任意键退出...")



    def run_playlist(self):
        """下载歌单歌曲主流程"""
        failed_playlists = []
        # 检查歌单文件是否有有效内容
        if not self.playlist_manager.read_playlist_ids():
            self.utils.create_file(self.utils.config['path']['playlist_file'])
            self.show_usage_instructions()
            return

        # 获取所有歌单
        playlists = self.playlist_manager.get_all_playlists()
        if not playlists:
            return

        # 处理每个歌单
        for playlist in playlists:
            print(f"\n[bold]开始处理歌单: {playlist['name']}[/bold]")

            # 处理歌单中的每首歌曲
            for track_id in tqdm(playlist['song_ids'], desc="下载进度"):
                track_info = self.track_manager.get_track_info(track_id)
                if not track_info:
                    print(f"跳过无法获取信息的歌曲: {track_id}")
                    failed_playlists.append(track_id)
                    continue

                # 下载封面和歌曲
                self.download_manager.download_cover(track_info, playlist['name'])
                self.download_manager.download_track(track_info, playlist['name'])

                # 避免请求过于频繁
                time.sleep(self.utils.config['download']['request_delay'])

        print("\n[bold green]所有歌单处理完成![/bold green]")

    def run_track(self):
        """下载单首歌曲主流程"""

    def show_info(self):
        """显示循环文本"""
        print("\n" + "=" * 50)
        print("[bold]欢迎使用NCMdownloader! [/bold]")
        print("请选择下载方式: ")
        print("1. 歌单歌曲下载")
        print("2. 单首歌曲下载")
        print("0. 退出程序")
        print("=" * 50)

    def show_usage_instructions(self):
        """显示使用说明"""
        print("\n" + "=" * 50)
        print("[bold]网易云音乐歌单下载器使用说明[/bold]")
        print("=" * 50)
        print(f"1. 请编辑歌单文件: {self.utils.config['path']['playlist_file']}")
        print("2. 每行添加一个网易云歌单ID（纯数字，不要包含包括'#'在内的任何其它文字）")
        print("3. 以'#'开头的行被视为注释")
        print("4. 示例:")
        print("   # 我的收藏歌单")
        print("   123456789")
        print("   987654321")
        print("=" * 50)
        print("程序将在您添加有效歌单ID后运行")
        print("=" * 50)