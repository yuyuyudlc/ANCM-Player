// 全局变量
const audioPlayer = document.getElementById('audioPlayer');
const albumCover = document.getElementById('albumCover');
const songTitle = document.querySelector('.song-title');
const artistName = document.querySelector('.artist-name');
const progressBarEl = document.querySelector('.progress-bar');
const currentTime = document.querySelector('.time-info span:first-child');
const totalTime = document.querySelector('.time-info span:last-child');
const lyrics = document.querySelector('.lyrics');
const playBtn = document.querySelector('.play-btn');
const progressBar = document.querySelector('.progress');
const volumeSlider = document.querySelector('.volume-slider');
const lyricsToggle = document.querySelector('.lyrics-toggle');
const playerMain = document.querySelector('.player-main');
const lyricsContainer = document.querySelector('.lyrics-container');
const bar_songTitle = document.querySelector('.bar-now-playing-title');
const bar_albumCover = document.getElementById('bar-albumCover');
const bar_artistName = document.querySelector('.bar-now-playing-artist');



let isPlaying = false; // 播放状态
let lastActiveIndex = -1; // 上一个高亮的歌词索引
let pr_flag = 0;

// 更新歌词
function updateLyrics(lyricsArray, currentTime) {
  if (!lyricsArray || lyricsArray.length === 0) {
    lyrics.innerHTML = '<div class="lyric-line">暂无歌词</div>';
    return;
  }
  
  // 清空现有歌词
  lyrics.innerHTML = '';
  
  // 找到当前应该显示的歌词
  let activeIndex = -1;
  for (let i = 0; i < lyricsArray.length; i++) {
    if (lyricsArray[i].time > currentTime) {
      activeIndex = i - 1;
      break;
    }
  }
  if (activeIndex === -1 && currentTime >= lyricsArray[lyricsArray.length - 1].time) {
    activeIndex = lyricsArray.length - 1;
  }
  
  // 创建并添加歌词行
  lyricsArray.forEach((line, index) => {
    const div = document.createElement('div');
    div.textContent = line.text;
    div.className = 'lyric-line';
    
    // 设置当前行和附近行的样式
    if (index === activeIndex) {
      div.classList.add('active');
    } else if (Math.abs(index - activeIndex) <= 2) {
      div.classList.add('nearby');
    }
    
    lyrics.appendChild(div);
  });
  
  // 滚动到当前歌词
  if (activeIndex !== -1 && activeIndex !== lastActiveIndex) {
    const activeElement = lyrics.children[activeIndex];
    if (activeElement) {
      activeElement.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
      });
    }
    lastActiveIndex = activeIndex; // 更新上一个高亮的歌词索引
  }
}

// 播放控制
playBtn.addEventListener('click', async function() {
  if (!audioPlayer.src) return;
  if (audioPlayer.paused) {
    await audioPlayer.play();
    playBtn.querySelector('i').className = 'bi bi-pause-circle-fill';
    albumCover.classList.remove('paused');
  } else {
    audioPlayer.pause();
    playBtn.querySelector('i').className = 'bi bi-play-circle-fill';
    albumCover.classList.add('paused');
  }
});

// 进度条控制
progressBar.addEventListener('click', function(e) {
  const rect = this.getBoundingClientRect();
  const percent = (e.clientX - rect.left) / rect.width;
  audioPlayer.currentTime = percent * audioPlayer.duration;
});

// 音量控制
volumeSlider.addEventListener('input', function() {
  audioPlayer.volume = this.value / 100;
});

// 更新进度
audioPlayer.addEventListener('timeupdate', function() {
  const progress = (audioPlayer.currentTime / audioPlayer.duration) * 100;
  progressBarEl.style.width = `${progress}%`;
  currentTime.textContent = formatTime(audioPlayer.currentTime * 1000);
  totalTime.textContent = formatTime(audioPlayer.duration * 1000);
  // 更新歌词
  if (window.currentLyrics) {
    updateLyrics(window.currentLyrics, audioPlayer.currentTime * 1000);
  }
});

// 播放结束处理
audioPlayer.addEventListener('ended', function() {
  playBtn.querySelector('i').className = 'bi bi-play-circle-fill';
  albumCover.classList.add('paused');
});

// 歌词显示切换
lyricsToggle.addEventListener('click', () => {
  playerMain.classList.toggle('show-lyrics');
  lyricsContainer.classList.toggle('show');
  lyricsToggle.classList.toggle('active');
});

// 监听专辑封面更换事件
albumCover.addEventListener('load', () => {
  updateBackgroundColor(albumCover.src);
});