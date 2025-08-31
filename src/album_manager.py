from pyncm import apis
from rich import print
from .utils import Utils
from .id_list_manager import IdListManager
import os

class AlbumManager:
    def __init__(self):
        self.utils = Utils()
        self.ilm = IdListManager("album")
        apis.login.LoginViaAnonymousAccount()

    def get_album_info(self, album_id):
        """获取单个专辑相关信息"""
        try:
            album_id = int(album_id)
        except ValueError:
            print(f"[bold red] {album_id} 不是有效的专辑ID, 应为纯数字组合![/bold red]")
            return None

        res = apis.album.GetAlbumInfo(album_id)

        if not res or res.get('code') != 200 or not res.get('songs'):
            print(f"[bold red]获取专辑信息失败: {album_id}[/bold red]")
            return None

        song_ids = [_['id'] for _ in res['songs']]
        album_name = self.utils.sanitize_filename(res['album']['name'])

        return {
            'id': album_id,
            'name': album_name,
            'song_ids': song_ids
        }

    def get_all_albums(self):
        """获取所有专辑信息"""
        album_ids = self.ilm.read_ids()
        if not album_ids:
            print("[bold red]未找到有效的专辑ID[/bold red]")
            return []

        albums = []

        for pid in album_ids:
            album = self.get_album_info(pid)
            if album:
                albums.append(album)
                print(f"获取专辑信息: [bold]{album['name']} {len(album['song_ids'])}[/bold] 首歌曲")

        return albums