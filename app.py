from flask import Flask, render_template, jsonify, request
from music import search_song, get_song_url
from flask_cors import CORS
from auth import cookie_login
from playlist_info import get_playlist_songs
import os

app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))
CORS(app)

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
        
        return jsonify({
            'success': True,
            'url': url,
            'song_info': {
                'title': song['name'],
                'artist': song['ar'][0]['name'],
                'cover_url': song['al']['picUrl'],
                'lyrics': lyrics,
                'duration': song['dt']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})



if __name__ == '__main__':
    app.run(port=5000, debug=False, host='127.0.0.1')