import platform
import re
import subprocess
import os


from pyipatool.cookie_jar import CookieJar
from pyipatool.http_client import HTTPClient
from pyipatool.config import ConfigManager

from pyipatool.models import Account


       
class Auth:
    def __init__(self, config_path=None, data_dir=None):
        # 使用ConfigManager管理配置
        self.config_manager = ConfigManager(config_path, data_dir)
        self.config = self.config_manager.config
        
        # 计算cookies目录路径
        try:
            config_cookies_dir = self.config_manager.get("paths.cookies")
            if config_cookies_dir:
                cookies_dir = config_cookies_dir
            else:
                # 使用默认数据目录
                cookies_dir = os.path.join(self.config_manager.data_dir, "cookies")
            jar_path = os.path.join(cookies_dir, "cookies.txt")
            self.cookie_jar = CookieJar(jar_path)
        except Exception:
            # 如果无法获取配置，让CookieJar使用默认路径
            self.cookie_jar = CookieJar()
        self.http_client = HTTPClient(self.cookie_jar)

    def _load_config(self):
        # 使用ConfigManager加载配置
        return self.config_manager.config


    def _get_mac_address(self):
        try:
            if platform.system() == "Windows":
                output = subprocess.check_output("ipconfig /all", shell=True, universal_newlines=True)
                # 使用更精确的正则表达式匹配MAC地址格式
                matches = re.findall(r'Physical Address[^:]+:\s*([0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2})', output)
                if matches:
                    mac = matches[0]
                    return mac
            elif platform.system() == "Darwin":
                output = subprocess.check_output("ifconfig", shell=True, universal_newlines=True)
                matches = re.findall(r'ether\s+([0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2})', output)
                if matches:
                    mac = matches[0]
                    return mac
            elif platform.system() == "Linux":
                output = subprocess.check_output("ifconfig", shell=True, universal_newlines=True)
                matches = re.findall(r'ether\s+([0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2})', output)
                if matches:
                    mac = matches[0]
                    return mac
        except Exception as e:
            pass
        
        # 如果获取失败，使用一个固定的MAC地址格式的字符串
        # 这对于测试和跨平台一致性很重要
        fixed_mac = "00:11:22:33:44:55"
        return fixed_mac

    def login(self, email: str, password: str, auth_code: str = "") -> Account:
        mac_addr = self._get_mac_address()
        # 移除所有分隔符（包括冒号和连字符）并转为大写
        guid = mac_addr.replace(":", "").replace("-", "").upper()
        
        account, err = self._login(email, password, auth_code, guid)
        if err:
            raise err
        
        return account

    def _login(self, email, password, auth_code, guid):

        attempt = 1
        request = self._login_request(email, password, auth_code, guid, attempt)
        response = self.http_client.send(request)

        self.cookie_jar.save()
        data = response["data"]
        store_front = response["headers"]["x-set-apple-store-front"]

        first_name = data.get("accountInfo", {}).get("address", {}).get("firstName", "")
        last_name = data.get("accountInfo", {}).get("address", {}).get("lastName", "")
        name = f"{first_name} {last_name}".strip()
        if not name:
            name = email.split("@")[0].capitalize()

        account = Account(
            email=data.get("accountInfo", {}).get("appleId", email),
            name=name,
            password_token=data.get("passwordToken", ""),
            directory_services_id=data.get("dsPersonId", ""),
            store_front=store_front,
            password=password
        )

        self.config["auth"] = account.to_dict()
        # 使用ConfigManager保存配置
        self.config_manager.set_auth_config(account.to_dict())

        return account, None

    def _login_request(self, email, password, auth_code, guid, attempt):
        payload = {
            "appleId": email,
            "attempt": str(attempt),
            "guid": guid,
            "password": f"{password}{auth_code.replace(' ', '')}",
            "rmp": "0",
            "why": "signIn"
        }

        return {
            "method": "POST",
            "url": self.config_manager.get("urls.auth"),
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            "payload": payload,
            "response_format": "xml"
        }



    def logout(self):
        if "auth" in self.config:
            # 使用ConfigManager清除认证配置
            self.config_manager.clear_auth_config()

    def get_account_info(self):
        if "auth" in self.config and self.config["auth"]:
            auth_data = self.config["auth"]
            return Account(
                email=auth_data.get("email", ""),
                name=auth_data.get("name", ""),
                password_token=auth_data.get("password_token", ""),
                directory_services_id=auth_data.get("directory_services_id", ""),
                store_front=auth_data.get("store_front", ""),
                password=auth_data.get("password")
            )
        return None

    def country_code_from_store_front(self, store_front):
        """根据 storeFront 转换为国家代码"""
        store_fronts = {
            "AE": "143481",
            "AG": "143540",
            "AI": "143538",
            "AL": "143575",
            "AM": "143524",
            "AO": "143564",
            "AR": "143505",
            "AT": "143445",
            "AU": "143460",
            "AZ": "143568",
            "BB": "143541",
            "BD": "143490",
            "BE": "143446",
            "BG": "143526",
            "BH": "143559",
            "BM": "143542",
            "BN": "143560",
            "BO": "143556",
            "BR": "143503",
            "BS": "143539",
            "BW": "143525",
            "BY": "143565",
            "BZ": "143555",
            "CA": "143455",
            "CH": "143459",
            "CI": "143527",
            "CL": "143483",
            "CN": "143465",
            "CO": "143501",
            "CR": "143495",
            "CY": "143557",
            "CZ": "143489",
            "DE": "143443",
            "DK": "143458",
            "DM": "143545",
            "DO": "143508",
            "DZ": "143563",
            "EC": "143509",
            "EE": "143518",
            "EG": "143516",
            "ES": "143454",
            "FI": "143447",
            "FR": "143442",
            "GB": "143444",
            "GD": "143546",
            "GE": "143615",
            "GH": "143573",
            "GR": "143448",
            "GT": "143504",
            "GY": "143553",
            "HK": "143463",
            "HN": "143510",
            "HR": "143494",
            "HU": "143482",
            "ID": "143476",
            "IE": "143449",
            "IL": "143491",
            "IN": "143467",
            "IS": "143558",
            "IT": "143450",
            "IQ": "143617",
            "JM": "143511",
            "JO": "143528",
            "JP": "143462",
            "KE": "143529",
            "KN": "143548",
            "KR": "143466",
            "KW": "143493",
            "KY": "143544",
            "KZ": "143517",
            "LB": "143497",
            "LC": "143549",
            "LI": "143522",
            "LK": "143486",
            "LT": "143520",
            "LU": "143451",
            "LV": "143519",
            "MD": "143523",
            "MG": "143531",
            "MK": "143530",
            "ML": "143532",
            "MN": "143592",
            "MO": "143515",
            "MS": "143547",
            "MT": "143521",
            "MU": "143533",
            "MV": "143488",
            "MX": "143468",
            "MY": "143473",
            "NE": "143534",
            "NG": "143561",
            "NI": "143512",
            "NL": "143452",
            "NO": "143457",
            "NP": "143484",
            "NZ": "143461",
            "OM": "143562",
            "PA": "143485",
            "PE": "143507",
            "PH": "143474",
            "PK": "143477",
            "PL": "143478",
            "PT": "143453",
            "PY": "143513",
            "QA": "143498",
            "RO": "143487",
            "RS": "143500",
            "RU": "143469",
            "SA": "143479",
            "SE": "143456",
            "SG": "143464",
            "SI": "143499",
            "SK": "143496",
            "SN": "143535",
            "SR": "143554",
            "SV": "143506",
            "TC": "143552",
            "TH": "143475",
            "TN": "143536",
            "TR": "143480",
            "TT": "143551",
            "TW": "143470",
            "TZ": "143572",
            "UA": "143492",
            "UG": "143537",
            "US": "143441",
            "UY": "143514",
            "UZ": "143566",
            "VC": "143550",
            "VE": "143502",
            "VG": "143543",
            "VN": "143471",
            "YE": "143571",
            "ZA": "143472",
        }
        
        # 处理 store_front 格式，例如 "143443-2"
        parts = store_front.split("-")
        if len(parts) >= 1:
            store_front_code = parts[0]
            # 查找对应的国家代码
            for country_code, code in store_fronts.items():
                if code == store_front_code:
                    return country_code
        return "US"  # 默认返回 US
