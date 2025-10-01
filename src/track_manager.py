from pyncm import apis
import time
from .utils import Utils
from .lyric_manager import LyricManager
from .id_list_manager import IdListManager
from rich import print

class TrackManager:
    def __init__(self):
        self.utils = Utils()
        self.lm = LyricManager()
        self.ilm = IdListManager("track")
        apis.login.LoginViaAnonymousAccount()

    def get_track_info(self, track_id, enable_api, detail_res={}):
        """获取歌曲详细信息"""
        # 获取歌曲详情
        if not detail_res:
            detail_res = self._get_track_detail(track_id)

        # 判断是否为VIP歌曲并获取歌曲音频信息
        if detail_res.get('songs')[0]['fee'] == 1 and enable_api:
            print(f"[bold] {track_id} 为vip歌曲, 使用落月api下载...[/bold]")
            audio_res = self._get_vip_track_audio(track_id)
            try:
                audio_info = audio_res['data']
            except TypeError:
                print(f"[bold red]获取 {track_id} 信息失败! [/bold red]")
                raise ConnectionError

        elif detail_res.get('songs')[0]['fee'] == 1 and not enable_api:
            print(f"[bold] {track_id} 为vip歌曲, 跳过下载...[/bold]")
            return {}

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

    def get_track_list(self):
        """获取歌曲列表"""
        track_ids = self.ilm.read_ids()
        if not track_ids:
            print("[bold red]未找到有效的歌曲ID[/bold red]")
            return []

        tracks, failed = [], []

        for tid in track_ids:
            try:
                track = self.get_track_info(tid)
            except ConnectionError:
                failed.append(track)
            if track:
                tracks.append(track)
            print(f"获取信息: [bold]{len(tracks)}[/bold] 首歌曲")

        return {
        'tracks': tracks,
        'failed': failed
        }

    def search_track(self):
        """搜索歌曲并返回歌曲信息"""
        keyword = input("搜索歌曲或歌手名称:\n")
        if keyword:
            results = apis.cloudsearch.GetSearchResult(keyword, limit=self.utils.config['search']['limit'])['result']['songs']
            print("\n" + "=" * 50)
            for result in results:
                index = results.index(result) + 1
                if result.get('tns'):
                    name_str = f"{result.get('name', "未知歌曲")} ({result.get('tns')[0]})"
                else:
                    name_str = result.get('name', "未知歌曲")
                artists = [ar['name'] for ar in result.get('ar', [])]
                artist_str = '/'.join(artists) if artists else '未知艺术家'
                info = f"{index}. {name_str} - {artist_str}"
                print(info)
            print("0. 退出搜索")
            print("=" * 50)
            print("\n请选择:")
            while True:
                choice = input()
                try:
                    choice = int(choice)
                except Exception:
                    print("[bold]请输入正确的数字! [/bold]")
                else:
                    if choice <= self.utils.config['search']['limit'] and choice >= 1:
                        res = results[choice - 1]
                        return {
                        'songs': [res]
                        }
                    elif choice == 0:
                        return
                    else:
                        print("[bold]请输入正确的数字! [/bold]")

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
                # print(audio_res.json())
                if audio_res.json().get('code') != 200 or not audio_res.json().get('data'):
                    time.sleep(self.utils.config['retry']['delay'])
                    continue
                return audio_res.json()
            except Exception:
                time.sleep(self.utils.config['retry']['delay'])