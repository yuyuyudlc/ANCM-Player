from bs4 import BeautifulSoup

def parse_song_list(html_content):
    """解析HTML内容中的歌曲列表，提取歌曲ID和名称
    Args:
        html_content (str): 包含歌曲列表的HTML内容
    Returns:
        list: 包含歌曲信息的字典列表，每个字典包含id和name字段
    """
    try:
        # 创建BeautifulSoup对象解析HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找所有歌曲链接
        song_links = soup.select('ul.f-hide li a')
        
        # 提取歌曲信息
        songs = []
        for link in song_links:
            # 从href属性中提取歌曲ID
            href = link.get('href', '')
            song_id = href.split('id=')[-1] if 'id=' in href else None
            
            # 获取歌曲名称
            song_name = link.get_text(strip=True)
            
            if song_id and song_name:
                songs.append({
                    'id': song_id,
                    'name': song_name
                })
        
        return songs
    except Exception as e:
        print(f"解析歌曲列表失败: {e}")
        return []