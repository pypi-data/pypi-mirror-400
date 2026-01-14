"""
pyipatool - Apple App Store search and download tool
"""

__version__ = "1.0.6"
__author__ = "pjp"
__email__ = "pjp385334338@gmail.com"

from .api import API
from .models import SearchResult, Account, LookupResult, ListVersionsResult, AuthError

def login(email: str, password: str, auth_code: str = "") -> Account:
    """
    登录App Store，方便其他Python项目直接引用
    
    Args:
        email: Apple ID邮箱
        password: 密码
        auth_code: 2FA验证码，可选
        
    Returns:
        Account: 账户信息
        
    Raises:
        AuthError: 登录失败时抛出
    """
    api = API()
    return api.login(email, password, auth_code)

def logout():
    """
    登出App Store，方便其他Python项目直接引用
    """
    api = API()
    return api.logout()

def get_account_info() -> Account:
    """
    获取账户信息，方便其他Python项目直接引用
    
    Returns:
        Account: 账户信息，未登录时返回None
    """
    api = API()
    return api.get_account_info()

def search(term, limit=5) -> SearchResult:
    """
    搜索应用，方便其他Python项目直接引用
    
    Args:
        term: 搜索关键词
        limit: 结果数量限制，默认为5
        
    Returns:
        SearchResult: 搜索结果
        
    Raises:
        AuthError: 未登录时抛出
    """
    api = API()
    return api.search(term, limit)

def lookup(bundle_id) -> LookupResult:
    """
    通过bundle ID查询应用信息，方便其他Python项目直接引用
    
    Args:
        bundle_id: 应用的bundle ID
        
    Returns:
        LookupResult: 查询结果
        
    Raises:
        AuthError: 未登录或应用不存在时抛出
    """
    api = API()
    return api.lookup(bundle_id)

def list_versions(app_id=None, bundle_id=None) -> ListVersionsResult:
    """
    查询应用版本列表，方便其他Python项目直接引用
    
    Args:
        app_id: 应用ID，可选
        bundle_id: 应用的bundle ID，可选
        
    Returns:
        ListVersionsResult: 版本列表结果
        
    Raises:
        AuthError: 未登录或参数错误时抛出
    """
    api = API()
    return api.list_versions(app_id, bundle_id)

def download(app_id=None, bundle_id=None, output_path="", external_version_id="") -> str:
    """
    下载应用，方便其他Python项目直接引用
    
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
    api = API()
    return api.download(app_id, bundle_id, output_path, external_version_id)

# 导出API类，方便高级使用
from .api import API as ApiClient