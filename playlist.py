import json
import os
from music import search_song

class Playlist:
    def __init__(self):
        self.playlist_file = "playlist.json"
        if not os.path.exists(self.playlist_file):
            with open(self.playlist_file, "w") as file:
                json.dump({}, file)
    
    def get_all_songs(self):
        """获取播放列表中的所有歌曲"""
        try:
            with open(self.playlist_file, "r") as file:
                playlist_data = json.load(file)
            songs = []
            for i, (name, url) in enumerate(playlist_data.items()):
                songs.append({
                    'id': i,
                    'title': name,
                    'artist': 'Unknown',  # 可以根据需要添加更多信息
                    'url': url
                })
            return songs
        except Exception as e:
            print(f"获取歌曲列表错误: {e}")
            return []
    
    def search_songs(self, query):
        """搜索歌曲"""
        songs = search_song(query)
        if songs:
            print("\n获取到的原始歌曲数据:")
            for song in songs:
                print(json.dumps(song, ensure_ascii=False, indent=2))
            return songs
        return []
    
    def play_song(self, song):
        """播放歌曲"""
        try:
            song_name = song.get('title')
            if not song_name:
                raise ValueError("无效的歌曲信息")
            print(f"正在播放: {song_name}")
            self.current_song = song
            return True
        except Exception as e:
            print(f"播放出错: {e}")
            return False
    
    def get_current_song(self):
        """获取当前播放的歌曲信息"""
        return getattr(self, 'current_song', None)

def add_to_playlist(song_name, song_url):
    playlist_file = "playlist.json"
    playlist_data = {}
    
    # 如果文件存在,先读取现有数据
    if os.path.exists(playlist_file):
        with open(playlist_file, "r") as file:
            playlist_data = json.load(file)
    
    # 添加新歌曲
    if song_name in playlist_data:
        print(f"歌曲 {song_name} 已存在")
        return False
    playlist_data[song_name] = song_url
    # 保存到JSON文件
    with open(playlist_file, "w") as file:
        json.dump(playlist_data, file, indent=4)
    return True

def get_playlist():
    playlist_file = "playlist.json"
    if os.path.exists(playlist_file):
        with open(playlist_file, "r") as file:
            return json.load(file)
    return {}

def remove_from_playlist(song_name):
    playlist_file = "playlist.json"
    if os.path.exists(playlist_file):
        with open(playlist_file, "r") as file:
            playlist_data = json.load(file)
        
        # 如果歌曲存在则删除
        if song_name in playlist_data:
            del playlist_data[song_name]
            
            # 保存更新后的播放列表
            with open(playlist_file, "w") as file:
                json.dump(playlist_data, file, indent=4)
            return True
    return False

def clear_playlist():
    playlist_file = "playlist.json"
    # 创建空的播放列表
    with open(playlist_file, "w") as file:
        json.dump({}, file)

