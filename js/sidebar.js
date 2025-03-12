// 侧边栏功能
document.addEventListener('DOMContentLoaded', function() {
    // 侧边栏切换
    const toggleBtn = document.querySelector('.toggle-btn');
    const sidebar = document.querySelector('.sidebar');
    
    toggleBtn.addEventListener('click', function() {
        sidebar.classList.toggle('active');
        toggleBtn.style.display = 'none';
    });

    // 点击页面其他区域关闭侧边栏
    document.addEventListener('click', function(e) {
        if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target) && sidebar.classList.contains('active')) {
            sidebar.classList.remove('active');
            toggleBtn.style.display = 'block';
        }
    });

    // 导航功能
    document.querySelector('.home-link').addEventListener('click', function(e) {
        e.preventDefault();
        // 显示主页内容
        document.querySelector('.container.mt-5').style.display = 'block';
        document.querySelector('.music-player').style.display = 'none';
        toggleBtn.style.display = 'block';
        sidebar.classList.remove('active');
    });

    document.querySelector('.search-link').addEventListener('click', function(e) {
        e.preventDefault();
        // 显示搜索界面
        document.querySelector('.container.mt-5').style.display = 'block';
        document.querySelector('.music-player').style.display = 'none';
        document.querySelector('#searchInput').focus();
        sidebar.classList.remove('active');
        toggleBtn.style.display = 'block';
    });

    // 播放列表下拉菜单切换
    const playlistLink = document.querySelector('.playlist-link');
    const submenu = document.querySelector('.submenu');
    
    if (playlistLink && submenu) {
        // 初始隐藏子菜单
        submenu.style.display = 'none';
        
        playlistLink.addEventListener('click', function(e) {
            e.preventDefault();
            // 切换子菜单显示状态
            submenu.style.display = submenu.style.display === 'none' ? 'block' : 'none';
            // 切换箭头方向
            const arrow = this.querySelector('.bi-chevron-down');
            if (arrow) {
                arrow.classList.toggle('bi-chevron-down');
                arrow.classList.toggle('bi-chevron-up');
            }
        });
    }

    // 播放列表选择
    document.querySelectorAll('.submenu a').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const playlistType = this.dataset.playlist;
            // 这里可以根据不同的播放列表类型加载相应的内容
            console.log('加载播放列表:', playlistType);
            
            // 加载对应的播放列表（这里需要实现具体的加载逻辑）
            loadPlaylist(playlistType);
            
            // 关闭侧边栏
            sidebar.classList.remove('active');
        });
    });
});

// 加载播放列表函数
function loadPlaylist(playlistType) {
    // 根据播放列表类型加载不同的内容
    let apiEndpoint = '';
    
    switch(playlistType) {
        case 'liked':
            apiEndpoint = '/api/playlist/liked';
            break;
        case 'recent':
            apiEndpoint = '/api/playlist/recent';
            break;
        case 'custom':
            apiEndpoint = '/api/playlist/custom';
            break;
        default:
            apiEndpoint = '/api/playlist';
    }
    
    // 显示加载中提示
    const searchResults = document.getElementById('searchResults');
    searchResults.innerHTML = '<div class="col-12 text-center"><p>加载中...</p></div>';
    
    // 显示搜索界面
    document.querySelector('.container.mt-5').style.display = 'block';
    document.querySelector('.music-player').style.display = 'none';
    
    // 发送请求获取播放列表数据
    fetch(apiEndpoint)
        .then(response => {
            if (!response.ok) {
                throw new Error('获取播放列表失败');
            }
            return response.json();
        })
        .then(songs => {
            // 使用搜索结果渲染函数来显示播放列表
            if (typeof renderSearchResults === 'function') {
                renderSearchResults(songs);
            } else {
                console.error('renderSearchResults 函数未定义');
            }
        })
        .catch(error => {
            console.error('获取播放列表失败:', error);
            searchResults.innerHTML = '<div class="col-12 text-center"><p>加载播放列表失败，请稍后重试</p></div>';
        });
}