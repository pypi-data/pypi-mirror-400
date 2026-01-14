from typing import Optional, Union, List, Dict
from urllib.parse import urlencode

import requests


async def efetch(
        ids: Optional[Union[str, List[str], List[int]]],
        db: str = "pubmed",
        retmode: str = "xml",
        rettype: Optional[str] = "abstract",
        retstart: int = 0,
        retmax: int = 20,
        strand: Optional[int] = None,
        seq_start: Optional[int] = None,
        seq_stop: Optional[int] = None,
        complexity: Optional[int] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
) -> Union[str, Dict]:
    """
    获取UID对应的完整格式化记录（核心工具）
    :param db: 目标数据库
    :param ids: UID列表
    :param retmode: 返回格式（xml/text/html/fasta等）
    :param rettype: 返回类型（如abstract/medline/fasta）
    :param retstart: 结果起始位置
    :param retmax: 返回结果数量（最大10000）
    :param strand: DNA链方向（1/2，序列专属）
    :param seq_start/seq_stop: 序列起止位置（序列专属）
    :param complexity: 数据复杂度（0-4，序列专属）
    :param api_key: NCBI API密钥
    :param base_url: API基础URL
    :return: 原始文本（如FASTA）或解析后的字典
    """
    if not ids:
        raise ValueError("EFetch必须传入ids")

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
    if rettype:
        params["rettype"] = rettype
    # 序列专属参数
    if strand:
        params["strand"] = strand
    if seq_start:
        params["seq_start"] = seq_start
    if seq_stop:
        params["seq_stop"] = seq_stop
    if complexity is not None:
        params["complexity"] = complexity

    url = f"{base_url}efetch.fcgi?{urlencode(params)}"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        # 非结构化格式（如fasta/text）返回原始文本，结构化返回解析结果
        if retmode in ["json", "xml"]:
            return resp.json() if retmode == "json" else resp.text
        return resp.text
    except requests.exceptions.RequestException as e:
        raise Exception(f"EFetch请求失败: {str(e)}")