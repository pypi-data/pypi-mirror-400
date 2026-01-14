from pyipatool.models import SearchResult, App, AuthError

def search(auth, term, limit=5):
    """
    搜索应用
    
    Args:
        auth: Auth实例
        term: 搜索关键词
        limit: 结果数量限制，默认为5
        
    Returns:
        SearchResult: 搜索结果
        
    Raises:
        AuthError: 未登录时抛出
    """
    account = auth.get_account_info()
    if not account:
        raise AuthError("Not logged in")

    # 获取国家代码
    country_code = auth.country_code_from_store_front(account.store_front) if account.store_front else "US"

    # 使用iTunes Search API v2，它返回JSON格式
    url = auth.config_manager.get("urls.search")
    payload = {
        "term": term,
        "media": "software",
        "entity": "software",
        "limit": str(limit),
        "country": country_code,
        "lang": "en_us"
    }

    request = {
        "method": "GET",
        "url": url,
        "payload": payload,
        "response_format": "json"
    }

    response = auth.http_client.send(request)
    
    data = response["data"]

    if not data:
        return SearchResult(0, [])

    results = []
    count = 0

    if "results" in data:
        for item in data["results"]:
            app = App(
                id=item.get("trackId"),
                bundle_id=item.get("bundleId"),
                name=item.get("trackName"),
                version=item.get("version"),
                price=item.get("price")
            )
            results.append(app)
            count += 1

    return SearchResult(count, results)
