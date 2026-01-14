from typing import Union, List, Optional, Dict
from urllib.parse import urlencode

import requests


async def esummary(
        ids: Union[str, List[str], List[int]],
        db: str = "pubmed",
        retstart: int = 1,
        retmax: int = 20,
        retmode: str = "xml",
        version: Optional[str] = "2.0",
        api_key: Optional[str] = None,
        base_url: Optional[str] = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
) -> Dict:
    """
    获取UID对应的文档摘要（DocSum）
    :param db: 目标数据库
    :param ids: UID列表
    :param retstart: 结果起始位置
    :param retmax: 返回结果数量（最大10000）
    :param retmode: 返回格式（xml/json）
    :param version: XML版本（2.0返回详细DocSum）
    :param api_key: NCBI API密钥
    :param base_url: API基础URL
    :return: 解析后的字典结果
    """
    # 校验输入（二选一）
    if not ids:
        raise ValueError("ESummary必须传入ids")

    params = {}
    if api_key:
        params["api_key"] = api_key
    params.update({
        "db": db,
        "retstart": retstart,
        "retmax": min(retmax, 10000),
        "retmode": retmode.lower()
    })
    if isinstance(ids, (list, tuple)):
        ids = ",".join(map(str, ids))
    params["id"] = ids
    if version:
        params["version"] = version

    url = f"{base_url}esummary.fcgi?{urlencode(params)}"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json() if retmode == "json" else resp.text
    except requests.exceptions.RequestException as e:
        raise Exception(f"ESummary请求失败: {str(e)}")
