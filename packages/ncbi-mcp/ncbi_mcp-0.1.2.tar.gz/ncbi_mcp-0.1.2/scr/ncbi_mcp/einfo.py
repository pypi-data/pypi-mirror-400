from typing import Optional, Dict
from urllib.parse import urlencode
import requests


async def einfo(
        db: Optional[str] = None,
        retmode: str = "xml",
        api_key: Optional[str] = None,
        base_url: Optional[str] = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
) -> Dict:
    """
    获取Entrez数据库列表或单个数据库的统计信息
    :param db: 目标数据库（如pubmed/protein），None则返回所有数据库
    :param retmode: 返回格式（xml/json）
    :param api_key: NCBI API密钥
    :param base_url: API基础URL
    :return: 解析后的字典结果
    """
    params = {}
    if api_key:
        params["api_key"] = api_key  # 单IP每秒>3次请求时添加
    if db:
        params["db"] = db
    params["retmode"] = retmode.lower()

    url = f"{base_url}einfo.fcgi?{urlencode(params)}"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json() if retmode == "json" else resp.text
    except requests.exceptions.RequestException as e:
        raise Exception(f"EInfo请求失败: {str(e)}")
