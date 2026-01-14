import os
from pyipatool.models import App, AuthError

def download(auth, app_id=None, bundle_id=None, output_path="", external_version_id=""):
    """下载应用
    
    Args:
        auth: Auth实例
        app_id (str, optional): 应用ID. Defaults to None.
        bundle_id (str, optional): 应用Bundle ID. Defaults to None.
        output_path (str, optional): 输出路径. Defaults to "".
        external_version_id (str, optional): 外部版本ID. Defaults to "".
        
    Returns:
        str: 下载文件路径
    """
    account = auth.get_account_info()
    if not account:
        raise AuthError("Not logged in")

    if not app_id and not bundle_id:
        raise AuthError("Either app ID or bundle ID must be specified")

    # 获取应用信息
    if bundle_id:
        from lookup import lookup
        lookup_result = lookup(auth, bundle_id)
        app = lookup_result.app
    else:
        # 构建临时App对象
        app = App(id=app_id)

    # 获取MAC地址并生成GUID
    mac_addr = auth._get_mac_address()
    guid = mac_addr.replace(":", "").replace("-", "").upper()

    # 构建下载请求
    base_url = auth.config_manager.get("urls.volume_store_download")
    url = f"{base_url}?guid={guid}"

    payload = {
        "creditDisplay": "",
        "guid": guid,
        "salableAdamId": str(app.id)
    }

    if external_version_id:
        payload["externalVersionId"] = external_version_id

    headers = {
        "Content-Type": "application/x-apple-plist",
        "iCloud-DSID": account.directory_services_id,
        "X-Dsid": account.directory_services_id
    }

    request = {
        "method": "POST",
        "url": url,
        "payload": payload,
        "headers": headers,
        "response_format": "xml"
    }

    response = auth.http_client.send(request)
    data = response["data"]

    # 处理错误响应
    if data and isinstance(data, dict):
        if data.get("failureType") == "passwordTokenExpired":
            raise AuthError("Password token expired")
        if data.get("failureType") == "licenseNotFound":
            raise AuthError("License required")
        if data.get("failureType") == "5002" and data.get("customerMessage"):
            # 遇到5002错误，重试一次
            response = auth.http_client.send(request)
            data = response["data"]
            # 再次检查错误
            if data and isinstance(data, dict):
                if data.get("failureType") and data.get("customerMessage"):
                    raise AuthError(f"Error: {data['customerMessage']}")
                if data.get("failureType"):
                    raise AuthError(f"Error: {data['failureType']}")
        elif data.get("failureType") and data.get("customerMessage"):
            raise AuthError(f"Error: {data['customerMessage']}")
        elif data.get("failureType"):
            raise AuthError(f"Error: {data['failureType']}")

    # 提取下载信息
    if not data or "songList" not in data or len(data["songList"]) == 0:
        raise AuthError("Invalid response")

    item = data["songList"][0]

    # 获取版本信息
    version = "unknown"
    if "metadata" in item:
        metadata = item["metadata"]
        if "bundleShortVersionString" in metadata:
            version = str(metadata["bundleShortVersionString"])

    # 解析目标路径
    destination_path = _resolve_destination_path(app, version, output_path)

    # 下载文件
    download_url = item.get("URL")
    if not download_url:
        raise AuthError("No download URL found")

    temp_path = f"{destination_path}.tmp"
    _download_file(auth, download_url, temp_path)

    # 应用补丁
    _apply_patches(item, account, temp_path, destination_path)

    # 删除临时文件
    if os.path.exists(temp_path):
        os.remove(temp_path)

    return destination_path

def _resolve_destination_path(app, version, output_path):
    """解析目标路径
    
    Args:
        app: App对象
        version: 版本号
        output_path: 输出路径
        
    Returns:
        str: 解析后的目标路径
    """
    # 生成文件名
    file_name = _get_file_name(app, version)

    if not output_path:
        # 默认下载路径
        output_path = "data/downloads"
        try:
            from config import ConfigManager
            config = ConfigManager()
            config_download_dir = config.get("paths.downloads")
            if config_download_dir:
                output_path = config_download_dir
        except Exception:
            pass

    if os.path.isdir(output_path):
        # 确保目录存在
        os.makedirs(output_path, exist_ok=True)
        # 如果是目录，拼接文件名
        return os.path.join(output_path, file_name)

    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # 如果是文件路径，直接使用
    return output_path

def _get_file_name(app, version):
    """生成文件名
    
    Args:
        app: App对象
        version: 版本号
        
    Returns:
        str: 文件名
    """
    parts = []
    if app.bundle_id:
        parts.append(app.bundle_id)
    if app.id:
        parts.append(str(app.id))
    if version:
        parts.append(version)
    if not parts:
        parts.append("app")
    return f"{'-'.join(parts)}.ipa"

def _download_file(auth, url, destination):
    """下载文件
    
    Args:
        auth: Auth实例
        url: 下载URL
        destination: 目标路径
    """
    # 创建目录
    os.makedirs(os.path.dirname(destination), exist_ok=True)

    # 使用requests下载文件
    response = auth.http_client.session.get(url, stream=True)
    response.raise_for_status()

    # 获取文件大小
    total_size = int(response.headers.get('content-length', 0))

    # 下载文件
    downloaded = 0
    chunk_size = 1024 * 1024  # 1MB chunks

    with open(destination, 'wb') as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)

def _apply_patches(item, account, src_path, dst_path):
    """应用补丁
    
    Args:
        item: 下载项信息
        account: 账户信息
        src_path: 源文件路径
        dst_path: 目标文件路径
    """
    import zipfile
    import plistlib

    # 打开源zip文件
    with zipfile.ZipFile(src_path, 'r') as src_zip:
        # 创建目标zip文件
        with zipfile.ZipFile(dst_path, 'w', zipfile.ZIP_DEFLATED) as dst_zip:
            # 复制所有文件
            for file_info in src_zip.infolist():
                if file_info.filename != 'iTunesMetadata.plist':
                    with src_zip.open(file_info) as src_file:
                        dst_zip.writestr(file_info, src_file.read())
            
            # 写入iTunesMetadata.plist
            if "metadata" in item:
                metadata = item["metadata"]
                # 添加账户信息
                metadata["apple-id"] = account.email
                metadata["userName"] = account.email
                
                # 写入plist文件
                plist_data = plistlib.dumps(metadata)
                dst_zip.writestr('iTunesMetadata.plist', plist_data)
