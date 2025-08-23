from mutagen.flac import FLAC, Picture
from mutagen.mp3 import EasyMP3
from mutagen.id3 import ID3, APIC
from mutagen.mp4 import MP4, MP4Cover
import os

class TagManager:
    def __init__(self, file_path, tags):
        self.file_path = file_path
        self.tags = tags

    def _get_cover_path(self):
        """获取有效的封面路径（优先查找jpg、jpeg、png格式）"""
        cover_dir = os.path.join(os.path.dirname(self.file_path), 'covers')
        album_name = self.tags.get('album')
        if not album_name or not os.path.exists(cover_dir):
            return None

        # 可能的图片后缀，按优先级排序
        possible_exts = ['jpg', 'jpeg', 'png']
        for ext in possible_exts:
            cover_path = os.path.join(cover_dir, f"{album_name}.{ext}")
            if os.path.exists(cover_path):
                return cover_path
        return None

    def _get_image_info(self, cover_path):
        """通过后缀名获取图片MIME类型和格式"""
        ext = os.path.splitext(cover_path)[1].lower().lstrip('.')
        if ext in ['jpg', 'jpeg']:
            return 'image/jpeg', 'jpeg'
        elif ext == 'png':
            return 'image/png', 'png'
        else:
            raise ValueError(f"不支持的图片格式: {ext}")

    def set_audio_tags(self):
        """为音频文件设置元数据标签和封面"""
        ext = os.path.splitext(self.file_path)[1].lower()

        try:
            if ext == '.mp3':
                self._set_mp3_tags()
            elif ext in ('.m4a', '.mp4'):
                self._set_m4a_tags()
            elif ext == '.flac':
                self._set_flac_tags()
            else:
                raise ValueError(f"不支持的文件格式: {ext}")
            return True
        except Exception as e:
            print(f"✗ 处理失败 {os.path.basename(self.file_path)}: {str(e)}")
            return False

    def _set_mp3_tags(self):
        # 处理文本标签
        audio = EasyMP3(self.file_path)

        # 只更新提供的标签
        if 'title' in self.tags:
            audio['title'] = self.tags['title']
        if 'artist' in self.tags:
            audio['artist'] = self.tags['artist']
        if 'album' in self.tags:
            audio['album'] = self.tags['album']
        if 'date' in self.tags:
            audio['date'] = self.tags['date']
        if 'genre' in self.tags:
            audio['genre'] = self.tags['genre']
        if 'tracknumber' in self.tags:
            audio['tracknumber'] = self.tags['tracknumber']
        audio.save()

        # 处理封面图片
        cover_path = self._get_cover_path()
        if not cover_path:
            return

        try:
            audio = ID3(self.file_path)
        except:
            audio = ID3()

        mime, _ = self._get_image_info(cover_path)
        with open(cover_path, 'rb') as f:
            audio['APIC'] = APIC(
                encoding=3,  # UTF-8
                mime=mime,
                type=3,  # 封面图片
                desc='Cover',
                data=f.read()
            )
        audio.save(v2_version=3)  # 兼容更多播放器

    def _set_m4a_tags(self):
        audio = MP4(self.file_path)

        # MP4标签映射
        tag_map = {
            'title': '\xa9nam',
            'artist': '\xa9ART',
            'album': '\xa9alb',
            'date': '\xa9day',
            'genre': '\xa9gen',
            'tracknumber': 'trkn',
            'comment': '\xa9cmt'
        }

        # 特殊处理轨道号
        if 'tracknumber' in self.tags:
            try:
                track_num = self.tags['tracknumber'].split('/')[0]
                total_tracks = self.tags['tracknumber'].split('/')[1] if '/' in self.tags['tracknumber'] else None
                if total_tracks:
                    audio[tag_map['tracknumber']] = [(int(track_num), int(total_tracks))]
                else:
                    audio[tag_map['tracknumber']] = [(int(track_num), 0)]
            except (ValueError, IndexError):
                pass

        # 处理其他标签
        for key, mp4_key in tag_map.items():
            if key in self.tags and key != 'tracknumber':
                audio[mp4_key] = self.tags[key]

        # 添加封面
        cover_path = self._get_cover_path()
        if not cover_path:
            audio.save()
            return

        _, img_format = self._get_image_info(cover_path)
        with open(cover_path, 'rb') as f:
            mp4_format = MP4Cover.FORMAT_JPEG if img_format == 'jpeg' else MP4Cover.FORMAT_PNG
            cover = MP4Cover(f.read(), imageformat=mp4_format)
        audio['covr'] = [cover]

        audio.save()

    def _set_flac_tags(self):
        audio = FLAC(self.file_path)

        # 文本标签
        for tag in ['title', 'artist', 'album', 'date', 'genre', 'comment']:
            if tag in self.tags:
                audio[tag] = self.tags[tag]

        # 特殊处理轨道号
        if 'tracknumber' in self.tags:
            audio['tracknumber'] = self.tags['tracknumber']

        # 添加封面
        cover_path = self._get_cover_path()
        if not cover_path:
            audio.save()
            return

        mime, _ = self._get_image_info(cover_path)

        # 删除现有封面
        for pic in audio.pictures:
            if pic.type == 3:  # 封面图片
                audio.remove_picture(pic)

        image = Picture()
        image.type = 3  # 封面图片
        image.mime = mime
        image.desc = 'Cover'
        with open(cover_path, 'rb') as f:
            image.data = f.read()

        audio.add_picture(image)
        audio.save()
