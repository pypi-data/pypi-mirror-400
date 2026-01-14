# NCBI E-utilities MCP 服务器

用于访问 NCBI E-utilities API 的MCP服务器。该包提供对 NCBI 数据库（包括 PubMed、Protein、Nucleotide 等）的程序化访问。

## 功能特性

- **EInfo**: 获取 Entrez 数据库列表或特定数据库的统计信息
- **ESearch**: 基于文本的搜索，从 NCBI 数据库检索 UID 列表
- **ESummary**: 检索指定 UID 的文档摘要（DocSum）
- **EFetch**: 获取指定 UID 的完整格式化记录（核心功能）

## 连接到您的 MCP 客户端

您可以使用uvx命令从本地 MCP 客户端连接到您的 NCBI MCP 服务器。

要从 Claude Desktop 或其他兼容 MCP 的客户端连接到您的 MCP 服务器，请按照 MCP 客户端设置指南并更新客户端配置。

使用以下配置更新您的 MCP 客户端配置：

```json
{
  "mcpServers": {
    "ncbi-mcp": {
      "command": "uvx",
      "args": [
        "ncbi-mcp"
      ],
      "env": {
        "API_KEY": "YOUR_NCBI_API_KEY"
      }
    }
  }
}
```
**注意**: 不提供 API 密钥时，您的请求被限制为每秒最多 3 次。提供 API 密钥后，您可以每秒发出多达 10 个请求。

### 获取 NCBI API 密钥

要获取 NCBI API 密钥，您需要：

1. 在 [https://www.ncbi.nlm.nih.gov/account/](https://www.ncbi.nlm.nih.gov/account/) 注册 NCBI 账户
2. 前往您的账户"设置"页面
3. 找到"API 密钥管理"区域并点击"创建 API 密钥"
4. 复制生成的密钥并在您的 `.env` 文件中使用

有关 NCBI API 密钥的更多信息，请访问：[https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/)

## 可用工具

### EInfo
- 描述：查询 NCBI 数据库，获取数据库统计信息
- 参数：db_name（可选），retmode（默认：xml）

### ESearch
- 描述：在指定数据库中按术语搜索内容
- 参数：db_name（默认：pubmed），term（搜索查询）

### ESummary
- 描述：获取指定 ID 的摘要信息
- 参数：db_name（默认：pubmed），ids（ID 列表）

### EFetch
- 描述：获取指定 ID 的完整记录
- 参数：db_name（默认：pubmed），ids（ID 列表），retmode（默认：xml），rettype（默认：abstract）

## 环境变量

服务器会自动从环境变量中获取以下配置：

- `API_KEY`: NCBI API 密钥（推荐用于提高请求限制）

## 要求

- Python >= 3.12
- NCBI API 密钥（推荐用于更高的请求限制）

## 许可证

MIT