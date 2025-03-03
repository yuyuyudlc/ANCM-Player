from pyncm import GetCurrentSession, SetCurrentSession
from pyncm.apis import login

def cookie_login(cookie_file="cookie.txt"):
    """
    通过 cookie 文件登录
    :return: 登录成功返回 True，失败返回 False
    """
    try:
        # 读取 cookie 文件
        with open(cookie_file, "r") as file:
            cookie_string = file.read().strip()
            cookies = {
                item.split("=")[0]: item.split("=")[1] 
                for item in cookie_string.split("; ")
            }
            
            # 设置会话的 Cookie
            session = GetCurrentSession()
            session.cookies.update(cookies)
            SetCurrentSession(session)
            
            # 验证登录状态
            if "__csrf" in cookies:
                print("Cookie 登录成功！")
                return True
    except FileNotFoundError:
        print("Cookie 文件不存在")
    except Exception as e:
        print(f"Cookie 登录失败: {e}")
    return False

def phone_login(phone, password):
    """
    通过手机号和密码登录
    :return: 登录成功返回 True，失败返回 False
    """
    try:
        response = login.LoginViaCellphone(phone=phone, password=password)
        if response['code'] == 200:
            print("手机号登录成功！")
            
            # 保存 cookie 到文件
            cookies = GetCurrentSession().cookies.get_dict()
            save_cookie(cookies)
            return True
        else:
            print(f"登录失败: {response.get('message', '未知错误')}")
    except Exception as e:
        print(f"登录时发生错误: {e}")
    return False

def save_cookie(cookies, cookie_file="cookie.txt"):
    """
    保存 cookie 到文件
    """
    cookie_string = "; ".join([f"{key}={value}" for key, value in cookies.items()])
    with open(cookie_file, "w") as file:
        file.write(cookie_string)

def init_session():
    """初始化会话，尝试使用保存的 cookies 或手机号登录"""
    # 首先尝试使用 cookie 登录
    if cookie_login():
        return True
    
    # 如果 cookie 登录失败，使用手机号登录
    phone = 19929070870
    password = "20041227abcd"
    return phone_login(phone, password)