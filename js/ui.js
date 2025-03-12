// UI相关功能
document.addEventListener('DOMContentLoaded', function() {
    // 处理返回按钮点击事件
    document.querySelector('.back-btn').addEventListener('click', function() {
        console.log('返回按钮被点击'); // 调试信息
        document.querySelector('.music-player').style.display = 'none';
        document.querySelector('.container.mt-5').style.display = 'block';
        document.querySelector('.dynamic-background').style.display = 'none';
        document.querySelector('.toggle-btn').style.display = 'block';
        // 重置背景颜色
        const root = document.documentElement;
        root.style.setProperty('--bg-primary', '#F7EEDD');
        root.style.setProperty('--bg-secondary', '#F7EEDD');
        root.style.setProperty('--text-color', '#000000');
        root.style.setProperty('--text-secondary', '#2c2c2c');
    });

    // 初始化页面显示
    function initializePageDisplay() {
        // 检查URL参数，决定显示哪个页面
        const urlParams = new URLSearchParams(window.location.search);
        const page = urlParams.get('page');
        
        if (page === 'player') {
            document.querySelector('.music-player').style.display = 'flex';
            document.querySelector('.container.mt-5').style.display = 'none';
        } else {
            document.querySelector('.music-player').style.display = 'none';
            document.querySelector('.container.mt-5').style.display = 'block';
        }
    }
    
    // 初始化页面显示
    initializePageDisplay();
    
    // 搜索按钮事件监听
    document.getElementById('searchButton').addEventListener('click', async function() {
        const query = document.getElementById('searchInput').value.trim();
        if (query) {
            const results = await searchSongs(query);
            renderSearchResults(results);
        }
    });
    
    // 搜索框回车事件
    document.getElementById('searchInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const query = this.value.trim();
            if (query) {
                searchSongs(query).then(results => renderSearchResults(results));
            }
        }
    });
    
    // 搜索框输入事件 - 防抖处理
    const debouncedSearch = debounce(async (query) => {
        if (query) {
            const results = await searchSongs(query);
            renderSearchResults(results);
        }
    }, 500);
    
    document.getElementById('searchInput').addEventListener('input', function() {
        const query = this.value.trim();
        if (query) {
            debouncedSearch(query);
        } else {
            // 当搜索框为空时，清空搜索结果
            document.getElementById('searchResults').innerHTML = '';
        }
    });
}); 