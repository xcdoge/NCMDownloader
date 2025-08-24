from pyncm import apis
import time
from .utils import Utils
from rich import print

class TrackManager:
    def __init__(self):
        self.utils = Utils()
        apis.login.LoginViaAnonymousAccount()

    def get_track_info(self, track_id):
        """获取歌曲详细信息"""
        # 获取歌曲详情
        detail_res = self._get_track_detail_with_retry(track_id)
        if not detail_res:
            return {}

        song_detail = detail_res['songs'][0]
        is_vip = song_detail.get('fee') == 1

        # 获取歌曲音频信息
        audio_res = self._get_track_audio_with_retry(track_id, is_vip)
        if not audio_res:
            return {}

        # 处理艺术家信息
        artist_str = self._format_artists(song_detail)

        # 处理专辑封面
        cover_url = song_detail.get('al', {}).get('picUrl', '')

        # 处理发行年份
        year = self._get_release_year(song_detail)

        # 处理文件名
        name = self._format_track_name(song_detail)
        album = self.utils.sanitize_filename(song_detail.get('al', {}).get('name', '未知专辑'))

        # 获取音频信息
        audio_info = audio_res['data'][0] if not is_vip else audio_res['data']

        return {
            'id': track_id,
            'name': name,
            'album': album,
            'url': audio_info.get('url', ''),
            'cover_url': cover_url,
            'tags': {
                'title': name,
                'artist': artist_str,
                'album': album,
                'date': year
            }
        }

    def _get_track_detail_with_retry(self, track_id):
        """带重试机制的获取歌曲详情"""
        for _ in range(self.utils.config['retry']['max_retries']):
            try:
                detail_res = apis.track.GetTrackDetail(track_id)
                if detail_res.get('code') == 200 and detail_res.get('songs'):
                    return detail_res
            except Exception:
                time.sleep(self.utils.config['retry']['delay'])
        return None

    def _get_track_audio_with_retry(self, track_id, is_vip):
        """带重试机制的获取歌曲音频信息"""
        for _ in range(self.utils.config['retry']['max_retries']):
            try:
                audio_res = self._get_vip_track_audio(track_id) if is_vip else apis.track.GetTrackAudio(track_id)
                if audio_res.get('code') == 200 and audio_res.get('data'):
                    return audio_res
            except Exception as e:
                print(e)
                time.sleep(self.utils.config['retry']['delay'])
        return None

    def _format_artists(self, song_detail):
        """格式化艺术家信息"""
        artists = [ar['name'] for ar in song_detail.get('ar', [])]
        return '/'.join(artists) if artists else '未知艺术家'

    def _get_release_year(self, song_detail):
        """获取发行年份"""
        publish_time = song_detail.get('publishTime', 0)
        if publish_time:
            return time.strftime('%Y', time.localtime(publish_time/1000))
        return '未知年份'

    def _format_track_name(self, song_detail):
        """格式化歌曲名称"""
        name = self.utils.sanitize_filename(song_detail.get('name', '未知歌曲'))
        if self.utils.config['track']['translated_name']:
            try:
                translated_name = song_detail.get('tns')[0]
                name = self.utils.sanitize_filename(f"{name} ({translated_name})")
            except (TypeError, IndexError):
                pass
        return name

    def _get_vip_track_audio(self, track_id):
        """以落月api作为pyncm获取vip歌曲信息的下位替代"""
        url = f"https://api.vkeys.cn/v2/music/netease?id={track_id}&quality=4"
        return self.utils.fetch_api_data(url)