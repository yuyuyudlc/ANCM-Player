from flask import Flask, render_template, jsonify, request
from music import search_song, get_song_url
from flask_cors import CORS
from auth import cookie_login
from playlist_info import get_playlist_songs
import os
import vlc

app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))
CORS(app)

# 初始化全局变量
current_song_info = {
    'title': '',
    'artist': '',
    'cover_url': '',
    'lyrics': [],
    'progress': 0,
    'duration': 0,
    'is_playing': False
}

# 添加全局播放器实例
current_player = None

# 尝试使用cookie登录
cookie_login()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/api/search')
def api_search():
    query = request.args.get('query', '')
    if not query:
        return jsonify([])
    
    results = search_song(query)
    if results:
        return jsonify(results)
    return jsonify([])

@app.route('/api/playlist')
def api_playlist():
    songs = get_playlist_songs()
    return jsonify(songs)

@app.route('/api/play', methods=['POST'])
def api_play():
    try:
        global current_player, current_song_info
        data = request.get_json()
        song_id = data.get('id')
        if not song_id:
            return jsonify({'success': False, 'error': '未提供歌曲ID'})
        
        url = get_song_url(song_id)
        if not url:
            return jsonify({'success': False, 'error': '获取歌曲URL失败'})
        
        # 获取歌曲详细信息
        from pyncm.apis import track
        song_detail = track.GetTrackDetail(song_id)
        song = song_detail['songs'][0]
        
        # 获取歌词
        from pyncm.apis.track import GetTrackLyrics
        lyrics_data = GetTrackLyrics(song_id)
        lyrics = []
        if lyrics_data and 'lrc' in lyrics_data and 'lyric' in lyrics_data['lrc']:
            raw_lyrics = lyrics_data['lrc']['lyric']
            for line in raw_lyrics.split('\n'):
                if line.strip():
                    time_start = line.find('[')
                    time_end = line.find(']')
                    if time_start != -1 and time_end != -1:
                        time_str = line[time_start+1:time_end]
                        text = line[time_end+1:].strip()
                        if text:
                            try:
                                mm, ss = time_str.split(':')
                                ss, ms = ss.split('.')
                                timestamp = (int(mm) * 60 + int(ss)) * 1000 + int(ms[:2]) * 10
                                lyrics.append({'time': timestamp, 'text': text})
                            except:
                                continue
        
        # 停止当前播放的音乐（如果有）
        if current_player:
            current_player.stop()
        
        # 创建新的VLC实例和播放器
        instance = vlc.Instance()
        player = instance.media_player_new()
        media = instance.media_new(url)
        player.set_media(media)
        
        # 开始播放
        player.play()
        current_player = player
        
        # 更新全局歌曲信息
        current_song_info.update({
            'title': song['name'],
            'artist': song['ar'][0]['name'],
            'cover_url': song['al']['picUrl'],
            'lyrics': lyrics,
            'progress': 0,
            'duration': song['dt'],
            'is_playing': True
        })
        
        return jsonify({
            'success': True,
            'url': url
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/song_info')
def get_song_info():
    global current_player, current_song_info
    if current_player:
        current_time = current_player.get_time()
        total_length = current_player.get_length()
        if current_time >= 0 and total_length > 0:
            current_song_info['progress'] = current_time
            current_song_info['duration'] = total_length
            # 检查歌曲是否播放完成
            if current_time >= total_length:
                current_song_info['is_playing'] = False
                current_player.stop()
    return jsonify(current_song_info)

@app.route('/api/toggle_play', methods=['POST'])
def toggle_play():
    global current_player, current_song_info
    if current_player:
        if current_song_info['is_playing']:
            current_player.pause()
            current_song_info['is_playing'] = False
        else:
            current_player.play()
            current_song_info['is_playing'] = True
        return jsonify({'success': True, 'is_playing': current_song_info['is_playing']})
    return jsonify({'success': False, 'error': '没有正在播放的歌曲'})

@app.route('/api/stop')
def stop_play():
    global current_player, current_song_info
    if current_player:
        current_player.stop()
        current_song_info['is_playing'] = False
        current_song_info['progress'] = 0
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': '没有正在播放的歌曲'})

@app.route('/api/set_progress', methods=['POST'])
def set_progress():
    global current_player, current_song_info
    try:
        data = request.get_json()
        progress = data.get('progress')
        if not current_player:
            return jsonify({'success': False, 'error': '没有正在播放的歌曲'})
        
        # 设置播放进度（毫秒）
        current_player.set_time(int(progress))
        current_song_info['progress'] = progress
        
        return jsonify({
            'success': True,
            'current_time': progress
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/set_volume', methods=['POST'])
def set_volume():
    global current_player
    try:
        data = request.get_json()
        volume = data.get('volume')
        if not current_player:
            return jsonify({'success': False, 'error': '没有正在播放的歌曲'})
        
        # 设置音量（0-100）
        current_player.audio_set_volume(int(volume))
        
        return jsonify({
            'success': True,
            'volume': volume
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(port=5000, debug=False, host='127.0.0.1')