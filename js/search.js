let searchTimeout;
const searchLoadingIndicator = document.createElement('div');
searchLoadingIndicator.className = 'text-center mt-3 d-none';
searchLoadingIndicator.innerHTML = '<div class="spinner-border text-light" role="status"><span class="visually-hidden">搜索中...</span></div>';

document.addEventListener('DOMContentLoaded', function() {
  document.querySelector('.search-container').appendChild(searchLoadingIndicator);
});

// 搜索歌曲
async function searchSongs(query) {
  try {
    searchLoadingIndicator.classList.remove('d-none');
    const response = await Promise.race([
      fetch(`/api/search?query=${encodeURIComponent(query)}`),
      new Promise((_, reject) => setTimeout(() => reject(new Error('搜索超时')), 10000))
    ]);
    if (!response.ok) {
      throw new Error('搜索请求失败');
    }
    const songs = await response.json();
    return songs;
  } catch (error) {
    console.error('搜索出错:', error);
    return [];
  } finally {
    searchLoadingIndicator.classList.add('d-none');
  }
}

// 渲染搜索结果
function renderSearchResults(songs) {
  const searchResults = document.getElementById('searchResults');
  if (!songs || songs.length === 0) {
    searchResults.innerHTML = '<div class="col-12 text-center"><p>没有找到匹配的歌曲</p></div>';
    return;
  }
  
  searchResults.innerHTML = songs.map(song => `
    <div class="col-md-12">
      <div class="custom-card" data-id="${song.id}">
        <img src="${song.al.picUrl || 'music.png'}" class="card-img-top" alt="${song.name}">
        <div class="card-body">
          <h5 class="card-title">${song.name}</h5>
          <p class="card-text">${song.ar[0].name}</p>
        </div>
      </div>
    </div>
  `).join('');

  // 添加点击事件监听器
  document.querySelectorAll('.custom-card').forEach(card => {
    card.addEventListener('click', async function() {
      const songId = this.dataset.id;
      try {
        const response = await fetch('/api/play', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ id: songId })
        });
        const data = await response.json();
        console.log(data);
        document.querySelector('.toggle-btn').style.display = 'none';
        if (data.success && data.url) {
          // 设置音频源并播放
          audioPlayer.src = data.url;
          audioPlayer.play();
          // 更新UI状态
          playBtn.querySelector('i').className = 'bi bi-pause-circle-fill';
          albumCover.classList.remove('paused');
          // 更新歌曲信息
          const songInfo = data.song_info;
          if (songInfo) {
            console.log(songInfo);
            songTitle.textContent = songInfo.title;
            artistName.textContent = songInfo.artist;
            albumCover.src = songInfo.cover_url;
            bar_songTitle.textContent = songInfo.title;
            bar_artistName.textContent = songInfo.artist;
            bar_albumCover.src = songInfo.cover_url;
            updateBackgroundColor(songInfo.cover_url);
            // 存储歌词数据
            if (songInfo.lyrics) {
              window.currentLyrics = songInfo.lyrics;
              // 初始更新歌词
              updateLyrics(window.currentLyrics, 0);
            }
          }
          // 显示播放器界面
          document.querySelector('.music-player').style.display = 'flex';
          document.querySelector('.container.mt-5').style.display = 'none';
          document.querySelector('.dynamic-background').style.display = 'block';
          const root = document.documentElement;
          root.style.setProperty('--text-color', '#ffffff');
          root.style.setProperty('--text-secondary', '#f0f0f0');
        } else {
          console.error('播放失败:', data.error);
          alert('播放失败，请稍后重试');
        }
      } catch (error) {
        console.error('请求错误:', error);
        alert('播放请求失败，请检查网络连接');
      }
    });
  });
}

// 页面加载时获取并显示歌单数据
document.addEventListener('DOMContentLoaded', async function() {
  try {
    const response = await fetch('/api/playlist');
    if (!response.ok) {
      throw new Error('获取歌单数据失败');
    }
    const songs = await response.json();
    renderSearchResults(songs.map(song => ({
      id: song.id,
      name: song.name,
      ar: [{ name: song.ar[0].name }],
      al: { picUrl: song.al.picUrl || 'music.png' }
    })));
  } catch (error) {
    console.error('获取歌单数据失败:', error);
  }
});