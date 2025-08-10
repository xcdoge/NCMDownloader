from pyncm import apis
import time
from .utils import Utils

class TrackManager:
    def __init__(self):
        self.utils = Utils()
    
    def get_track_info(self, track_id):
        """获取歌曲详细信息"""
        # 获取歌曲详情
        for attempt in range(self.utils.config['retry']['max_retries']):
            try:
                detail_res = apis.track.GetTrackDetail(track_id)
                if detail_res.get('code') != 200 or not detail_res.get('songs'):
                    continue
                break
            except Exception:
                time.sleep(self.utils.config['retry']['retry_delay'])
            else:
                print(f"获取歌曲详情失败: {track_id}")
                return None
        
        # 获取歌曲音频信息
        for attempt in range(self.utils.config['retry']['max_retries']):
            try:
                audio_res = apis.track.GetTrackAudio(track_id)
                if audio_res.get('code') != 200 or not audio_res.get('data'):
                    continue
                break
            except Exception:
                time.sleep(self.utils.config['retry']['retry_delay'])
            else:
                print(f"获取音频信息失败: {track_id}")
                return None
        
        song_detail = detail_res['songs'][0]
        audio_info = audio_res['data'][0]
        
        # 处理艺术家信息
        artists = [ar['name'] for ar in song_detail.get('ar', [])]
        artist_str = '、'.join(artists) if artists else '未知艺术家'
        
        # 处理专辑封面
        cover_url = song_detail.get('al', {}).get('picUrl', '')
        
        # 处理发行年份
        publish_time = song_detail.get('publishTime', 0)
        year = time.strftime('%Y', time.localtime(publish_time/1000)) if publish_time else '未知年份'
        
        # 处理文件名
        name = self.utils.sanitize_filename(song_detail.get('name', f'未知歌曲_{track_id}'))
        album = self.utils.sanitize_filename(song_detail.get('al', {}).get('name', '未知专辑'))
        
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