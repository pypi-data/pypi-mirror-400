from pyipatool.models import ListVersionsResult, AuthError

def list_versions(auth, app_id=None, bundle_id=None):
    """
    查询应用版本列表
    
    Args:
        auth: Auth实例
        app_id: 应用ID，可选
        bundle_id: 应用的bundle ID，可选
        
    Returns:
        ListVersionsResult: 版本列表结果
        
    Raises:
        AuthError: 未登录或参数错误时抛出
    """
    account = auth.get_account_info()
    if not account:
        raise AuthError("Not logged in")

    if not app_id and not bundle_id:
        raise AuthError("Either app ID or bundle ID must be specified")

    if bundle_id:
        from lookup import lookup
        lookup_result = lookup(auth, bundle_id)
        app_id = lookup_result.app.id

    # 获取MAC地址并生成GUID
    mac_addr = auth._get_mac_address()
    guid = mac_addr.replace(":", "").replace("-", "").upper()

    # 按照Go代码逻辑构建请求
    base_url = auth.config_manager.get("urls.volume_store_download")
    url = f"{base_url}?guid={guid}"

    payload = {
        "creditDisplay": "",
        "guid": guid,
        "salableAdamId": str(app_id)
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

    # 提取版本信息
    if not data or "songList" not in data or len(data["songList"]) == 0:
        return ListVersionsResult([])

    item = data["songList"][0]
    if "metadata" not in item:
        return ListVersionsResult([])

    metadata = item["metadata"]
    external_version_identifiers = []

    if "softwareVersionExternalIdentifiers" in metadata:
        raw_identifiers = metadata["softwareVersionExternalIdentifiers"]
        if isinstance(raw_identifiers, list):
            external_version_identifiers = [str(identifier) for identifier in raw_identifiers]

    return ListVersionsResult(external_version_identifiers)
