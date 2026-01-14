
# 导入功能模块
from .auth import Auth
from .search import search
from .lookup import lookup
from .list_version import list_versions
from .download import download

from pyipatool.models import Account, SearchResult, LookupResult, ListVersionsResult

class API:
    def __init__(self, config_path=None, data_dir=None):
        """
        初始化API实例
        
        Args:
            config_path: 配置文件路径，默认为None，将使用默认路径
            data_dir: 数据目录路径，默认为None，将使用包安装目录下的data
        """
        self.auth = Auth(config_path, data_dir)
    
    def login(self, email: str, password: str, auth_code: str = "") -> Account:
        """
        登录App Store
        
        Args:
            email: Apple ID邮箱
            password: 密码
            auth_code: 2FA验证码，可选
            
        Returns:
            Account: 账户信息
            
        Raises:
            AuthError: 登录失败时抛出
        """
        return self.auth.login(email, password, auth_code)
    
    def logout(self):
        """
        登出App Store
        """
        self.auth.logout()
    
    def get_account_info(self) -> Account:
        """
        获取账户信息
        
        Returns:
            Account: 账户信息，未登录时返回None
        """
        return self.auth.get_account_info()
    
    def search(self, term, limit=5) -> SearchResult:
        """
        搜索应用
        
        Args:
            term: 搜索关键词
            limit: 结果数量限制，默认为5
            
        Returns:
            SearchResult: 搜索结果
            
        Raises:
            AuthError: 未登录时抛出
        """
        return search(self.auth, term, limit)
    
    def lookup(self, bundle_id) -> LookupResult:
        """
        通过bundle ID查询应用信息
        
        Args:
            bundle_id: 应用的bundle ID
            
        Returns:
            LookupResult: 查询结果
            
        Raises:
            AuthError: 未登录或应用不存在时抛出
        """
        return lookup(self.auth, bundle_id)
    
    def list_versions(self, app_id=None, bundle_id=None) -> ListVersionsResult:
        """
        查询应用版本列表
        
        Args:
            app_id: 应用ID，可选
            bundle_id: 应用的bundle ID，可选
            
        Returns:
            ListVersionsResult: 版本列表结果
            
        Raises:
            AuthError: 未登录或参数错误时抛出
        """
        return list_versions(self.auth, app_id, bundle_id)
    
    def download(self, app_id=None, bundle_id=None, output_path="", external_version_id="") -> str:
        """
        下载应用
        
        Args:
            app_id: 应用ID，可选
            bundle_id: 应用的bundle ID，可选
            output_path: 输出路径，可选
            external_version_id: 外部版本ID，可选
            
        Returns:
            str: 下载文件的路径
            
        Raises:
            AuthError: 未登录或参数错误时抛出
        """
        return download(self.auth, app_id, bundle_id, output_path, external_version_id)
