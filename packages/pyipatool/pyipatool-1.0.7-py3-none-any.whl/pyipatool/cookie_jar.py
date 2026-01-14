import os
import requests

class CookieJar:
    def __init__(self, jar_path=None):
        if jar_path is None:
            # 默认cookies存储路径
            try:
                from pyipatool.config import ConfigManager
                config = ConfigManager()
                config_cookies_dir = config.get("paths.cookies")
                if config_cookies_dir:
                    cookies_dir = config_cookies_dir
                else:
                    # 使用默认数据目录
                    cookies_dir = os.path.join(config.data_dir, "cookies")
            except Exception:
                # 如果无法导入ConfigManager，使用基于当前文件的绝对路径
                package_dir = os.path.dirname(os.path.abspath(__file__))
                cookies_dir = os.path.join(package_dir, "data", "cookies")
            jar_path = os.path.join(cookies_dir, "cookies.txt")
        self.jar_path = jar_path
        
        # 确保目录存在
        os.makedirs(os.path.dirname(jar_path), exist_ok=True)
        
        # 使用requests的RequestsCookieJar
        self.jar = requests.cookies.RequestsCookieJar()
        
        # 加载cookies文件
        if os.path.exists(jar_path):
            try:
                # 读取cookie文件并解析
                with open(jar_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # 解析cookie字符串
                            parts = line.split('; ')
                            if parts:
                                name_value = parts[0].split('=', 1)
                                if len(name_value) == 2:
                                    cookie_dict = {
                                        'name': name_value[0],
                                        'value': name_value[1]
                                    }
                                    # 解析其他cookie属性
                                    for part in parts[1:]:
                                        if '=' in part:
                                            key, val = part.split('=', 1)
                                            # 转换布尔值
                                            if val.lower() in ('true', 'false'):
                                                val = val.lower() == 'true'
                                            # 跳过httponly，因为它不是set()的标准参数
                                            if key.lower() != 'httponly':
                                                cookie_dict[key] = val
                                    # 添加cookie到jar
                                    self.jar.set(**cookie_dict)
            except Exception as e:
                pass

    def save(self):
        if self.jar_path:
            os.makedirs(os.path.dirname(self.jar_path), exist_ok=True)
            try:
                if len(self.jar) > 0:
                    # 保存cookies到文件
                    with open(self.jar_path, 'w') as f:
                        f.write('# Requests Cookies\n')
                        for cookie in self.jar:
                            # 构建cookie字符串
                            cookie_str = f"{cookie.name}={cookie.value}"
                            if cookie.domain:
                                cookie_str += f"; domain={cookie.domain}"
                            if cookie.path:
                                cookie_str += f"; path={cookie.path}"
                            cookie_str += f"; secure={cookie.secure}"
                            cookie_str += f"; httponly={cookie.has_nonstandard_attr('HttpOnly')}"
                            f.write(cookie_str + '\n')
                else:
                    # 如果没有cookies，删除文件（如果存在）
                    if os.path.exists(self.jar_path):
                        os.remove(self.jar_path)
            except Exception as e:
                pass

    def clear(self):
        """清空cookies，包括内存中的cookies和本地文件"""
        try:
            # 清空内存中的cookies
            self.jar.clear()
            
            # 删除本地cookies文件（如果存在）
            if self.jar_path and os.path.exists(self.jar_path):
                os.remove(self.jar_path)
        except Exception as e:
            pass