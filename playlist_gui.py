import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.ttk import Combobox
from playlist import add_to_playlist, get_playlist, remove_from_playlist, clear_playlist
from auth import init_session
from music import search_song, download_song, get_song_url
from pyncm.apis.track import GetTrackLyrics
from pyncm.apis import track, cloudsearch
from tkinter import Tk, Label
from PIL import Image, ImageTk
import requests
from io import BytesIO
import json
import webbrowser
from flask import Flask, render_template, jsonify
import threading
import os

app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))

# 全局变量用于存储GUI实例
gui_instance = None

# 全局变量用于存储当前播放信息
current_song_info = {
    'title': '',
    'artist': '',
    'cover_url': '',
    'lyrics': [],
    'progress': 0,
    'duration': 0,
    'is_playing': False
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/song_info')
def get_song_info():
    return jsonify(current_song_info)

@app.route('/api/seek', methods=['POST'])
def seek():
    global gui_instance
    if gui_instance and gui_instance.current_player:
        try:
            data = request.get_json()
            new_time = data.get('time', 0)
            gui_instance.current_player.set_time(new_time)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    return jsonify({'success': False, 'error': 'No player available'})

@app.route('/api/toggle_play', methods=['POST'])
def toggle_play():
    global current_song_info, gui_instance
    if gui_instance and gui_instance.current_player:
        gui_instance.toggle_play_pause()
        return jsonify({'success': True, 'is_playing': current_song_info['is_playing']})
    return jsonify({'success': False, 'error': 'No player available'})

def start_flask():
    try:
        app.run(port=5000, debug=False, host='127.0.0.1')
    except Exception as e:
        print(f"Flask服务器启动失败: {e}")
        messagebox.showerror("错误", "网页播放器启动失败,但不影响基本播放功能")

import playlist
import vlc
import time

class PlaylistGUI:
    def __init__(self):
        global gui_instance
        gui_instance = self
        
        self.window = tk.Tk()
        self.song_data = {}
        # 添加页码相关变量
        self.current_page = 1
        self.songs_per_page = 10
        self.search_results = []  # 存储搜索结果
        self.playlists = {}      # 存储所有歌单
        self.current_playlist = None  # 当前选中的歌单
        self.is_playlist_mode = False  # 控制显示模式
        self.album_page_url = ""
        self.current_player = None
        self.web_player_available = True
        
        # 启动Flask服务器
        try:
            self.flask_thread = threading.Thread(target=start_flask, daemon=True)
            self.flask_thread.start()
        except Exception as e:
            print(f"创建Flask线程失败: {e}")
            self.web_player_available = False
            messagebox.showwarning("警告", "网页播放器启动失败,将使用基本播放功能")
        
        self.setup_window()
        self.setup_menu()  # 添加菜单栏
        self.setup_login()
        self.setup_search_widgets()
        self.setup_pagination_widgets()
        self.setup_progress_bar()
        self.setup_album_widgets()
        self.load_playlist()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_window(self):
        """设置主窗口属性"""
        self.window.title('网易云音乐播放器')
        width = self.window.winfo_screenwidth()
        height = self.window.winfo_screenheight()
        self.window.geometry(f'1000x600+{int(width/2-500)}+{int(height/2-300)}')
        
        # 设置图标和背景
        ico_path = 'C:\\Users\\error\\Desktop\\MUSIC\\Music.ico'
        self.window.iconbitmap(ico_path)
        
        # 设置主题颜色
        self.bg_color = '#2c2c2c'  # 深灰色背景
        self.fg_color = '#ffffff'  # 白色前景
        self.accent_color = '#d13c37'  # 网易云红色
        self.secondary_color = '#363636'  # 次要背景色
        
        self.window.configure(bg=self.bg_color)
        
        # 创建左右分栏布局并设置权重
        self.window.grid_columnconfigure(0, weight=2)  # 左侧占2份
        self.window.grid_columnconfigure(1, weight=1)  # 右侧占1份
        self.window.grid_rowconfigure(0, weight=1)
        
        # 使用grid布局替代pack
        self.left_frame = tk.Frame(self.window, bg=self.bg_color)
        self.left_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        self.right_frame = tk.Frame(self.window, bg=self.bg_color)
        self.right_frame.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)

    def setup_menu(self):
        """设置菜单栏"""
        self.menubar = tk.Menu(self.window)
        self.window.config(menu=self.menubar)
        
        # 创建播放列表菜单
        self.playlist_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="播放列表", menu=self.playlist_menu)
        
        # 添加切换模式选项
        self.playlist_menu.add_command(label="切换到搜索模式", command=lambda: self.toggle_mode(False))
        self.playlist_menu.add_separator()
        
    def setup_login(self):
        """处理登录检查"""
        if init_session():
            messagebox.showinfo("标题", "登录成功")
        else:
            messagebox.showinfo("标题", "登录失败")
            
    def setup_search_widgets(self):
        """设置搜索相关的控件"""
        # 创建搜索框架
        self.search_frame = tk.Frame(self.left_frame, bg=self.bg_color)
        self.search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 搜索输入框和按钮
        self.search_text = tk.StringVar()
        self.search_entry = tk.Entry(self.search_frame, width=30, textvariable=self.search_text)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_button = tk.Button(self.search_frame, text='搜索', command=self.search)
        self.search_button.pack(side=tk.LEFT)
        
        # 添加歌单选择下拉框
        self.playlist_var = tk.StringVar()
        self.playlist_combobox = ttk.Combobox(self.search_frame, textvariable=self.playlist_var, width=20)
        self.playlist_combobox.pack(side=tk.RIGHT)
        self.playlist_combobox.bind('<<ComboboxSelected>>', self.on_playlist_selected)
        
        # 歌曲列表
        self.listbox = tk.Listbox(self.left_frame, bg=self.secondary_color, fg=self.fg_color, 
                                 selectmode=tk.SINGLE, height=15)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind('<Double-Button-1>', lambda event: self.play_selected_song())

    def setup_pagination_widgets(self):
        """设置翻页控件"""
        # 创建翻页按钮框架
        self.page_frame = tk.Frame(self.left_frame, bg=self.bg_color)
        self.page_frame.pack(fill=tk.X, pady=5)
        
        # 上一页按钮
        self.prev_button = tk.Button(self.page_frame, text='上一页', command=self.prev_page)
        self.prev_button.pack(side=tk.LEFT)
        
        # 页码标签
        self.page_label = tk.Label(self.page_frame, text='1', bg=self.bg_color, fg=self.fg_color)
        self.page_label.pack(side=tk.LEFT, padx=10)
        
        # 下一页按钮
        self.next_button = tk.Button(self.page_frame, text='下一页', command=self.next_page)
        self.next_button.pack(side=tk.LEFT)

    def setup_progress_bar(self):
        """设置进度条"""
        # 创建进度条框架
        self.progress_frame = tk.Frame(self.left_frame, bg=self.bg_color)
        self.progress_frame.pack(fill=tk.X, pady=5)
        
        # 创建进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Scale(
            self.progress_frame,
            from_=0,
            to=100,
            orient='horizontal',
            variable=self.progress_var,
            command=self.on_progress_change
        )
        self.progress_bar.pack(fill=tk.X, side=tk.LEFT, expand=True)
        
        # 创建时间标签
        self.time_label = tk.Label(self.progress_frame, text="00:00 / 00:00", 
                                 bg=self.bg_color, fg=self.fg_color)
        self.time_label.pack(side=tk.RIGHT, padx=5)
        
        # 添加播放/暂停按钮
        self.play_pause_button = tk.Button(self.left_frame, text="暂停", 
                                         command=self.toggle_play_pause)
        self.play_pause_button.pack(pady=5)

    def setup_album_widgets(self):
        """设置专辑相关控件"""
        # 设置右侧框架的网格布局
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)
        
        # 创建专辑封面标签，使用grid布局
        self.album_label = tk.Label(self.right_frame, text="无专辑封面", 
                                  bg=self.bg_color, fg=self.fg_color)
        self.album_label.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        # 设置默认图片或占位符
        self.set_default_album_cover()
    
    def set_default_album_cover(self):
        """设置默认专辑封面"""
        # 这里可以创建一个默认的图片，或者使用纯文本
        self.album_label.config(image='', text="无专辑封面")
    
    def get_album_cover_url(self, song_id):
        """获取专辑封面URL"""
        try:
            song_detail = track.GetTrackDetail(song_id)
            album_cover_url = song_detail['songs'][0]['al']['picUrl']
            self.album_page_url = album_cover_url
            print(f"专辑封面URL: {album_cover_url}")
            return album_cover_url
        except Exception as e:
            print(f"获取专辑封面出错: {e}")
            return None
    
    def update_album_cover(self, song_id):
        """更新专辑封面"""
        try:
            album_url = self.get_album_cover_url(song_id)
            if album_url:
                response = requests.get(album_url)
                if response.status_code == 200:
                    image_data = response.content
                    self.album_image = Image.open(BytesIO(image_data))
                    # 调整图片大小为300x300像素
                    self.album_image = self.album_image.resize((300, 300), Image.LANCZOS)
                    tk_image = ImageTk.PhotoImage(self.album_image)
                    self.album_label.config(image=tk_image, text="")
                    self.album_label.image = tk_image  # 保持引用以防止被垃圾回收
                else:
                    self.set_default_album_cover()
            else:
                self.set_default_album_cover()
        except Exception as e:
            print(f"更新专辑封面出错: {e}")
            self.set_default_album_cover()
    
    def play_selected_song(self):
        """播放选中的歌曲"""
        selected_index = self.listbox.curselection()
        if not selected_index:
            messagebox.showinfo("提示", "请选择歌曲")
            return
        
        selected_song = self.listbox.get(selected_index[0])
        song_id = self.song_data[selected_song]
        
        # 更新专辑封面
        self.update_album_cover(song_id)
        
        # 播放歌曲
        self.display_song_info(song_id)

    def display_song_info(self, song_id):
        """显示歌曲信息并播放"""
        url = get_song_url(song_id)
        if not url:
            print("获取URL失败")
            messagebox.showinfo("错误", "获取歌曲URL失败")
            return
        
        # 获取歌曲详细信息
        try:
            song_detail = track.GetTrackDetail(song_id)
            song = song_detail['songs'][0]
            
            # 获取歌词
            lyrics_data = GetTrackLyrics(song_id)
            lyrics = []
            if lyrics_data and 'lrc' in lyrics_data and 'lyric' in lyrics_data['lrc']:
                raw_lyrics = lyrics_data['lrc']['lyric']
                # 解析带时间戳的歌词
                lyrics = []
                for line in raw_lyrics.split('\n'):
                    if line.strip():
                        # 匹配时间戳 [mm:ss.xx]
                        time_start = line.find('[')
                        time_end = line.find(']')
                        if time_start != -1 and time_end != -1:
                            time_str = line[time_start+1:time_end]
                            text = line[time_end+1:].strip()
                            if text:  # 只添加有文本的歌词
                                try:
                                    # 转换时间戳为毫秒
                                    mm, ss = time_str.split(':')
                                    ss, ms = ss.split('.')
                                    timestamp = (int(mm) * 60 + int(ss)) * 1000 + int(ms[:2]) * 10
                                    lyrics.append({'time': timestamp, 'text': text})
                                except:
                                    continue
            
            # 更新全局歌曲信息
            global current_song_info
            current_song_info.update({
                'title': song['name'],
                'artist': song['ar'][0]['name'],
                'cover_url': song['al']['picUrl'],
                'lyrics': lyrics,  # 现在是包含时间戳的歌词数组
                'progress': 0,
                'duration': song['dt'],  # 歌曲总时长(毫秒)
                'is_playing': True
            })
            
            # 打开网页播放器
            webbrowser.open('http://localhost:5000')
            
        except Exception as e:
            print(f"获取歌曲信息失败: {e}")
            return
        
        # 如果有正在播放的实例，先停止
        if hasattr(self, 'current_player') and self.current_player:
            self.current_player.stop()
        
        instance = vlc.Instance()
        player = instance.media_player_new()
        media = instance.media_new(url)
        player.set_media(media)
        
        if not media:
            print("创建媒体对象失败")
            messagebox.showinfo("错误", "创建媒体对象失败")
            return
        
        self.current_player = player
        player.play()
        print("开始播放")
        
        # 给VLC一点时间加载媒体
        time.sleep(1)
        
        # 启动一个更新进度的函数
        self.update_player_progress()
    
    def update_player_progress(self):
        """更新播放进度"""
        if not hasattr(self, 'current_player') or not self.current_player:
            return
        
        if self.current_player.is_playing():
            current_time = self.current_player.get_time()
            total_length = self.current_player.get_length()
            
            if current_time >= 0 and total_length > 0:
                # 更新全局进度信息
                global current_song_info
                current_song_info['progress'] = current_time
                current_song_info['duration'] = total_length
                current_song_info['is_playing'] = True
            
            # 使用after方法进行周期性更新
            self.window.after(100, self.update_player_progress)
        else:
            # 检查是否真的播放结束（而不是暂停）
            state = self.current_player.get_state()
            if state == vlc.State.Ended:
                current_song_info['is_playing'] = False
                current_song_info['progress'] = 0
            else:
                # 如果不是播放结束（可能是暂停），继续检查状态
                self.window.after(100, self.update_player_progress)

    def search(self):
        """搜索歌曲功能"""
        search_text_value = self.search_text.get()
        self.search_results = search_song(search_text_value)
        
        if self.search_results:
            messagebox.showinfo("标题", "搜索成功")
            self.current_page = 1  # 重置页码
            self.update_page_display()  # 更新显示
        else:
            messagebox.showinfo("标题", "搜索失败")
            return

    def update_page_display(self):
        """更新当前页面显示的歌曲"""
        self.listbox.delete(0, tk.END)  # 清空列表
        
        # 计算当前页的歌曲范围
        start_idx = (self.current_page - 1) * self.songs_per_page
        end_idx = start_idx + self.songs_per_page
        current_songs = self.search_results[start_idx:end_idx]
        
        # 显示当前页的歌曲
        for song in current_songs:
            song_info = f'{song["name"]} - {song["ar"][0]["name"]}'
            self.song_data[song_info] = song['id']
            self.listbox.insert('end', song_info)
        
        # 更新页码显示
        self.page_label.config(text=str(self.current_page))
        
        # 更新按钮状态
        total_pages = (len(self.search_results) + self.songs_per_page - 1) // self.songs_per_page
        self.prev_button['state'] = 'normal' if self.current_page > 1 else 'disabled'
        self.next_button['state'] = 'normal' if self.current_page < total_pages else 'disabled'

    def next_page(self):
        """下一页"""
        total_pages = (len(self.search_results) + self.songs_per_page - 1) // self.songs_per_page
        if self.current_page < total_pages:
            self.current_page += 1
            self.update_page_display()

    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_page_display()

    def add_to_playlist(self):
        """添加歌曲到播放列表"""
        selected_index = self.listbox.curselection()
        if selected_index:
            selected_song = self.listbox.get(selected_index[0])
            add_to_playlist(selected_song, self.song_data[selected_song])
            messagebox.showinfo("已添加", f"已添加歌曲: {selected_song} 到播放列表")

    def get_selected_song(self):
        """获取选中的歌曲"""
        selected_index = self.listbox.curselection()
        if selected_index:
            selected_song = self.listbox.get(selected_index[0])
            self.display_song_info(self.song_data[selected_song])
            messagebox.showinfo("已选中", f"Selected song: {selected_song}")
        else:
            messagebox.showinfo("未选中", "No song selected")
            
    def on_closing(self):
        """处理窗口关闭事件"""
        if messagebox.askokcancel("退出", "确定要退出吗?"):
            self.window.destroy()  # 销毁窗口
            self.window.quit()     # 退出主循环
            exit()
            
    def update_progress(self, current_time, total_time):
        """更新进度条和时间显示"""
        # 更新进度条
        progress = (current_time / total_time) * 100 if total_time > 0 else 0
        self.progress_var.set(progress)
        
        # 格式化时间显示
        current_min = int(current_time / 1000 // 60)
        current_sec = int(current_time / 1000 % 60)
        total_min = int(total_time / 1000 // 60)
        total_sec = int(total_time / 1000 % 60)
        
        time_text = f"{current_min:02d}:{current_sec:02d} / {total_min:02d}:{total_sec:02d}"
        self.time_label.config(text=time_text)
        
    def toggle_play_pause(self):
        """切换播放/暂停状态"""
        if not hasattr(self, 'current_player') or not self.current_player:
            return
            
        global current_song_info
        if self.current_player.is_playing():
            self.current_player.pause()
            current_song_info['is_playing'] = False
        else:
            self.current_player.play()
            current_song_info['is_playing'] = True
            
    def on_progress_change(self, value):
        """处理进度条值变化"""
        if not hasattr(self, 'current_player') or not self.current_player:
            return
            
        # 获取总时长
        total_length = self.current_player.get_length()
        if total_length > 0:
            # 计算新的时间位置
            new_time = (float(value) / 100) * total_length
            # 设置新的播放位置
            self.current_player.set_time(int(new_time))
            
    def load_playlist(self):
        """从json文件加载歌单数据"""
        try:
            with open('playlist.json', 'r', encoding='utf-8') as f:
                self.playlists = json.load(f)
                # 更新菜单和下拉框
                self.update_playlist_menu()
        except Exception as e:
            print(f"加载歌单失败: {e}")
            self.playlists = {}
            
    def update_playlist_menu(self):
        """更新歌单菜单和下拉框"""
        # 更新下拉框
        playlist_names = list(self.playlists.keys())
        self.playlist_combobox['values'] = playlist_names
        if playlist_names:
            self.playlist_combobox.set(playlist_names[0])
            
        # 更新菜单
        for name in playlist_names:
            self.playlist_menu.add_command(
                label=name,
                command=lambda n=name: self.switch_to_playlist(n)
            )
            
    def switch_to_playlist(self, playlist_name):
        """切换到指定歌单"""
        self.current_playlist = playlist_name
        self.playlist_var.set(playlist_name)
        self.toggle_mode(True)
        
    def on_playlist_selected(self, event):
        """处理歌单选择事件"""
        selected_playlist = self.playlist_var.get()
        if selected_playlist:
            self.switch_to_playlist(selected_playlist)

    def toggle_mode(self, to_playlist_mode=None):
        """切换显示模式"""
        if to_playlist_mode is not None:
            self.is_playlist_mode = to_playlist_mode
        else:
            self.is_playlist_mode = not self.is_playlist_mode
            
        self.current_page = 1  # 重置页码
        
        if self.is_playlist_mode:
            self.playlist_menu.entryconfig(0, label="切换到搜索模式")
            self.search_entry.config(state='disabled')
            self.search_button.config(state='disabled')
            self.playlist_combobox.config(state='readonly')
            self.update_display()  # 显示歌单
        else:
            self.playlist_menu.entryconfig(0, label="切换到歌单模式")
            self.search_entry.config(state='normal')
            self.search_button.config(state='normal')
            self.playlist_combobox.config(state='disabled')
            self.listbox.delete(0, tk.END)  # 清空列表

    def update_display(self):
        """更新显示内容"""
        if self.is_playlist_mode:
            self.update_playlist_display()
        else:
            self.update_page_display()

    def update_playlist_display(self):
        """更新歌单显示"""
        self.listbox.delete(0, tk.END)  # 清空列表
        
        if not self.current_playlist or self.current_playlist not in self.playlists:
            return
            
        # 获取当前歌单的歌曲
        current_playlist_songs = list(self.playlists[self.current_playlist].items())
        
        # 计算当前页的歌曲范围
        start_idx = (self.current_page - 1) * self.songs_per_page
        end_idx = start_idx + self.songs_per_page
        current_songs = current_playlist_songs[start_idx:end_idx]
        
        # 显示当前页的歌曲
        for song_name, song_id in current_songs:
            self.song_data[song_name] = song_id
            self.listbox.insert('end', song_name)
        
        # 更新页码显示
        self.page_label.config(text=str(self.current_page))
        
        # 更新按钮状态
        total_pages = (len(current_playlist_songs) + self.songs_per_page - 1) // self.songs_per_page
        self.prev_button['state'] = 'normal' if self.current_page > 1 else 'disabled'
        self.next_button['state'] = 'normal' if self.current_page < total_pages else 'disabled'

    def run(self):
        """运行GUI程序"""
        self.window.mainloop()

if __name__ == "__main__":
    app = PlaylistGUI()
    app.run()