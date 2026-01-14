import json
import os

class ConfigManager:
    """配置文件管理类"""
    
    def __init__(self, config_path=None, data_dir=None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
            data_dir: 数据目录路径，如果为None则使用默认路径（包安装目录下的data）
        """
        # 获取包安装目录（pyipatool目录）
        package_dir = os.path.dirname(os.path.abspath(__file__))
        
        if data_dir is None:
            # 默认数据目录路径（包安装目录下的data）
            self.data_dir = os.path.join(package_dir, "data")
        else:
            self.data_dir = data_dir
        
        if config_path is None:
            # 默认配置文件路径
            self.config_path = os.path.join(self.data_dir, "config.json")
        else:
            self.config_path = config_path
        
        # 确保data目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 生成配置文件示例
        self._generate_config_example()
        
        # 加载配置
        self.config = self._load_config()
    
    def _generate_config_example(self):
        """生成配置文件示例"""
        example_path = os.path.join(self.data_dir, "config.json.example")
        
        # 如果示例文件不存在，则生成
        if not os.path.exists(example_path):
            example_config = {
                "auth": {
                    "apple_id": "your_apple_id@example.com",
                    "password": "your_password",
                    "store_front": "143443-2"
                },
                "paths": {
                    "cookies": os.path.join(self.data_dir, "cookies").replace("\\", "/"),
                    "downloads": os.path.join(self.data_dir, "downloads").replace("\\", "/")
                },
                "urls": {
                    "auth": "https://buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/authenticate",
                    "search": "https://itunes.apple.com/search",
                    "lookup": "https://itunes.apple.com/lookup",
                    "volume_store_download": "https://buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/volumeStoreDownloadProduct"
                },
                "download": {
                    "timeout": 300
                },
                "http": {
                    "timeout": 30,
                    "retries": 3
                }
            }
            
            with open(example_path, "w", encoding="utf-8") as f:
                json.dump(example_config, f, indent=2, ensure_ascii=False)
    
    def _load_config(self):
        """
        加载配置文件
        
        Returns:
            dict: 配置数据
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    
                    # 确保URL配置存在
                    if "urls" not in config:
                        config["urls"] = {
                            "auth": "https://buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/authenticate",
                            "search": "https://itunes.apple.com/search",
                            "lookup": "https://itunes.apple.com/lookup",
                            "volume_store_download": "https://buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/volumeStoreDownloadProduct"
                        }
                    
                    return config
            except Exception as e:
                pass
        return {"auth": {}, "urls": {
            "auth": "https://buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/authenticate",
            "search": "https://itunes.apple.com/search",
            "lookup": "https://itunes.apple.com/lookup",
            "volume_store_download": "https://buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/volumeStoreDownloadProduct"
        }}
    
    def _save_config(self):
        """保存配置文件"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get(self, key, default=None):
        """
        获取配置值
        
        Args:
            key: 配置键，支持嵌套键，如 "auth.email"
            default: 默认值
        
        Returns:
            Any: 配置值
        """
        keys = key.split(".")
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key, value):
        """
        设置配置值
        
        Args:
            key: 配置键，支持嵌套键，如 "auth.email"
            value: 配置值
        """
        keys = key.split(".")
        config = self.config
        
        # 遍历到目标键的父级
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
        self._save_config()
    
    def get_auth_config(self):
        """
        获取认证配置
        
        Returns:
            dict: 认证配置
        """
        return self.config.get("auth", {})
    
    def set_auth_config(self, auth_config):
        """
        设置认证配置
        
        Args:
            auth_config: 认证配置字典
        """
        self.config["auth"] = auth_config
        self._save_config()
    
    def clear_auth_config(self):
        """清除认证配置"""
        if "auth" in self.config:
            del self.config["auth"]
            self._save_config()
    
    def get_config_path(self):
        """
        获取配置文件路径
        
        Returns:
            str: 配置文件路径
        """
        return self.config_path