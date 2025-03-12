// 格式化时间
function formatTime(ms) {
  const totalSeconds = Math.floor(ms / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

// 防抖函数
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// 更新背景颜色
function updateBackgroundColor(coverUrl) {
  const colorThief = new ColorThief();
  const img = new Image();
  img.src = coverUrl; // 使用新的专辑封面图像
  img.crossOrigin = "Anonymous"; // 允许跨域获取图片数据

  img.onload = function() {
    const dominantColor = colorThief.getColor(img);
    const palette = colorThief.getPalette(img, 2);
    document.documentElement.style.setProperty('--bg-primary', `rgb(${dominantColor[0]}, ${dominantColor[1]}, ${dominantColor[2]})`);
    document.documentElement.style.setProperty('--bg-secondary', `rgb(${palette[1][0]}, ${palette[1][1]}, ${palette[1][2]})`);
  };
} 