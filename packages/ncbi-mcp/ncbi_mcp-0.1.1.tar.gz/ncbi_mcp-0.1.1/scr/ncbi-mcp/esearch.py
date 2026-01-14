

from typing import Optional, Dict
from urllib.parse import urlencode

import requests


async def esearch(
        term: str,
        db: str = "pubmed",
        retstart: int = 0,
        retmax: int = 20,
        rettype: str = "uilist",
        retmode: str = "xml",
        sort: Optional[str] = None,
        field: Optional[str] = None,
        datetype: Optional[str] = None,
        reldate: Optional[int] = None,
        mindate: Optional[str] = None,
        maxdate: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
) -> Dict:
    """
        文本检索获取UID列表，支持History服务器存储
        :param db: 目标数据库（必填）
        :param term: 检索词（URL编码前的字符串，必填）
        :param retstart: 结果起始位置
        :param retmax: 返回结果数量（最大10000）
        :param rettype: 返回类型（uilist/count）
        :param retmode: 返回格式（xml/json）
        :param sort: 排序方式（如pub_date/relevance）
        :param field: 限定检索字段（如title/author）
        :param datetype: 日期类型（mdat/pdat/edat）
        :param reldate: 最近N天（配合datetype）
        :param mindate/maxdate: 日期范围（YYYY/MM/DD等）
        :param api_key: NCBI API密钥
        :param base_url: API基础URL
        :return: 解析后的字典结果
        """
    # 校验必填参数
    if not term:
        raise ValueError("ESearch必填参数term不能为空")

    params = {}
    if api_key:
        params["api_key"] = api_key  # 单IP每秒>3次请求时添加
    params.update({
        "db": db,
        "term": term,
        "retstart": retstart,
        "retmax": min(retmax, 10000),  # 限制最大值
        "rettype": rettype,
        "retmode": retmode.lower()
    })
    # 可选参数
    if sort:
        params["sort"] = sort
    if field:
        params["field"] = field
    if datetype:
        params["datetype"] = datetype
    if reldate:
        params["reldate"] = reldate
    if mindate:
        params["mindate"] = mindate
    if maxdate:
        params["maxdate"] = maxdate

    url = f"{base_url}esearch.fcgi?{urlencode(params)}"

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json() if retmode == "json" else resp.text
    except requests.exceptions.RequestException as e:
        raise Exception(f"ESearch请求失败: {str(e)}")
