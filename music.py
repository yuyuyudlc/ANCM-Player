from pyncm.apis import track, cloudsearch

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

    
