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
        for _ in range(self.utils.config['retry']['max_retries']):
            is_vip = False
            try:
                detail_res = apis.track.GetTrackDetail(track_id)
                if detail_res.get('code') != 200 or not detail_res.get('songs'):
                    continue
                if detail_res.get('songs')[0]['fee'] == 1:
                    print(f" {track_id} 为vip歌曲, 使用落月api下载...")
                    is_vip = True
                break
            except Exception:
                time.sleep(self.utils.config['retry']['retry_delay'])
        
        # 获取歌曲音频信息
        for _ in range(self.utils.config['retry']['max_retries']):
            try:
                if is_vip == False:
                    audio_res = apis.track.GetTrackAudio(track_id)
                else:
                    audio_res = self.get_track_audio(track_id)
                if audio_res.get('code') != 200 or not audio_res.get('data'):
                    continue
                break
            except Exception:
                time.sleep(self.utils.config['retry']['retry_delay'])
        
        song_detail = detail_res['songs'][0]
        
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
        if is_vip == False:
            audio_info = audio_res['data'][0]
        else:
            audio_info = audio_res['data']
        
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

    def get_track_audio(self, track_id):
        """以落月api作为pyncm获取vip歌曲信息的下位替代"""
        url = f"https://api.vkeys.cn/v2/music/netease?id={track_id}&quality=4"
        res = self.utils.fetch_api_data(url)
        return res