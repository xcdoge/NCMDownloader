from pyncm import apis
from rich import print
from .utils import Utils
from .id_list_manager import IdListManager
import os

class PlaylistManager:
    def __init__(self):
        self.utils = Utils()
        self.ilm = IdListManager("playlist")
        apis.login.LoginViaAnonymousAccount()

    def get_playlist_info(self, playlist_id):
        """获取单个歌单相关信息"""
        try:
            playlist_id = int(playlist_id)
        except ValueError:
            print(f"[bold red] {playlist_id} 不是有效的歌单ID, 应为纯数字组合![/bold red]")
            return None

        res = apis.playlist.GetPlaylistInfo(playlist_id)

        if not res or res.get('code') != 200 or not res.get('playlist'):
            print(f"[bold red]获取歌单信息失败: {playlist_id}[/bold red]")
            return None

        song_ids = [track['id'] for track in res['playlist']['trackIds']]
        playlist_name = self.utils.sanitize_filename(res['playlist']['name'])

        return {
            'id': playlist_id,
            'name': playlist_name,
            'song_ids': song_ids
        }

    def get_all_playlists(self):
        """获取所有歌单信息"""
        playlist_ids = self.ilm.read_ids()
        if not playlist_ids:
            print("[bold red]未找到有效的歌单ID[/bold red]")
            return []

        playlists = []

        for pid in playlist_ids:
            playlist = self.get_playlist_info(pid)
            if playlist:
                playlists.append(playlist)
                print(f"获取歌单信息: [bold]{playlist['name']} {len(playlist['song_ids'])}[/bold] 首歌曲")

        return playlists
