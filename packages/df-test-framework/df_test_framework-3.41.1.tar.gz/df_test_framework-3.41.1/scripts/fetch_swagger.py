"""从 Swagger UI / Knife4j 获取 OpenAPI 文档

支持：
- 标准 Swagger UI
- Knife4j 2.x/3.x/4.x（包括多分组模式）
- SpringDoc OpenAPI
- Spring Boot context-path

用法：
    python scripts/fetch_swagger.py [URL] [OUTPUT]

示例：
    python scripts/fetch_swagger.py http://localhost:8089/swagger-ui/index.html
    python scripts/fetch_swagger.py http://localhost:8089/api/doc.html  # 带 context-path
    python scripts/fetch_swagger.py http://example.com swagger.json
"""

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

import httpx


# 常见的 OpenAPI 文档端点（按优先级排序）
COMMON_API_DOC_PATHS = [
    # OpenAPI 3.x
    "/v3/api-docs",
    "/v3/api-docs/default",
    "/v3/api-docs/default-group",
    # Swagger 2.x
    "/v2/api-docs",
    "/v2/api-docs?group=default",
    # 通用
    "/swagger.json",
    "/api-docs",
    "/openapi.json",
    "/swagger/v1/swagger.json",
    # Knife4j 资源发现
    "/swagger-resources",
]


def get_base_url(url: str) -> str:
    """从 URL 中提取基础地址（包含 context-path）

    智能识别 Spring Boot context-path，例如：
    - http://localhost:8089/api/doc.html → http://localhost:8089/api
    - http://localhost:8089/api/swagger-ui/index.html → http://localhost:8089/api
    - http://localhost:8089/swagger-ui/index.html → http://localhost:8089

    Returns:
        包含 context-path 的基础地址
    """
    parsed = urlparse(url)
    path = parsed.path

    # 常见的 Swagger/Knife4j UI 页面路径（需要从 URL 中移除）
    ui_patterns = [
        "/doc.html",           # Knife4j
        "/swagger-ui.html",    # 旧版 Swagger UI
        "/swagger-ui/",        # SpringDoc Swagger UI
        "/webjars/",           # 静态资源
    ]

    # 提取 context-path：移除 UI 页面路径部分
    context_path = path
    for pattern in ui_patterns:
        if pattern in context_path:
            context_path = context_path.split(pattern)[0]
            break

    # 移除尾部斜杠
    context_path = context_path.rstrip("/")

    base = f"{parsed.scheme}://{parsed.netloc}"
    if context_path:
        base = f"{base}{context_path}"

    return base


def try_fetch_swagger_doc(base_url: str, client: httpx.Client) -> dict | list[dict] | None:
    """尝试从常见端点获取 Swagger 文档

    Returns:
        单个文档 dict，或多分组时返回 list[dict]
    """
    for path in COMMON_API_DOC_PATHS:
        # 直接拼接，避免 urljoin 替换 context-path
        url = base_url.rstrip("/") + path
        print(f"  尝试: {url}")
        try:
            response = client.get(url, timeout=10)
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                if "json" in content_type or path.endswith(".json") or "?" in path:
                    data = response.json()
                    # 检查是否是有效的 OpenAPI 文档
                    if "swagger" in data or "openapi" in data or "paths" in data:
                        print(f"  ✅ 找到 OpenAPI 文档: {url}")
                        return data

                    # 可能是 swagger-resources 响应（Knife4j 多分组模式）
                    if isinstance(data, list) and len(data) > 0:
                        return _handle_swagger_resources(base_url, data, client)
        except Exception as e:
            print(f"  ❌ 失败: {e}")
            continue
    return None


