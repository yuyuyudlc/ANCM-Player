from pyncm.apis import track, cloudsearch
from pathlib import Path
import requests
import vlc
import time
from tqdm import tqdm
import pygame

def search_song(keyword):
    """搜索歌曲"""
    try:
        results = cloudsearch.GetSearchResult(keyword, limit=100, offset=0)
        if results['code'] == 200:
            songs = results['result']['songs']
            return songs
        print("搜索失败")
        return None
    except Exception as e:
        print(f"搜索错误: {e}")
        return None

def download_song(url, filename):
    """下载歌曲"""
    try:
        # 创建下载目录
        download_dir = Path("downloads")
        download_dir.mkdir(exist_ok=True)
        
        # 下载文件
        response = requests.get(url, stream=True)
        file_path = download_dir / filename
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"下载成功: {file_path}")
        return True
    except Exception as e:
        print(f"下载失败: {e}")
        return False

def get_song_url(song_id):
    """获取歌曲链接"""
    try:
        result = track.GetTrackAudio(song_id)
        if result['code'] == 200:
            return result['data'][0]['url']
        print("获取歌曲链接失败")
        return None
    except Exception as e:
        print(f"获取链接错误: {e}")
        return None 

def display_song_info(song_id):
    """显示歌曲信息"""
    url=get_song_url(song_id)
    instance = vlc.Instance()
                        # 创建一个媒体播放器
    player = instance.media_player_new()
    # 创建一个媒体对象，传入网络流媒体的 URL
    media = instance.media_new(url)  # 替换为实际的网络流媒体 URL
                        # 将媒体对象设置到播放器
    player.set_media(media)
    player.play()
                        # 等待一段时间，让播放器开始播放
    time.sleep(1)

    
