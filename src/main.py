from .playlist_manager import PlaylistManager
from .album_manager import AlbumManager
from .track_manager import TrackManager
from .download_manager import DownloadManager
from .lyric_manager import LyricManager
from .id_list_manager import IdListManager
from .utils import Utils
import os
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
            choice =input()
            try:
                choice = int(choice)
            except Exception:
                pass
            else:
                if choice == 1:
                    self.run_playlist()
                elif choice == 2:
                    self.run_list("album")
                elif choice == 3:
                    self.run_track()
                elif choice == 0:
                    break

    def run_list(self, file_type, lists=[], read_file=True):
        """下载列表歌曲主流程"""
        self.ilm = IdListManager(file_type)
        failed = []
        test_res = self.tm._get_vip_track_audio(1345872140)
        enable_api = True
        try:
            test_info = test_res['data']
        except TypeError:
            enable_api = False
            print("[bold red]落月API运行异常, 目前无法下载VIP歌曲![/bold red]")
        if read_file:
            # 检查文件是否有有效内容
            if not self.ilm.read_ids():
                self.utils.create_file(self.utils.config['path'][f'{file_type}_file'])
                self.show_usage_instructions(file_type)
                return

        # 获取所有歌单或专辑
        if not lists:
            if file_type == "playlist":
                lists = self.pm.get_playlist_list()
            elif file_type == "album":
                lists = self.am.get_album_list()
            elif file_type == "track":
                lists = self.tm.get_track_list()
                tracks = lists['tracks']
                failed = lists['failed']
            if not lists:
                return

        if file_type == "track":
            print("\n[bold]开始处理...[/bold]")
            # 创建目录
            list_dir = os.path.join(self.utils.config['path']['download_dir'], f"{file_type}s")
            dir_not_exist = self.utils.create_directory(list_dir)
            track_info = self.filter_exist_tracks(list_dir, track_info, dir_not_exist)
            for track_info in tracks:
                self.dm.download_cover(track_info)
                self.dm.download_track(track_info, "", file_type, enable_api)

        else:
            # 处理每个列表
            for list in lists:
                print(f"\n[bold]开始处理: {list['name']}[/bold]")
                # 创建目录
                list_dir = os.path.join(self.utils.config['path']['download_dir'], f"{file_type}s", list['name'])
                dir_not_exist = self.utils.create_directory(list_dir)
                list['song_ids'] = self.filter_exist_tracks(list_dir, list['song_ids'], dir_not_exist)

                # 处理列表中的每首歌曲
                for track_id in tqdm(list['song_ids'], desc="下载进度"):
                    try:
                        track_info = self.tm.get_track_info(track_id, enable_api)
                    except (ConnectionError, TypeError):
                        failed.append(track_id)
                        continue

                    if not track_info:
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

    def run_playlist(self):
        """下载歌单歌曲主流程"""
        print("\n" + "=" * 50)
        print("请选择下载方式: ")
        print("1. 读取用户歌单并下载")
        print("2. 文件下载")
        print("=" * 50)
        choice =input()
        try:
            choice = int(choice)
        except Exception:
            pass
        else:
            if choice == 1:
                print("请输入用户ID:")
                user_id = input()
                try:
                    user_id = int(user_id)
                except Exception as e:
                    print(e)
                else:
                    playlists_info = self.pm.get_user_playlists(user_id)
                    print("\n" + "=" * 50)
                    for pinfo in playlists_info:
                        order = playlists_info.index(pinfo) + 1
                        info = f"{order}. {pinfo.get("name")}"
                        print(info)
                    print("0. 退出")
                    print("=" * 50)
                    print("\n请选择:")
                    while True:
                        choice = input()
                        try:
                            choice = int(choice)
                        except Exception:
                            print("[bold]请输入正确的数字! [/bold]")
                        else:
                            if choice <= len(playlists_info) and choice >= 1:
                                res = playlists_info[choice - 1]
                                break
                            elif choice == 0:
                                return
                            else:
                                print("[bold]请输入正确的数字! [/bold]")
                    pinfo = [self.pm.get_playlist_info(res["id"])]
                    self.run_list("playlist", pinfo, read_file=False)
                        
            else:
                self.run_list("playlist")

    def run_track(self):
        """下载单首歌曲主流程"""
        print("\n" + "=" * 50)
        print("请选择下载方式: ")
        print("1. 搜索下载")
        print("2. 文件下载")
        print("=" * 50)
        choice =input()
        try:
            choice = int(choice)
        except Exception:
            pass
        else:
            if choice == 1:
                detail_res = self.tm.search_track()
                if detail_res:
                    track_id = detail_res['songs'][0]['id']
                    try:
                        track_info = self.tm.get_track_info(track_id, detail_res)
                    except ConnectionError:
                        return
                    self.dm.download_cover(track_info)
                    self.dm.download_track(track_info, "", "track")

            elif choice == 2:
                self.run_list("track")

    def filter_exist_tracks(self, list_dir, list_info, dir_not_exist):
        """过滤列表中已存在的歌曲"""
        if not dir_not_exist:
            exist_ids = self.utils.exract_dir_ids(list_dir)
            exist_ids = set(exist_ids)
            filtered_list = [
                track for track in list_info if str(track) not in exist_ids
            ]
            if exist_ids:
                print(f"已下载 {len(exist_ids)} 首歌曲, 正在下载剩余 {len(filtered_list)} 首歌曲...")
        return filtered_list


    def show_info(self):
        """显示循环文本"""
        print("\n" + "=" * 50)
        print("[bold]欢迎使用NCMDownloader! [/bold]")
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