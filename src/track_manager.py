from pyncm import apis
import time
from .utils import Utils
from .lyric_manager import LyricManager
from rich import print

class TrackManager:
    def __init__(self):
        self.utils = Utils()
        self.lm = LyricManager()
        apis.login.LoginViaAnonymousAccount()

    def get_track_info(self, track_id):
        """获取歌曲详细信息"""
        # 获取歌曲详情
        detail_res = self._get_track_detail(track_id)

        # 判断是否为VIP歌曲并获取歌曲音频信息
        if detail_res.get('songs')[0]['fee'] == 1:
            print(f"[bold] {track_id} 为vip歌曲, 使用落月api下载...[/bold]")
            audio_res = self._get_vip_track_audio(track_id)
            audio_info = audio_res['data']

        else:
            audio_res = self._get_track_audio(track_id)
            audio_info = audio_res['data'][0]

        song_detail = detail_res['songs'][0]

        # 处理歌曲标签
        tags = self._process_track_tags(song_detail, track_id)

        # 处理专辑封面
        cover_url = song_detail.get('al', {}).get('picUrl', '')

        return {
            'id': track_id,
            'name': tags.get('title'),
            'album': tags.get('album'),
            'url': audio_info.get('url', ''),
            'cover_url': cover_url,
            'tags': tags
        }

    def _process_track_tags(self, song_detail, track_id):
        """处理歌曲标签"""
        # 处理文件名
        name = self.utils.sanitize_filename(song_detail.get('name', '未知歌曲'))
        if self.utils.config['track']['translated_name'] == True:
            try:
                translated_name = song_detail.get('tns')[0]
            except (TypeError, IndexError):
                pass
            else:
                name = self.utils.sanitize_filename(f"{name} ({translated_name})")
        # 处理艺术家信息
        artists = [ar['name'] for ar in song_detail.get('ar', [])]
        artist_str = '/'.join(artists) if artists else '未知艺术家'
        # 处理专辑信息
        album = self.utils.sanitize_filename(song_detail.get('al', {}).get('name', '未知专辑'))
        # 处理发行年份
        publish_time = song_detail.get('publishTime', 0)
        year = time.strftime('%Y', time.localtime(publish_time/1000)) if publish_time else '未知年份'
        # 处理歌词
        lyric = self.lm.get_lyric_info(track_id)
        return {
                'title': name,
                'artist': artist_str,
                'album': album,
                'date': year,
                "lyric": lyric
            }

    def _get_track_detail(self, track_id):
        """获取歌曲详情"""
        for _ in range(self.utils.config['retry']['max_retries']):
            try:
                detail_res = apis.track.GetTrackDetail(track_id)
                if detail_res.get('code') != 200 or not detail_res.get('songs'):
                    continue
                return detail_res
            except Exception:
                time.sleep(self.utils.config['retry']['delay'])

    def _get_track_audio(self, track_id):
        """获取非VIP歌曲音频信息"""
        for _ in range(self.utils.config['retry']['max_retries']):
            try:
                audio_res = apis.track.GetTrackAudio(track_id)
                if audio_res.get('code') != 200 or not audio_res.get('data'):
                    continue
                return audio_res
            except Exception:
                time.sleep(self.utils.config['retry']['delay'])

    def _get_vip_track_audio(self, track_id):
        """获取VIP歌曲音频信息"""
        url = f"https://api.vkeys.cn/v2/music/netease?id={track_id}&quality=4"
        for _ in range(self.utils.config['retry']['max_retries']):
            try:
                audio_res = self.utils.fetch_api_data(url)
                if audio_res.get('code') != 200 or not audio_res.get('data'):
                    continue
                return audio_res
            except Exception:
                time.sleep(self.utils.config['retry']['delay'])