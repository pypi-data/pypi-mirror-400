class AuthError(Exception):
    """认证错误"""
    pass

class AuthCodeRequiredError(AuthError):
    """需要验证码错误"""
    pass

class Account:
    """账户信息"""
    def __init__(self, email, name, password_token, directory_services_id, store_front, password=None):
        self.email = email
        self.name = name
        self.password_token = password_token
        self.directory_services_id = directory_services_id
        self.store_front = store_front
        self.password = password

    def to_dict(self):
        return {
            "email": self.email,
            "name": self.name,
            "password_token": self.password_token,
            "directory_services_id": self.directory_services_id,
            "store_front": self.store_front,
            "password": self.password
        }

class App:
    """应用信息"""
    def __init__(self, id=None, bundle_id=None, name=None, version=None):
        self.id = id
        self.bundle_id = bundle_id
        self.name = name
        self.version = version

    def to_dict(self):
        return {
            "id": self.id,
            "bundle_id": self.bundle_id,
            "name": self.name,
            "version": self.version
        }

class SearchResult:
    """搜索结果"""
    def __init__(self, count, results):
        self.count = count
        self.results = results
    
    def __iter__(self):
        """支持直接迭代 SearchResult 对象"""
        return iter(self.results)

class LookupResult:
    """查询结果"""
    def __init__(self, app):
        self.app = app

class ListVersionsResult:
    """版本列表结果"""
    def __init__(self, external_version_identifiers):
        self.external_version_identifiers = external_version_identifiers
