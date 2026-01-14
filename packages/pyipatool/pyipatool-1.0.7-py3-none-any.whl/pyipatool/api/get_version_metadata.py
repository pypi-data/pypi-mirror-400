from pyipatool.models import AuthError, App

def get_version_metadata(auth, app_id=None, bundle_id=None, external_version_id=None):
    """
    获取指定版本的应用元数据
    
    Args:
        auth: Auth实例
        app_id: 应用ID，可选
        bundle_id: 应用的bundle ID，可选
        external_version_id: 外部版本ID，必须
        
    Returns:
        App: 应用信息，包含版本元数据
        
    Raises:
        AuthError: 未登录或参数错误时抛出
    """
    account = auth.get_account_info()
    if not account:
        raise AuthError("Not logged in")

    if not external_version_id:
        raise AuthError("External version ID must be specified")

    if not app_id and not bundle_id:
        raise AuthError("Either app ID or bundle ID must be specified")

    if bundle_id:
        from lookup import lookup
        lookup_result = lookup(auth, bundle_id)
        app_id = lookup_result.app.id

    # 获取MAC地址并生成GUID
    mac_addr = auth._get_mac_address()
    guid = mac_addr.replace(":", "").replace("-", "").upper()

    # 构建请求
    base_url = auth.config_manager.get("urls.volume_store_download")
    url = f"{base_url}?guid={guid}"

    payload = {
        "creditDisplay": "",
        "guid": guid,
        "salableAdamId": str(app_id),
        "externalVersionId": external_version_id
    }

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

    # 处理5002错误
    if data and isinstance(data, dict):
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

    # 处理其他错误
    if data and isinstance(data, dict):
        if data.get("failureType") and data.get("customerMessage"):
            raise AuthError(f"Error: {data['customerMessage']}")
        if data.get("failureType"):
            raise AuthError(f"Error: {data['failureType']}")

    # 提取应用信息
    if not data or "songList" not in data or len(data["songList"]) == 0:
        raise AuthError("No app data found")

    item = data["songList"][0]
    metadata = item.get("metadata", {})

    # 构建App对象
    app = App(
        id=app_id,
        name=metadata.get("itemName"),
        version=metadata.get("bundleShortVersionString")
    )

    return app