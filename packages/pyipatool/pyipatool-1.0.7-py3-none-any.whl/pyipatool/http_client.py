import json
import plistlib
import requests

class HTTPClient:
    def __init__(self, cookie_jar):
        self.cookie_jar = cookie_jar
        self.user_agent = "Configurator/2.17 (Macintosh; OS X 15.2; 24C5089c) AppleWebKit/0620.1.16.11.6"
        
        # 创建requests会话
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        
        # 设置最大重定向次数为0，以便手动处理302响应
        self.session.max_redirects = 0
        
        # 加载cookies到会话
        if hasattr(self, 'cookie_jar') and self.cookie_jar and hasattr(self.cookie_jar, 'jar'):
            # 直接使用cookie jar
            self.session.cookies = self.cookie_jar.jar

    def send(self, request):
        url = request["url"]
        method = request["method"]
        
        headers = {}
        if "headers" in request:
            headers.update(request["headers"])
        
        if "User-Agent" not in headers:
            headers["User-Agent"] = self.user_agent

        # 准备请求数据
        payload = request.get("payload")
        data = None
        
        # 检查是否需要发送plist格式数据
        content_type = headers.get("Content-Type", "")
        if content_type == "application/x-apple-plist" and payload:
            # 将payload转换为plist格式
            data = plistlib.dumps(payload)
        else:
            data = payload

        # 发送请求
        try:
            if method == "POST":
                response = self.session.post(url, data=data, headers=headers)
            else:
                response = self.session.get(url, headers=headers, params=payload)
        except requests.exceptions.TooManyRedirects as e:
            # 捕获重定向异常，手动处理
            redirect_url = e.response.headers['location']
            if method == "POST":
                response = self.session.post(redirect_url, data=data, headers=headers)
            else:
                response = self.session.get(redirect_url, headers=headers, params=payload)
        except Exception as e:
            raise

        status_code = response.status_code
        headers = dict(response.headers)
        body_data = response.content

        # 解析响应
        data = None
        if request.get("response_format") == "xml":
            try:
                data = plistlib.loads(body_data)
            except Exception as e:
                data = None
        elif request.get("response_format") == "json":
            try:
                data = json.loads(body_data.decode('utf-8'))
            except Exception as e:
                data = None
        else:
            data = body_data

        # 判断是否需要请求2fa
        if data and isinstance(data, dict) and 'customerMessage'in data and 'BadLogin' in data['customerMessage']:
            payload['attempt'] = str(int(payload['attempt']) + 1)
            auth_code = input("输入收到的2fa:")
            payload['password'] = payload['password'] + auth_code
            response = self.session.post(url, data=payload)
            status_code = response.status_code
            headers = dict(response.headers)
            body_data = response.content


        return {
            "status_code": status_code,
            "headers": headers,
            "data": data
        }