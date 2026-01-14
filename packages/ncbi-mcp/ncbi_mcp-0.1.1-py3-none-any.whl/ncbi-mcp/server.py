from typing import List, Union
from os import getenv
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP

from einfo import einfo
from esearch import esearch
from esummary import esummary
from efetch import efetch

# 加载环境变量
load_dotenv()
API_KEY = getenv("API_KEY")
BASE_URL = getenv("BASE_URL", "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/")

mcp_server = FastMCP(name="mcp-for-ncbi")


@mcp_server.tool(description="如无要求，返回所有数据库名称；如指定数据库，则返回该数据库的详细信息。",
                 title="查询ncbi数据库")
async def EInfo(db_name: str):
    return await einfo(db=db_name, api_key=API_KEY, base_url=BASE_URL)


@mcp_server.tool(
    description="term为要查询项，db为要查询的库，如不提供db，则默认在pubmed库中查找。返回结果为所在库的id，进一步获取需调用其他tool。",
    title="查询相关内容的id")
async def ESearch(db_name: str, term: str):
    return await esearch(db=db_name, term=term, api_key=API_KEY, base_url=BASE_URL)


@mcp_server.tool(
    description="ids为要查询项的id，db为要查询的库，如不提供db，则默认在pubmed库中查找。返回结果为所在库的summary。",
    title="查询相关内容的Summary")
async def ESummary(db_name: str, ids: Union[str, List[str], List[int]]):
    return await esummary(db=db_name, ids=ids, api_key=API_KEY, base_url=BASE_URL)


@mcp_server.tool(
    description="ids为要查询项的id，db为要查询的库，如不提供db，则默认在pubmed库中查找。返回结果为所在库的完整记录。",
    title="查询相关内容的完整记录")
async def EFetch(db_name: str, ids: Union[str, List[str], List[int]], retmode: str = "xml", rettype: str = "abstract"):
    return await efetch(ids=ids, db=db_name, retmode=retmode, rettype=rettype, api_key=API_KEY, base_url=BASE_URL)


def main():
    mcp_server.run(transport="stdio")


if __name__ == "__main__":
    main()
