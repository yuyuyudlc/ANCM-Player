import requests
from bs4 import BeautifulSoup
import re
from pyncm.apis import track


def get_playlist_songs():
    url = "https://music.163.com/playlist?id=3136952023"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": open('cookie2.txt').read().strip()
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch the playlist.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    song_list = []
    index = 0
    for song in soup.select("ul.f-hide li a"):
        index += 1
        if index > 18:
            break
        song_name = song.text   
        song_id_match = re.search(r'id=(\d+)', song['href'])
        if song_id_match:
            song_id = song_id_match.group(1)
            # 构造与搜索结果相同格式的数据结构
            # 获取歌曲详细信息
            song_detail = track.GetTrackDetail(song_id)
            if song_detail and 'songs' in song_detail and len(song_detail['songs']) > 0:
                song_info = song_detail['songs'][0]
                song_list.append({
                    'id': song_id,
                    'name': song_info['name'],
                    'ar': song_info['ar'],
                    'al': {'picUrl': song_info['al']['picUrl']}
                })
            else:
                # 如果获取详细信息失败，使用默认值
                song_list.append({
                    'id': song_id,
                    'name': song_name,
                    'ar': [{'name': '未知歌手'}],
                    'al': {'picUrl': 'music.png'}
                })

    return song_list
