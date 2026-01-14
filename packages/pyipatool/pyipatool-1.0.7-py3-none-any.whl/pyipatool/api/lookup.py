from pyipatool.models import LookupResult, App, AuthError

def lookup(auth, bundle_id):
    """
    通过bundle ID查询应用信息
    
    Args:
        auth: Auth实例
        bundle_id: 应用的bundle ID
        
    Returns:
        LookupResult: 查询结果
        
    Raises:
        AuthError: 未登录或应用不存在时抛出
    """
    account = auth.get_account_info()
    if not account:
        raise AuthError("Not logged in")

    # 获取国家代码
    country_code = auth.country_code_from_store_front(account.store_front) if account.store_front else "US"

    url = auth.config_manager.get("urls.lookup")
    payload = {
        "bundleId": bundle_id,
        "country": country_code
    }

    request = {
        "method": "GET",
        "url": url,
        "payload": payload,
        "response_format": "json"
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

    # 处理重定向响应
    if data and isinstance(data, dict) and "action" in data:
        action = data["action"]
        if action.get("kind") == "Goto" and "url" in action:
            # 提取重定向URL并处理
            redirect_url = action["url"].strip()
            
            # 构建新的请求
            redirect_request = {
                "method": "GET",
                "url": redirect_url,
                "payload": {},  # 重定向URL已经包含了所有参数
                "response_format": "json"
            }
            
            # 发送重定向请求
            redirect_response = auth.http_client.send(redirect_request)
            data = redirect_response["data"]

    if not data or "results" not in data or len(data["results"]) == 0:
        raise AuthError(f"App not found for bundle ID: {bundle_id}")

    item = data["results"][0]
    app = App(
        id=item.get("trackId"),
        bundle_id=item.get("bundleId"),
        name=item.get("trackName"),
        version=item.get("version")
    )

    return LookupResult(app)
