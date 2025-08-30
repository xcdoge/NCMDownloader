from pyncm import apis
from rich import print
from .utils import Utils
import os

class LyricManager:
    def __init__(self):
        self.utils = Utils()
        apis.login.LoginViaAnonymousAccount()
        self.config = self.utils.config['lyric']

    def get_lyric_info(self, track_id):
        """获取歌曲歌词"""
        if self.config['enable'] == False:
            return ""
        res = apis.track.GetTrackLyrics(track_id)
        if res['code'] != 200 or not res:
            print(f"[bold red]获取 {track_id} 歌词失败! [/bold red]")
            return ""
        lrc = self._set_lyric(res)
        return lrc

    def _set_lyric(self, res):
        """处理翻译歌词与罗马音歌词"""
        lrc = res['lrc']['lyric']
        # 处理不存在翻译情况
        try:
            translation = res['tlyric']['lyric']
        except KeyError:
            translation = ""
        # 处理不存在罗马音情况
        try:
            romaji = res['romalrc']['lyric']
        except KeyError:
            romaji = ""
        if self.config['translation'] == True and translation:
            lrc = lrc + "\n" + translation
        if self.config['romaji'] == True:
            lrc = lrc + "\n" + romaji
        return lrc