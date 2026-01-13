#!/usr/bin/env python
# pylint: disable=E0401,W0718

"""
Coding: UTF-8
Author: Bitliker
Date: 2025/12/30
Version: 1.0.0
Description: WMA 文件处理器 (ASF)
"""

from typing import List
from mutagen.asf import ASF, ASFByteArrayAttribute
from .base import BaseHandler
from ..metadata import AudioMetadata


class WMAHandler(BaseHandler):
    """WMA 文件处理器 (ASF 容器)"""

    # ASF 标准属性名映射
    TITLE = "Title"
    ARTIST = "Author"
    ALBUM = "WM/AlbumTitle"
    ALBUM_ARTIST = "WM/AlbumArtist"
    YEAR = "WM/Year"
    GENRE = "WM/Genre"
    TRACK_NUMBER = "WM/TrackNumber"
    DISC_NUMBER = "WM/PartOfSet"
    COMPOSER = "WM/Composer"
    COMMENT = "Description"
    LYRICS = "WM/Lyrics"
    PICTURE = "WM/Picture"

    def load(self) -> None:
        self._file = ASF(self.filepath)

    def read(self) -> AudioMetadata:
        tags = self._file.tags
        if tags is None:
            return AudioMetadata()

        track_num, total_tracks = self._parse_track_number(
            self._get_first_value(tags.get(self.TRACK_NUMBER))
        )
        disc_num, total_discs = self._parse_disc_number(
            self._get_first_value(tags.get(self.DISC_NUMBER))
        )

        # 获取封面
        artwork = None
        pictures = tags.get(self.PICTURE)
        if pictures:
            for pic in pictures:
                if isinstance(pic.value, bytes):
                    artwork = self._parse_wm_picture(pic.value)
                    if artwork:
                        break

        # 获取流派列表
        genre = self._parse_genre(tags.get(self.GENRE))

        return AudioMetadata(
            title=self._get_first_value(tags.get(self.TITLE)),
            artist=self._get_first_value(tags.get(self.ARTIST)),
            album=self._get_first_value(tags.get(self.ALBUM)),
            album_artist=self._get_first_value(tags.get(self.ALBUM_ARTIST)),
            year=self._get_first_value(tags.get(self.YEAR)),
            genre=genre,
            track_number=track_num,
            total_tracks=total_tracks,
            disc_number=disc_num,
            total_discs=total_discs,
            lyrics=self._get_first_value(tags.get(self.LYRICS)),
            composer=self._get_first_value(tags.get(self.COMPOSER)),
            comment=self._get_first_value(tags.get(self.COMMENT)),
            artwork=artwork,
        )

    def _parse_genre(self, genre_values) -> List[str]:
        """解析流派标签"""
        if genre_values is None:
            return []
        genres = []
        for genre in genre_values:
            genres.append(str(genre))
        return genres

    def _parse_wm_picture(self, data: bytes) -> bytes:
        """解析 WM/Picture 数据，提取图片数据

        WM/Picture 格式:
        - 1 byte: picture type
        - 4 bytes: data length (little-endian)
        - null-terminated UTF-16LE mime type
        - null-terminated UTF-16LE description
        - picture data
        """
        if not data or len(data) < 5:
            return None
        try:
            # 跳过 picture type (1 byte) 和 data length (4 bytes)
            offset = 5

            # 跳过 mime type (null-terminated UTF-16LE)
            while offset < len(data) - 1:
                if data[offset] == 0 and data[offset + 1] == 0:
                    offset += 2
                    break
                offset += 2

            # 跳过 description (null-terminated UTF-16LE)
            while offset < len(data) - 1:
                if data[offset] == 0 and data[offset + 1] == 0:
                    offset += 2
                    break
                offset += 2

            # 剩余的就是图片数据
            if offset < len(data):
                return data[offset:]
        except Exception:
            pass
        return None

    def _create_wm_picture(self, image_data: bytes, mime: str = "image/jpeg") -> bytes:
        """创建 WM/Picture 数据

        Args:
            image_data: 图片二进制数据
            mime: MIME 类型

        Returns:
            WM/Picture 格式的二进制数据
        """
        # picture type: 3 = front cover
        picture_type = b'\x03'
        # data length (little-endian)
        data_length = len(image_data).to_bytes(4, 'little')
        # mime type (UTF-16LE, null-terminated)
        mime_bytes = mime.encode('utf-16-le') + b'\x00\x00'
        # description (UTF-16LE, null-terminated, empty)
        desc_bytes = b'\x00\x00'

        return picture_type + data_length + mime_bytes + desc_bytes + image_data

    def write(self, metadata: AudioMetadata) -> None:
        tags = self._file.tags

        if metadata.title is not None:
            tags[self.TITLE] = metadata.title
        if metadata.artist is not None:
            tags[self.ARTIST] = metadata.artist
        if metadata.album is not None:
            tags[self.ALBUM] = metadata.album
        if metadata.album_artist is not None:
            tags[self.ALBUM_ARTIST] = metadata.album_artist
        if metadata.year is not None:
            tags[self.YEAR] = str(metadata.year)
        if metadata.genre:
            tags[self.GENRE] = list(metadata.genre)
        if metadata.composer is not None:
            tags[self.COMPOSER] = metadata.composer
        if metadata.comment is not None:
            tags[self.COMMENT] = metadata.comment
        if metadata.lyrics is not None:
            tags[self.LYRICS] = metadata.lyrics

        # 音轨号
        if metadata.track_number is not None:
            track_str = str(metadata.track_number)
            if metadata.total_tracks is not None:
                track_str += f'/{metadata.total_tracks}'
            tags[self.TRACK_NUMBER] = track_str

        # 碟片号
        if metadata.disc_number is not None:
            disc_str = str(metadata.disc_number)
            if metadata.total_discs is not None:
                disc_str += f'/{metadata.total_discs}'
            tags[self.DISC_NUMBER] = disc_str

        # 封面
        if metadata.artwork is not None:
            picture_data = self._create_wm_picture(metadata.artwork)
            tags[self.PICTURE] = [ASFByteArrayAttribute(data=picture_data)]

    def save(self) -> None:
        self._file.save()
