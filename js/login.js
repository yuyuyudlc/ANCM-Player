// 登录页面的 JavaScript 逻辑

document.addEventListener('DOMContentLoaded', function() {
  const loginForm = document.getElementById('loginForm');
  
  // 添加表单提交事件监听器
  if (loginForm) {
    loginForm.addEventListener('submit', function(event) {
      event.preventDefault();
      
      // 获取表单数据
      const phone = document.getElementById('phone').value;
      const password = document.getElementById('password').value;
      const remember = document.getElementById('remember').checked;
      
      // 表单验证
      if (!phone || !password) {
        showError('请填写所有必填字段');
        return;
      }
      
      // 显示加载状态
      const loginBtn = document.querySelector('.login-btn');
      const originalBtnText = loginBtn.textContent;
      loginBtn.disabled = true;
      loginBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 登录中...';
      
      // 发送登录请求
      fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          phone: phone,
          password: password,
          remember: remember
        }),
      })
      .then(response => response.json())
      .then(data => {
        // 恢复按钮状态
        loginBtn.disabled = false;
        loginBtn.textContent = originalBtnText;
        
        if (data.success) {
          // 登录成功，重定向到主页
          showSuccess('登录成功！');
          document.querySelector('.music-player').style.display = 'none';
          document.querySelector('.container.mt-5').style.display = 'block';
          document.querySelector('.login-container').style.display = 'none';
        } else {
          // 登录失败，显示错误信息
          showError(data.error || '登录失败，请检查您的凭据');
        }
      })
      .catch(error => {
        // 恢复按钮状态
        loginBtn.disabled = false;
        loginBtn.textContent = originalBtnText;
        
        // 显示错误信息
        showError('登录请求失败，请稍后再试');
        console.error('登录错误:', error);
      });
    });
  }
  
  // 添加输入字段动画效果
  const inputFields = document.querySelectorAll('.form-control');
  inputFields.forEach(field => {
    field.addEventListener('focus', function() {
      this.parentElement.classList.add('input-focused');
    });
    
    field.addEventListener('blur', function() {
      if (!this.value) {
        this.parentElement.classList.remove('input-focused');
      }
    });
    
    // 如果字段已有值，添加 focused 类
    if (field.value) {
      field.parentElement.classList.add('input-focused');
    }
  });
});

// 显示错误消息
function showError(message) {
  // 检查是否已存在消息元素
  let messageElement = document.querySelector('.login-message');
  
  if (!messageElement) {
    // 创建消息元素
    messageElement = document.createElement('div');
    messageElement.className = 'login-message';
    
    // 将消息元素插入到表单之前
    const loginForm = document.getElementById('loginForm');
    loginForm.parentNode.insertBefore(messageElement, loginForm);
  }
  
  // 设置消息内容和样式
  messageElement.textContent = message;
  messageElement.className = 'login-message error';
  
  // 添加动画效果
  messageElement.style.animation = 'none';
  setTimeout(() => {
    messageElement.style.animation = 'fadeIn 0.3s ease-out';
  }, 10);
  
  // 5秒后自动隐藏消息
  setTimeout(() => {
    messageElement.style.animation = 'fadeOut 0.3s ease-out forwards';
  }, 5000);
}

// 显示成功消息
function showSuccess(message) {
  // 与 showError 类似，但使用不同的样式
  let messageElement = document.querySelector('.login-message');
  
  if (!messageElement) {
    messageElement = document.createElement('div');
    messageElement.className = 'login-message';
    
    const loginForm = document.getElementById('loginForm');
    loginForm.parentNode.insertBefore(messageElement, loginForm);
  }
  
  messageElement.textContent = message;
  messageElement.className = 'login-message success';
  
  messageElement.style.animation = 'none';
  setTimeout(() => {
    messageElement.style.animation = 'fadeIn 0.3s ease-out';
  }, 10);
  
  setTimeout(() => {
    messageElement.style.animation = 'fadeOut 0.3s ease-out forwards';
  }, 5000);
} 