def _handle_swagger_resources(
    base_url: str, resources: list, client: httpx.Client
) -> dict | list[dict] | None:
    """处理 swagger-resources 响应（Knife4j 多分组模式）

    Args:
        base_url: API 基础地址
        resources: swagger-resources 返回的资源列表
        client: HTTP 客户端

    Returns:
        单个文档或多个文档列表
    """
    print(f"\n  📋 发现 {len(resources)} 个 API 分组:")
    docs = []

    for i, resource in enumerate(resources):
        # 获取资源 URL（支持多种字段名）
        resource_url = resource.get("url") or resource.get("location") or resource.get("path")
        if not resource_url:
            continue

        # 获取分组名称
        group_name = resource.get("name") or resource.get("swaggerVersion") or f"group_{i}"
        # 智能拼接 URL：如果资源 URL 是相对路径，则拼接到 base_url
        if resource_url.startswith("http"):
            full_url = resource_url
        else:
            full_url = base_url.rstrip("/") + (
                resource_url if resource_url.startswith("/") else "/" + resource_url
            )
        print(f"    [{i + 1}] {group_name}: {full_url}")

        try:
            res = client.get(full_url, timeout=10)
            if res.status_code == 200:
                doc = res.json()
                if "swagger" in doc or "openapi" in doc or "paths" in doc:
                    doc["_group_name"] = group_name  # 标记分组名
                    doc["_group_url"] = full_url
                    docs.append(doc)
                    print(f"        ✅ 成功 ({len(doc.get('paths', {}))} 个接口)")
        except Exception as e:
            print(f"        ❌ 失败: {e}")

    if not docs:
        return None
    if len(docs) == 1:
        return docs[0]
    return docs


def fetch_swagger(url: str, output: str | None = None) -> None:
    """获取 Swagger 文档并保存"""
    base_url = get_base_url(url)
    print(f"基础地址: {base_url}")
    print("正在探测 OpenAPI 文档端点...")

    with httpx.Client(follow_redirects=True) as client:
        # 尝试获取文档
        result = try_fetch_swagger_doc(base_url, client)

        if not result:
            print("\n❌ 未找到 OpenAPI 文档，请手动指定文档 URL")
            print("常见端点:")
            for path in COMMON_API_DOC_PATHS:
                print(f"  {base_url.rstrip('/') + path}")
            sys.exit(1)

        # 处理多分组情况
        if isinstance(result, list):
            _save_multiple_docs(result, output)
        else:
            _save_single_doc(result, output)


def _save_single_doc(doc: dict, output: str | None) -> None:
    """保存单个文档"""
    # 确定输出文件名
    if not output:
        # 从文档中获取标题作为文件名
        title = doc.get("info", {}).get("title", "swagger")
        # 清理文件名
        safe_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in title)
        output = f"{safe_title}.json"

    # 保存文档
    output_path = Path(output)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 已保存到: {output_path.absolute()}")
    print(f"   版本: {doc.get('openapi') or doc.get('swagger', 'unknown')}")
    print(f"   标题: {doc.get('info', {}).get('title', 'N/A')}")
    print(f"   接口数: {len(doc.get('paths', {}))}")

    # 提示使用方法
    print("\n🚀 使用方法:")
    print(f"   uv run df-test gen from-swagger {output_path.name}")


def _save_multiple_docs(docs: list[dict], output: str | None) -> None:
    """保存多个分组文档（Knife4j 多分组模式）"""
    print(f"\n📦 检测到 Knife4j 多分组模式，共 {len(docs)} 个分组")

    saved_files = []
    for doc in docs:
        group_name = doc.pop("_group_name", "unknown")
        doc.pop("_group_url", None)

        # 生成文件名
        if output:
            # 用户指定了输出，添加分组后缀
            base_name = Path(output).stem
            suffix = Path(output).suffix or ".json"
            safe_group = "".join(c if c.isalnum() or c in "-_" else "_" for c in group_name)
            file_name = f"{base_name}_{safe_group}{suffix}"
        else:
            # 使用分组名作为文件名
            safe_group = "".join(c if c.isalnum() or c in "-_" else "_" for c in group_name)
            file_name = f"{safe_group}.json"

        output_path = Path(file_name)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)

        saved_files.append((output_path, group_name, len(doc.get("paths", {}))))
        print(f"  ✅ {output_path.name} ({len(doc.get('paths', {}))} 个接口)")

    print(f"\n📁 已保存 {len(saved_files)} 个文件")

    # 提示使用方法
    print("\n🚀 使用方法:")
    for file_path, group_name, _ in saved_files:
        print(f"   uv run df-test gen from-swagger {file_path.name}  # {group_name}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    url = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else None

    fetch_swagger(url, output)
