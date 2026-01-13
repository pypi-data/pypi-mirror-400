"""从 OpenAPI/Swagger 规范生成测试代码

基于 OpenAPI 规范自动生成测试用例、API 客户端和 Pydantic 模型。

v3.38.0 重大改进:
- Model 分类生成（requests/responses/common）
- API 方法类型化（强类型参数和返回值）
- 通用响应包装处理（Result[T]）
- 符合框架最佳实践和脚手架结构

v3.39.1 改进（智能类型推断）:
- 基于字段名的智能类型推断（data/pagination → dict，list/items → list）
- 查询操作识别和更精确的断言模板
- 兼容 ok/success 两种响应状态格式
- 适配 Java 后端缺少 Swagger 注解的场景
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from ..utils import (
    AUTO_GENERATED_END,
    AUTO_GENERATED_START,
    AUTO_GENERATED_WARNING,
    USER_EXTENSIONS_HINT,
    USER_EXTENSIONS_START,
    create_file_with_merge,
    detect_project_name,
    generate_init_from_directory,
    merge_with_markers,
    to_ascii_identifier,
    to_pascal_case,
    to_snake_case,
)
from .openapi_parser import OPENAPI_AVAILABLE, APIEndpoint, OpenAPIParser


def _simplify_operation_id(operation_id: str) -> str:
    """简化 FastAPI 自动生成的 operationId

    FastAPI 自动生成的 operationId 格式为: {summary}_{path}_{method}
    例如: create_association_group_api_jym_product_associations_groups_post

    本函数提取有意义的部分，移除冗余的路径和方法后缀。

    Args:
        operation_id: 原始的 operationId

    Returns:
        简化后的名称

    Example:
        >>> _simplify_operation_id("create_association_group_api_jym_product_associations_groups_post")
        "create_association_group"
        >>> _simplify_operation_id("get_user_by_id_api_users_id_get")
        "get_user_by_id"
        >>> _simplify_operation_id("simple_action")
        "simple_action"
    """
    if not operation_id:
        return "unknown"

    name = operation_id

    # 策略1: 查找 _api_ 模式（FastAPI 常见格式）
    # 例如: create_group_api_xxx_yyy_post -> create_group
    api_match = re.search(r"^(.+?)_api_", name)
    if api_match:
        name = api_match.group(1)
    else:
        # 策略2: 移除 _using_xxx 后缀（Spring 风格，优先检查）
        # 例如: delete_item_using_delete -> delete_item
        for suffix in ["_using_get", "_using_post", "_using_put", "_using_delete", "_using_patch"]:
            if name.endswith(suffix):
                name = name[: -len(suffix)]
                break
        else:
            # 策略3: 移除简单的 HTTP 方法后缀
            # 例如: get_users_get -> get_users
            for suffix in ["_get", "_post", "_put", "_delete", "_patch", "_head", "_options"]:
                if name.endswith(suffix):
                    name = name[: -len(suffix)]
                    break

    return name


def generate_from_openapi(
    spec_path: str | Path,
    *,
    output_dir: Path | None = None,
    generate_tests: bool = True,
    generate_clients: bool = True,
    generate_models: bool = True,
    tags: list[str] | None = None,
    force: bool = False,
    merge: bool = False,
) -> None:
    """从 OpenAPI 规范生成测试代码

    Args:
        spec_path: OpenAPI 规范文件路径或 URL
        output_dir: 输出目录（默认: 当前目录）
        generate_tests: 是否生成测试用例
        generate_clients: 是否生成 API 客户端
        generate_models: 是否生成 Pydantic 模型
        tags: 过滤的标签列表（None 表示生成所有）
        force: 是否强制覆盖（与 merge 互斥）
        merge: 是否使用增量合并模式（v3.39.0+）

    v3.39.0 新增增量合并模式:
        使用 merge=True 时，会保留用户在 USER EXTENSIONS 区域的修改，
        只更新 AUTO-GENERATED 区域的内容。适用于分阶段生成或 API 新增接口的场景。

    Example:
        >>> # 首次生成
        >>> generate_from_openapi("swagger.json", tags=["用户管理"])
        >>>
        >>> # 新增接口后增量合并
        >>> generate_from_openapi("swagger.json", tags=["用户管理"], merge=True)
    """
    if not OPENAPI_AVAILABLE:
        print("❌ 错误: OpenAPI 功能需要安装 pyyaml 库")
        print("   请运行: pip install pyyaml")
        return

    # 检测项目名称并转换为有效的 Python 包名
    raw_project_name = detect_project_name()
    if not raw_project_name:
        print("⚠️  错误: 无法检测项目名称，请在项目根目录下运行")
        return
    # 转换为 snake_case（Python 包名不能包含连字符）
    project_name = to_snake_case(raw_project_name)

    if output_dir is None:
        output_dir = Path.cwd()

    # 解析 OpenAPI 规范
    print(f"\n📝 解析 OpenAPI 规范: {spec_path}")
    try:
        parser = OpenAPIParser(spec_path)
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        return

    # 获取 API 信息
    info = parser.get_info()
    print(f"📋 API: {info.get('title', 'Unknown')} v{info.get('version', '1.0.0')}")

    # 获取端点列表
    endpoints = parser.get_endpoints(tags=tags)
    print(f"📊 找到 {len(endpoints)} 个 API 端点")

    if not endpoints:
        print("⚠️  没有找到符合条件的 API 端点")
        return

    # 生成统计
    generated_files = []

    # 显示模式
    if merge:
        print("🔀 使用增量合并模式（保留用户修改）")
    elif force:
        print("⚠️  使用强制覆盖模式")

    # Phase 1: 生成模型（分类到 requests/responses/common）
    if generate_models:
        print("\n📝 生成 Pydantic 模型...")
        model_files = _generate_models_v2(
            parser, endpoints, project_name, output_dir, force=force, merge=merge
        )
        generated_files.extend(model_files)

    # Phase 2: 生成 API 客户端（类型化方法）
    if generate_clients:
        print("\n📝 生成 API 客户端...")
        client_files = _generate_api_clients_v2(
            endpoints, parser, project_name, output_dir, force=force, merge=merge
        )
        generated_files.extend(client_files)

    # Phase 3: 生成测试用例
    if generate_tests:
        print("\n📝 生成测试用例...")
        # v3.41.1: 传递 parser 用于解析 $ref 引用
        test_files = _generate_tests_v2(
            endpoints, project_name, output_dir, parser=parser, force=force, merge=merge
        )
        generated_files.extend(test_files)

    # 输出结果
    print("\n✅ 生成完成！")
    print(f"\n📁 共生成 {len(generated_files)} 个文件:")
    for file_type, file_path in generated_files:
        print(f"  ✓ {file_type:<20} {file_path}")

    print("\n💡 下一步:")
    print("  1. 在 tests/conftest.py 中添加以下代码（自动发现所有 API 类）:")
    print("     ```python")
    print("     from df_test_framework.testing.decorators import load_api_fixtures")
    print("")
    print(f'     load_api_fixtures(globals(), apis_package="{project_name}.apis")')
    print("     ```")
    print("  2. 根据需要完善请求/响应模型")
    print("  3. 运行测试: pytest tests/ -v")


# ========== Phase 1: Model 分类生成 ==========


def _generate_models_v2(
    parser: OpenAPIParser,
    endpoints: list[APIEndpoint],
    project_name: str,
    output_dir: Path,
    *,
    force: bool = False,
    merge: bool = False,
) -> list[tuple[str, Path]]:
    """生成分类的 Pydantic 模型

    v3.38.0 改进:
    - 区分 requests/responses/common
    - 按 tag 组织文件
    - 生成通用响应包装类

    v3.39.0 改进:
    - 支持增量合并模式（merge=True）
    - 动态生成 __init__.py 导出
    """
    generated: list[tuple[str, Path]] = []

    # 创建目录
    models_dir = output_dir / "src" / project_name / "models"
    requests_dir = models_dir / "requests"
    responses_dir = models_dir / "responses"
    requests_dir.mkdir(parents=True, exist_ok=True)
    responses_dir.mkdir(parents=True, exist_ok=True)

    # Phase 1.1: 生成 models/base.py（通用响应包装）
    base_model_files = _generate_base_models(models_dir, force=force, merge=merge)
    generated.extend(base_model_files)

    # Phase 1.2: 按 tag 分组 endpoints
    endpoints_by_tag: dict[str, list[APIEndpoint]] = defaultdict(list)
    for endpoint in endpoints:
        tag = endpoint.tags[0] if endpoint.tags else "default"
        endpoints_by_tag[tag].append(endpoint)

    # Phase 1.3: 为每个 tag 生成 request/response 模型
    parser.get_schemas()

    for tag, tag_endpoints in endpoints_by_tag.items():
        # 生成 requests/{tag}.py
        request_files = _generate_request_models(
            tag, tag_endpoints, parser, requests_dir, force=force, merge=merge
        )
        generated.extend(request_files)

        # 生成 responses/{tag}.py
        response_files = _generate_response_models(
            tag, tag_endpoints, parser, responses_dir, force=force, merge=merge
        )
        generated.extend(response_files)

    # Phase 1.4: 生成 __init__.py（动态扫描目录）
    init_files = _generate_model_init_files(models_dir, requests_dir, responses_dir)
    generated.extend(init_files)

    return generated


def _generate_base_models(
    models_dir: Path, *, force: bool = False, merge: bool = False
) -> list[tuple[str, Path]]:
    """生成 models/base.py（通用响应包装类）

    v3.39.0: 添加分区标记支持增量合并
    """
    generated = []

    base_model_code = f'''"""通用响应模型

提供常见的响应包装类，如 Result[T]、PageInfo 等。
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


{AUTO_GENERATED_START}
{AUTO_GENERATED_WARNING}


class Result(BaseModel, Generic[T]):
    """通用响应包装

    常见格式:
        {{
          "code": 200,
          "message": "success",
          "data": {{ ... }}
        }}

    使用示例:
        >>> class UserResponse(BaseModel):
        ...     id: int
        ...     name: str
        >>>
        >>> response_data = {{"code": 200, "message": "success", "data": {{"id": 1, "name": "Alice"}}}}
        >>> result = Result[UserResponse](**response_data)
        >>> print(result.data.name)  # Alice
    """

    code: int = Field(..., description="业务状态码")
    message: str = Field(..., description="响应消息")
    data: T | None = Field(None, description="响应数据")


class PageInfo(BaseModel, Generic[T]):
    """分页响应

    常见格式:
        {{
          "total": 100,
          "current": 1,
          "size": 20,
          "records": [...]
        }}
    """

    total: int = Field(..., description="总记录数")
    current: int = Field(default=1, description="当前页码")
    size: int = Field(default=20, description="每页大小")
    records: list[T] = Field(default_factory=list, description="记录列表")


{AUTO_GENERATED_END}


{USER_EXTENSIONS_START}
{USER_EXTENSIONS_HINT}


__all__ = ["Result", "PageInfo"]
'''

    file_path = models_dir / "base.py"
    success, action = create_file_with_merge(file_path, base_model_code, force=force, merge=merge)

    if success:
        generated.append(
            ("Model (Base)", Path("src") / file_path.relative_to(models_dir.parent.parent))
        )
        if action == "merged":
            print(f"  🔀 合并: {file_path.name}")
    elif "skipped" not in action:
        print(f"  ⚠️  {action}: {file_path.name}")

    return generated


def _generate_request_models(
    tag: str,
    endpoints: list[APIEndpoint],
    parser: OpenAPIParser,
    requests_dir: Path,
    *,
    force: bool = False,
    merge: bool = False,
) -> list[tuple[str, Path]]:
    """生成请求模型文件

    v3.39.0: 添加分区标记支持增量合并
    """
    generated = []

    # 收集该 tag 下所有的 request models
    request_models = []
    for endpoint in endpoints:
        if endpoint.request_body:
            model_info = _extract_request_model_info(endpoint, parser)
            if model_info:
                request_models.append(model_info)

    if not request_models:
        return generated

    # 生成文件内容（使用 ASCII 标识符处理中文 tag）
    tag_id = to_ascii_identifier(tag)
    file_name = f"{tag_id}.py"
    file_path = requests_dir / file_name

    code = _build_request_models_file(tag, tag_id, request_models)

    success, action = create_file_with_merge(file_path, code, force=force, merge=merge)

    if success:
        generated.append(
            (
                "Model (Request)",
                Path("src") / file_path.relative_to(requests_dir.parent.parent.parent),
            )
        )
        if action == "merged":
            print(f"  🔀 合并: {file_path.name}")
    elif "skipped" not in action:
        print(f"  ⚠️  {action}: {file_path.name}")

    return generated


def _generate_response_models(
    tag: str,
    endpoints: list[APIEndpoint],
    parser: OpenAPIParser,
    responses_dir: Path,
    *,
    force: bool = False,
    merge: bool = False,
) -> list[tuple[str, Path]]:
    """生成响应模型文件

    v3.39.0: 添加分区标记支持增量合并
    """
    generated = []

    # 收集该 tag 下所有的 response models
    response_models = []
    for endpoint in endpoints:
        model_info = _extract_response_model_info(endpoint, parser)
        if model_info:
            response_models.append(model_info)

    if not response_models:
        return generated

    # 生成文件内容（使用 ASCII 标识符处理中文 tag）
    tag_id = to_ascii_identifier(tag)
    file_name = f"{tag_id}.py"
    file_path = responses_dir / file_name

    code = _build_response_models_file(tag, tag_id, response_models)

    success, action = create_file_with_merge(file_path, code, force=force, merge=merge)

    if success:
        generated.append(
            (
                "Model (Response)",
                Path("src") / file_path.relative_to(responses_dir.parent.parent.parent),
            )
        )
        if action == "merged":
            print(f"  🔀 合并: {file_path.name}")
    elif "skipped" not in action:
        print(f"  ⚠️  {action}: {file_path.name}")

    return generated


def _extract_request_model_info(endpoint: APIEndpoint, parser: OpenAPIParser) -> dict | None:
    """从 endpoint 提取请求模型信息"""
    if not endpoint.request_body:
        return None

    # 生成模型名称（简化后的 operationId）
    simplified_name = _simplify_operation_id(endpoint.operation_id)
    model_name = to_pascal_case(simplified_name) + "Request"

    # 获取 schema 并解析 $ref 引用
    schema = endpoint.request_body.get("schema", {})
    if "$ref" in schema:
        schema = parser._resolve_ref(schema["$ref"])

    return {
        "name": model_name,
        "schema": schema,
        "description": endpoint.summary or f"{model_name} 请求模型",
    }


def _extract_response_model_info(endpoint: APIEndpoint, parser: OpenAPIParser) -> dict | None:
    """从 endpoint 提取响应模型信息

    即使 Swagger 文档中没有详细的响应 schema，也会生成基于 Result[dict] 的占位符模型。
    """
    # 尝试获取 200/201 响应
    success_response = endpoint.get_success_response()
    if not success_response:
        return None

    # 生成模型名称（简化后的 operationId）
    simplified_name = _simplify_operation_id(endpoint.operation_id)
    model_name = to_pascal_case(simplified_name) + "Response"

    # 获取 schema 并解析 $ref 引用
    schema = success_response.get("schema", {})
    if "$ref" in schema:
        schema = parser._resolve_ref(schema["$ref"])

    # 标记是否有详细的 schema（用于决定生成完整模型还是占位符）
    has_detailed_schema = bool(schema and schema.get("properties"))

    return {
        "name": model_name,
        "schema": schema,
        "description": success_response.get("description", f"{model_name} 响应模型"),
        "has_detailed_schema": has_detailed_schema,
    }


def _build_request_models_file(tag: str, tag_id: str, models: list[dict]) -> str:
    """构建请求模型文件内容

    Args:
        tag: 原始 tag 名称（用于注释）
        tag_id: ASCII 标识符（用于导入路径）
        models: 模型信息列表

    v3.39.0: 添加分区标记支持增量合并
    v3.41.1: 使用 BaseRequest 基类（位于 core.models，默认排除 None 值）
    """
    # 去重
    unique_models = {m["name"]: m for m in models}

    model_classes = []
    for model_info in unique_models.values():
        # v3.41.1: 请求模型使用 BaseRequest 基类
        model_code = _build_model_class(
            model_info["name"],
            model_info["schema"],
            model_info["description"],
            base_class="BaseRequest",
        )
        model_classes.append(model_code)

    all_names = list(unique_models.keys())

    code = f'''"""自动生成的请求模型 - {tag}

从 OpenAPI 规范生成。
模块标识: {tag_id}

v3.41.1 改进：
- 使用 BaseRequest 基类（位于 core.models），序列化时自动排除 None 值
- 字段名使用 Python 惯例的 snake_case，序列化时使用原始的 camelCase
"""

from typing import Any

from pydantic import Field
from df_test_framework import BaseRequest


{AUTO_GENERATED_START}
{AUTO_GENERATED_WARNING}

{chr(10).join(model_classes)}

{AUTO_GENERATED_END}


{USER_EXTENSIONS_START}
{USER_EXTENSIONS_HINT}


__all__ = {all_names}
'''

    return code


def _build_response_models_file(tag: str, tag_id: str, models: list[dict]) -> str:
    """构建响应模型文件内容

    Args:
        tag: 原始 tag 名称（用于注释）
        tag_id: ASCII 标识符（用于导入路径）
        models: 模型信息列表

    v3.38.1 改进：
    - 为没有详细 schema 的响应生成基于 Result[dict] 的占位符模型
    - 添加 TODO 注释提示用户完善模型

    v3.39.0: 添加分区标记支持增量合并
    """
    # 去重
    unique_models = {m["name"]: m for m in models}

    model_classes = []
    for model_info in unique_models.values():
        has_detailed_schema = model_info.get("has_detailed_schema", False)
        if has_detailed_schema:
            # 有详细 schema，生成完整模型
            model_code = _build_model_class(
                model_info["name"], model_info["schema"], model_info["description"]
            )
        else:
            # 没有详细 schema，生成占位符模型
            model_code = _build_placeholder_response_model(
                model_info["name"], model_info["description"]
            )
        model_classes.append(model_code)

    all_names = list(unique_models.keys())

    code = f'''"""自动生成的响应模型 - {tag}

从 OpenAPI 规范生成。
模块标识: {tag_id}

注意：
- 字段名使用 Python 惯例的 snake_case，但序列化时使用原始的 camelCase
- 如果 Swagger 文档未定义响应结构，会生成基于 Result[dict] 的占位符模型
- 请根据实际 API 响应结构完善这些模型
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from ..base import Result


{AUTO_GENERATED_START}
{AUTO_GENERATED_WARNING}

{chr(10).join(model_classes)}

{AUTO_GENERATED_END}


{USER_EXTENSIONS_START}
{USER_EXTENSIONS_HINT}


__all__ = {all_names}
'''

    return code


def _build_placeholder_response_model(model_name: str, description: str) -> str:
    """构建占位符响应模型（当 Swagger 未定义响应 schema 时使用）

    生成基于 Result[dict] 的简单模型，用户可以后续根据实际响应结构完善。
    """
    return f'''class {model_name}(Result[dict[str, Any]]):
    """{description}

    注意：Swagger 文档未定义此响应的详细结构。
    此模型基于通用 Result[dict] 生成，请根据实际 API 响应完善。

    常见响应格式:
        {{"code": 200, "message": "success", "data": {{...}}}}

    使用示例:
        >>> response = api.some_method(request)
        >>> if response.code == 200:
        ...     print(response.data)  # dict[str, Any]

    TODO: 根据实际响应结构定义具体字段
    """
    pass
'''


def _build_model_class(
    model_name: str,
    schema: dict,
    description: str,
    base_class: str = "BaseModel",
) -> str:
    """构建 Pydantic 模型类代码

    自动处理 Java/Python 命名转换：
    - Java camelCase -> Python snake_case
    - 保留原始名称作为 alias

    Args:
        model_name: 模型类名
        schema: OpenAPI schema 定义
        description: 模型描述
        base_class: 基类名称，默认 "BaseModel"，请求模型使用 "BaseRequest"

    v3.41.1 改进：
    - 支持指定基类
    - 请求模型使用 BaseRequest（位于 core.models，默认排除 None 值）
    """
    properties = schema.get("properties", {})
    required = schema.get("required", [])

    # BaseRequest 已经包含 model_config，不需要重复定义
    need_model_config = base_class != "BaseRequest"
    model_config_line = (
        "\n    model_config = ConfigDict(populate_by_name=True)\n" if need_model_config else ""
    )

    if not properties:
        # 空模型
        if need_model_config:
            return f'''class {model_name}({base_class}):
    """{description}"""

    model_config = ConfigDict(populate_by_name=True)
    pass
'''
        else:
            return f'''class {model_name}({base_class}):
    """{description}"""
    pass
'''

    # 生成字段
    fields = []
    for original_name, field_schema in properties.items():
        # 转换字段名：camelCase -> snake_case
        python_name = to_snake_case(original_name)
        # v3.39.1: 传递字段名进行智能类型推断
        field_type = _get_python_type(field_schema, field_name=original_name)
        is_required = original_name in required
        field_desc = field_schema.get("description", f"{original_name} 字段")

        # 如果转换后名称不同，添加 alias
        if python_name != original_name:
            alias_param = f', alias="{original_name}"'
        else:
            alias_param = ""

        if is_required:
            fields.append(
                f'    {python_name}: {field_type} = Field(..., description="{field_desc}"{alias_param})'
            )
        else:
            fields.append(
                f'    {python_name}: {field_type} | None = Field(None, description="{field_desc}"{alias_param})'
            )

    fields_code = "\n".join(fields)

    return f'''class {model_name}({base_class}):
    """{description}"""
{model_config_line}
{fields_code}
'''


def _get_python_type(schema: dict, field_name: str | None = None) -> str:
    """将 OpenAPI 类型转换为 Python 类型

    v3.39.1 改进:
    - 支持基于字段名的智能类型推断
    - 当 Swagger 注解不完整时，根据常见命名惯例推断正确类型
    - 处理 $ref 引用类型，转换为 dict[str, Any]

    v3.41.1 改进:
    - 优先使用后端明确定义的类型
    - 只有当类型为 object/$ref 时才使用智能推断

    Args:
        schema: OpenAPI schema 定义
        field_name: 字段名称，用于智能类型推断

    Returns:
        Python 类型字符串
    """
    schema_type = schema.get("type")

    # 基础类型映射（当后端明确定义时直接使用）
    type_mapping = {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
    }

    # 1. 优先使用后端明确定义的基础类型
    if schema_type in type_mapping:
        return type_mapping[schema_type]

    # 2. 处理数组类型
    if schema_type == "array" and "items" in schema:
        item_type = _get_python_type(schema["items"])
        return f"list[{item_type}]"

    # 3. 当类型为 object/$ref 或未定义时，使用智能字段名推断
    # 这是 Java 后端 Swagger 注解不完善的常见情况
    is_ambiguous_type = schema_type == "object" or schema_type is None or "$ref" in schema

    if is_ambiguous_type and field_name:
        field_lower = field_name.lower()

        # v3.41.1: 常见的应该是 str 类型的字段名
        # 这些字段通常被 Java 后端错误地标注为 object 或没有明确类型
        string_patterns = [
            "msg",  # 消息
            "message",  # 消息
            "error",  # 错误信息
            "error_msg",  # 错误消息
            "error_message",  # 错误消息
            "status",  # 状态（通常是 "ok"/"fail" 等字符串）
            "reason",  # 原因
            "description",  # 描述
            "title",  # 标题
            "remark",  # 备注
            "remarks",  # 备注
            "note",  # 注释
            "notes",  # 注释
        ]

        # 检查是否是常见字符串字段
        for pattern in string_patterns:
            if field_lower == pattern or field_lower.endswith(f"_{pattern}"):
                return "str"

        # 常见的应该是 dict 类型的字段名
        dict_patterns = [
            "data",  # 响应数据容器
            "pagination",  # 分页信息
            "params",  # 参数对象
            "result",  # 结果对象
            "info",  # 信息对象
            "config",  # 配置对象
            "settings",  # 设置对象
            "options",  # 选项对象
            "metadata",  # 元数据
            "extra",  # 额外信息
            "attributes",  # 属性对象
            "properties",  # 属性对象
        ]

        # 常见的应该是 list 类型的字段名
        list_patterns = [
            "list",  # 列表数据
            "items",  # 项目列表
            "records",  # 记录列表
            "rows",  # 行数据
            "results",  # 结果列表
            "ids",  # ID 列表
            "names",  # 名称列表
            "codes",  # 编码列表
            "values",  # 值列表
            "tags",  # 标签列表
            "permissions",  # 权限列表
            "roles",  # 角色列表
        ]

        # 检查 dict 模式
        for pattern in dict_patterns:
            if field_lower == pattern or field_lower.endswith(f"_{pattern}"):
                return "dict[str, Any]"

        # 检查 list 模式
        for pattern in list_patterns:
            if field_lower == pattern or field_lower.endswith(f"_{pattern}"):
                return "list[Any]"

    return type_mapping.get(schema_type, "Any")


def _generate_model_init_files(
    models_dir: Path, requests_dir: Path, responses_dir: Path
) -> list[tuple[str, Path]]:
    """生成 models/__init__.py 和子目录的 __init__.py

    v3.39.0 改进：
    - 动态扫描目录生成导出列表
    - 解决分阶段生成时导出不累积的问题
    - __init__.py 总是根据实际文件重新生成
    """
    generated = []

    # models/__init__.py（导出 base 模块 + 子包内容）
    models_init_code = f'''"""数据模型模块

组织结构:
- base.py: 通用响应包装类（Result[T]、PageInfo等）
- requests/: 请求模型
- responses/: 响应模型
"""

{AUTO_GENERATED_START}
{AUTO_GENERATED_WARNING}

from .base import PageInfo, Result
from .requests import *  # noqa: F401, F403
from .responses import *  # noqa: F401, F403

__all__ = ["PageInfo", "Result", "requests", "responses"]

{AUTO_GENERATED_END}


{USER_EXTENSIONS_START}
{USER_EXTENSIONS_HINT}

'''

    models_init_path = models_dir / "__init__.py"
    # 使用增量合并：保留用户扩展区域
    if models_init_path.exists():
        existing = models_init_path.read_text(encoding="utf-8")
        if USER_EXTENSIONS_START in existing and AUTO_GENERATED_START in existing:
            models_init_code = merge_with_markers(existing, models_init_code)

    models_init_path.write_text(models_init_code, encoding="utf-8")
    generated.append(
        (
            "Model (Init)",
            Path("src") / models_init_path.relative_to(models_dir.parent.parent),
        )
    )

    # requests/__init__.py（动态扫描生成）
    requests_init_code = generate_init_from_directory(requests_dir, docstring="请求模型模块")
    requests_init_path = requests_dir / "__init__.py"
    # 使用增量合并：保留用户扩展区域
    if requests_init_path.exists():
        existing = requests_init_path.read_text(encoding="utf-8")
        if USER_EXTENSIONS_START in existing and AUTO_GENERATED_START in existing:
            requests_init_code = merge_with_markers(existing, requests_init_code)

    requests_init_path.write_text(requests_init_code, encoding="utf-8")

    # responses/__init__.py（动态扫描生成）
    responses_init_code = generate_init_from_directory(responses_dir, docstring="响应模型模块")
    responses_init_path = responses_dir / "__init__.py"
    # 使用增量合并：保留用户扩展区域
    if responses_init_path.exists():
        existing = responses_init_path.read_text(encoding="utf-8")
        if USER_EXTENSIONS_START in existing and AUTO_GENERATED_START in existing:
            responses_init_code = merge_with_markers(existing, responses_init_code)

    responses_init_path.write_text(responses_init_code, encoding="utf-8")

    return generated


# ========== Phase 2: API 客户端类型化 ==========


def _generate_api_clients_v2(
    endpoints: list[APIEndpoint],
    parser: OpenAPIParser,
    project_name: str,
    output_dir: Path,
    *,
    force: bool = False,
    merge: bool = False,
) -> list[tuple[str, Path]]:
    """生成类型化的 API 客户端

    v3.38.0 改进:
    - 方法参数和返回值使用 Pydantic 模型
    - 自动导入对应的 request/response 模型
    - 利用 BaseAPI 的自动序列化能力

    v3.39.0 改进:
    - 支持增量合并模式（merge=True）
    """
    generated: list[tuple[str, Path]] = []

    # 按标签分组
    endpoints_by_tag: dict[str, list[APIEndpoint]] = defaultdict(list)
    for endpoint in endpoints:
        tag = endpoint.tags[0] if endpoint.tags else "default"
        endpoints_by_tag[tag].append(endpoint)

    apis_dir = output_dir / "src" / project_name / "apis"
    apis_dir.mkdir(parents=True, exist_ok=True)

    # 为每个标签生成一个客户端（使用 ASCII 标识符处理中文 tag）
    for tag, tag_endpoints in endpoints_by_tag.items():
        tag_id = to_ascii_identifier(tag)
        file_name = f"{tag_id}_api.py"
        file_path = apis_dir / file_name

        # 生成客户端代码
        content = _build_typed_client_code(tag, tag_id, tag_endpoints, project_name)

        success, action = create_file_with_merge(file_path, content, force=force, merge=merge)

        if success:
            generated.append(("API Client", file_path.relative_to(output_dir)))
            if action == "merged":
                print(f"  🔀 合并: {file_path.name}")
        elif "skipped" in action:
            print(f"  ⏭️  跳过: {file_path.name}（已存在）")
        else:
            print(f"  ⚠️  {action}: {file_path.name}")

    # 生成 apis/__init__.py（动态扫描生成）
    apis_init_code = generate_init_from_directory(apis_dir, docstring="API 客户端模块")
    apis_init_path = apis_dir / "__init__.py"
    # 使用增量合并：保留用户扩展区域
    if apis_init_path.exists():
        existing = apis_init_path.read_text(encoding="utf-8")
        if USER_EXTENSIONS_START in existing and AUTO_GENERATED_START in existing:
            apis_init_code = merge_with_markers(existing, apis_init_code)

    apis_init_path.write_text(apis_init_code, encoding="utf-8")
    generated.append(("API (Init)", apis_init_path.relative_to(output_dir)))

    return generated


def _build_typed_client_code(
    tag: str, tag_id: str, endpoints: list[APIEndpoint], project_name: str
) -> str:
    """构建类型化的 API 客户端代码

    Args:
        tag: 原始 tag 名称（用于注释）
        tag_id: ASCII 标识符（用于类名、fixture名、导入路径）
        endpoints: API 端点列表
        project_name: 项目名称

    v3.38.0 改进:
    - 导入 request/response 模型
    - 方法签名使用强类型
    - 利用 BaseAPI 自动序列化/解析
    """
    class_name = to_pascal_case(tag_id) + "API"
    fixture_name = tag_id + "_api"
    tag_snake = tag_id

    # 获取公共路径前缀
    paths = [e.path for e in endpoints]
    base_path = _get_common_path_prefix(paths)

    # 收集需要导入的模型（使用简化后的名称）
    request_models = set()
    response_models = set()

    for endpoint in endpoints:
        if endpoint.request_body:
            simplified_name = _simplify_operation_id(endpoint.operation_id)
            request_models.add(to_pascal_case(simplified_name) + "Request")

        if endpoint.get_success_response():
            simplified_name = _simplify_operation_id(endpoint.operation_id)
            response_models.add(to_pascal_case(simplified_name) + "Response")

    # 生成导入语句
    imports = []
    if request_models:
        imports.append(
            f"from ..models.requests.{tag_snake} import (\n    "
            + ",\n    ".join(sorted(request_models))
            + ",\n)"
        )
    if response_models:
        imports.append(
            f"from ..models.responses.{tag_snake} import (\n    "
            + ",\n    ".join(sorted(response_models))
            + ",\n)"
        )

    imports_code = "\n".join(imports) if imports else ""

    # 生成方法
    methods = []
    for endpoint in endpoints:
        method_code = _build_typed_method_code(endpoint, base_path)
        methods.append(method_code)

    code = f'''"""自动生成的 API 客户端 - {tag}

从 OpenAPI 规范生成，基于 df-test-framework v3.38.0 最佳实践。
类名: {class_name}
模块标识: {tag_id}

v3.38.0 特性:
- ✅ 强类型方法签名（Pydantic 请求/响应模型）
- ✅ BaseAPI 自动序列化请求模型
- ✅ BaseAPI 自动解析响应模型
- ✅ @api_class 装饰器自动注册 fixture
- ✅ IDE 智能提示和类型检查

v3.39.0 新增:
- ✅ 支持增量合并（--force 选项保留用户扩展）
- ✅ 用户扩展区域保留自定义代码

使用示例:
    # 方式1: 直接实例化
    from {project_name}.models.requests.{tag_snake} import XxxRequest
    from {project_name}.models.responses.{tag_snake} import XxxResponse

    api = {class_name}(http_client)
    request = XxxRequest(field="value")
    response: XxxResponse = api.xxx_method(request)

    # 方式2: 使用 fixture（推荐）
    def test_example({fixture_name}):
        request = XxxRequest(field="value")
        response = {fixture_name}.xxx_method(request)
        assert response.code == 200
"""

from typing import Any

from df_test_framework import BaseAPI, HttpClient
from df_test_framework.testing.decorators import api_class

{imports_code}


{AUTO_GENERATED_START}
{AUTO_GENERATED_WARNING}


@api_class("{fixture_name}")
class {class_name}(BaseAPI):
    """{tag} API 客户端

    自动从 OpenAPI 规范生成。

    接口前缀: {base_path or "/"}
    Fixture 名称: {fixture_name}
    """

    def __init__(self, http_client: HttpClient):
        super().__init__(http_client)
        self.base_path = "{base_path}"

{chr(10).join(methods)}


{AUTO_GENERATED_END}


{USER_EXTENSIONS_START}
{USER_EXTENSIONS_HINT}


__all__ = ["{class_name}"]
'''

    return code


def _build_typed_method_code(endpoint: APIEndpoint, base_path: str = "") -> str:
    """构建类型化的方法代码

    v3.38.0 改进:
    - request: XXXRequest 参数
    - -> XXXResponse 返回值
    - 使用 BaseAPI 的 model 参数
    """
    # 生成方法名（使用简化后的名称）
    simplified_name = _simplify_operation_id(endpoint.operation_id)
    method_name = to_snake_case(simplified_name)

    # 路径参数
    path_params = endpoint.get_path_params()
    query_params = endpoint.get_query_params()

    # 请求模型（使用简化后的名称）
    request_model_name = None
    if endpoint.request_body:
        request_model_name = to_pascal_case(simplified_name) + "Request"

    # 响应模型（使用简化后的名称）
    response_model_name = None
    if endpoint.get_success_response():
        response_model_name = to_pascal_case(simplified_name) + "Response"

    # 构建方法参数（必填参数在前，可选参数在后）
    # 分离必填和可选的 query 参数
    required_query_params = [qp for qp in query_params if qp.required]
    optional_query_params = [qp for qp in query_params if not qp.required]

    params = []
    # 1. 必填参数（无默认值）
    if path_params:
        params.extend([f"{p.name}: {_get_python_type(p.schema)}" for p in path_params])
    if required_query_params:
        params.extend([f"{qp.name}: {_get_python_type(qp.schema)}" for qp in required_query_params])
    if request_model_name:
        params.append(f"request: {request_model_name}")

    # 2. 可选参数（有默认值）
    if optional_query_params:
        params.extend(
            [
                f"{qp.name}: {_get_python_type(qp.schema)} | None = None"
                for qp in optional_query_params
            ]
        )
    if not request_model_name and endpoint.method.upper() in ["POST", "PUT", "PATCH"]:
        params.append("data: dict[str, Any] | None = None")

    params_str = ", ".join(params)

    # 返回类型
    return_type = response_model_name if response_model_name else "dict[str, Any]"

    # 构建相对路径
    path = endpoint.path
    if base_path and path.startswith(base_path):
        path = path[len(base_path) :]
    if not path:
        path = "/"

    # HTTP 方法
    http_method = endpoint.method.lower()

    # 生成文档字符串
    summary = endpoint.summary or method_name.replace("_", " ").title()
    doc_lines = [f'"""{summary}']

    if endpoint.description:
        doc_lines.append("")
        doc_lines.append(f"        {endpoint.description}")

    if params:
        doc_lines.append("")
        doc_lines.append("        Args:")
        # 按照参数顺序生成文档：必填参数在前，可选参数在后
        for p in path_params:
            doc_lines.append(f"            {p.name}: {p.description or p.name}")
        for qp in required_query_params:
            doc_lines.append(f"            {qp.name}: {qp.description or qp.name}")
        if request_model_name:
            doc_lines.append(f"            request: {request_model_name} 请求模型")
        for qp in optional_query_params:
            doc_lines.append(f"            {qp.name}: {qp.description or qp.name}（可选）")
        if not request_model_name and endpoint.method.upper() in ["POST", "PUT", "PATCH"]:
            doc_lines.append("            data: 请求数据（可选）")

    doc_lines.append("")
    doc_lines.append("        Returns:")
    doc_lines.append(f"            {return_type}: 响应数据")
    doc_lines.append('        """')

    doc = "\n".join(doc_lines)

    # 构建路径表达式
    if path_params:
        path_expr = f'f"{{self.base_path}}{path}"'
    else:
        path_expr = f'self.base_path + "{path}"'

    # 构建方法调用
    call_args = [path_expr]
    if request_model_name:
        call_args.append("json=request")
    elif endpoint.method.upper() in ["POST", "PUT", "PATCH"] and "data" in params_str:
        call_args.append("json=data")

    # 添加 query 参数（如果有）
    if query_params:
        # 构建 params 字典
        query_param_names = [qp.name for qp in query_params]
        if len(query_param_names) == 1:
            # 单个参数，简化写法
            qp_name = query_param_names[0]
            call_args.append(f'params={{"{qp_name}": {qp_name}}}')
        else:
            # 多个参数，使用字典
            params_dict = ", ".join([f'"{qp.name}": {qp.name}' for qp in query_params])
            call_args.append(f"params={{{params_dict}}}")

    # 添加 model 参数（如果有响应模型）
    if response_model_name:
        call_args.append(f"model={response_model_name}")

    call_str = ", ".join(call_args)

    # 生成方法体
    if response_model_name:
        return_stmt = f"return self.{http_method}({call_str})"
    else:
        return_stmt = (
            f"response = self.http_client.{http_method}({call_str})\n        return response.json()"
        )

    code = f"""    def {method_name}(self{", " + params_str if params_str else ""}) -> {return_type}:
        {doc}
        {return_stmt}
"""

    return code


def _get_common_path_prefix(paths: list[str]) -> str:
    """获取路径列表的公共前缀"""
    if not paths:
        return ""

    # 将路径分割为部分
    split_paths = [p.split("/") for p in paths]
    if not split_paths:
        return ""

    # 找到公共前缀
    common = []
    for parts in zip(*split_paths):
        # 跳过路径参数 {id}
        if all(p == parts[0] and not p.startswith("{") for p in parts):
            common.append(parts[0])
        else:
            break

    return "/".join(common) if common else ""


# ========== Phase 3: 测试代码生成 ==========


def _generate_tests_v2(
    endpoints: list[APIEndpoint],
    project_name: str,
    output_dir: Path,
    *,
    parser: OpenAPIParser | None = None,
    force: bool = False,
    merge: bool = False,
) -> list[tuple[str, Path]]:
    """生成测试用例

    v3.38.0 改进:
    - 使用类型化的 API 客户端
    - 更清晰的测试结构

    v3.39.0 改进:
    - 支持增量合并模式（merge=True）

    v3.41.1 改进:
    - 接受 parser 参数用于解析 $ref 引用
    """
    generated: list[tuple[str, Path]] = []

    # 按标签分组
    endpoints_by_tag: dict[str, list[APIEndpoint]] = defaultdict(list)
    for endpoint in endpoints:
        tag = endpoint.tags[0] if endpoint.tags else "default"
        endpoints_by_tag[tag].append(endpoint)

    tests_dir = output_dir / "tests" / "api"
    tests_dir.mkdir(parents=True, exist_ok=True)

    # 为每个标签生成一个测试文件（使用 ASCII 标识符处理中文 tag）
    for tag, tag_endpoints in endpoints_by_tag.items():
        tag_id = to_ascii_identifier(tag)
        file_name = f"test_{tag_id}_api.py"
        file_path = tests_dir / file_name

        # 生成测试代码
        # v3.41.1: 传递 parser 用于解析 $ref 引用
        content = _build_typed_test_code(tag, tag_id, tag_endpoints, project_name, parser=parser)

        success, action = create_file_with_merge(file_path, content, force=force, merge=merge)

        if success:
            generated.append(("Test", file_path.relative_to(output_dir)))
            if action == "merged":
                print(f"  🔀 合并: {file_path.name}")
        elif "skipped" in action:
            print(f"  ⏭️  跳过: {file_path.name}（已存在）")
        else:
            print(f"  ⚠️  {action}: {file_path.name}")

    return generated


def _build_typed_test_code(
    tag: str,
    tag_id: str,
    endpoints: list[APIEndpoint],
    project_name: str,
    *,
    parser: OpenAPIParser | None = None,
) -> str:
    """构建类型化的测试代码（v3.41.0 增强版）

    Args:
        tag: 原始 tag 名称（用于注释和 allure feature）
        tag_id: ASCII 标识符（用于类名、fixture名、导入路径）
        endpoints: API 端点列表
        project_name: 项目名称
        parser: OpenAPI 解析器（用于解析 $ref 引用）

    v3.41.0 增强:
    - 智能生成分页查询请求示例
    - 前置查询生成
    - 中文测试标题
    - 智能区分 smoke/regression 测试
    - 增强断言
    - 自动生成 E2E 和负向测试
    - 自动生成 import 语句

    v3.41.1 增强:
    - 接受 parser 参数用于解析 $ref 引用
    """
    class_name = "Test" + to_pascal_case(tag_id) + "API"
    api_fixture_name = tag_id + "_api"
    tag_snake = tag_id

    # v3.41.0: 收集需要导入的请求模型
    request_models_to_import = set()
    for endpoint in endpoints:
        simplified_name = _simplify_operation_id(endpoint.operation_id)
        request_model = to_pascal_case(simplified_name) + "Request"
        if endpoint.request_body:
            request_models_to_import.add(request_model)
        # 前置查询也需要导入列表查询的请求模型
        if _needs_precondition_query(endpoint.operation_id, endpoint.summary):
            list_info = _find_list_endpoint(endpoints, endpoint)
            # v3.41.1: 只有当列表接口有请求体时才添加到导入
            if list_info and list_info[1]:
                request_models_to_import.add(list_info[1])

    # 生成测试方法（使用简化后的名称）
    test_methods = []
    for endpoint in endpoints:
        simplified_name = _simplify_operation_id(endpoint.operation_id)
        api_method = to_snake_case(simplified_name)

        # v3.41.0: 传递 endpoints 列表用于前置查询
        # v3.41.1: 传递 parser 用于解析 $ref 引用
        method_code = _build_typed_test_method_code(
            endpoint,
            api_fixture_name,
            api_method,
            project_name,
            tag_id,
            endpoints=endpoints,
            parser=parser,
        )
        test_methods.append(method_code)

    # v3.41.0: 生成 E2E 测试类
    e2e_test_class = _build_e2e_test_class(tag, tag_id, endpoints, api_fixture_name, project_name)

    # v3.41.0: 生成负向测试类
    negative_test_class = _build_negative_test_class(
        tag, tag_id, endpoints, api_fixture_name, project_name
    )

    # v3.41.0: 生成请求模型导入语句
    if request_models_to_import:
        imports_code = (
            f"from {project_name}.models.requests.{tag_snake} import (\n    "
            + ",\n    ".join(sorted(request_models_to_import))
            + ",\n)"
        )
    else:
        imports_code = ""

    code = f'''"""自动生成的测试文件 - {tag}

从 OpenAPI 规范生成，基于 df-test-framework v3.41.0 最佳实践。
测试类: {class_name}
模块标识: {tag_id}

v3.41.0 新增:
- ✅ 智能生成分页查询请求示例（不再是空占位符）
- ✅ 前置查询生成（详情/更新/删除操作自动查询获取ID）
- ✅ 中文测试标题
- ✅ 智能区分 smoke/regression 测试
- ✅ 增强的列表查询断言
- ✅ 自动生成 E2E 流程测试
- ✅ 自动生成负向测试

v3.39.0 特性:
- ✅ 支持增量合并（--force 选项保留用户扩展）
- ✅ 用户扩展区域保留自定义测试

使用方法:
    pytest tests/api/test_{tag_snake}_api.py -v
    pytest tests/api/test_{tag_snake}_api.py -v -k "smoke"  # 仅运行 smoke 测试
    pytest tests/api/test_{tag_snake}_api.py -v -k "e2e"    # 仅运行 E2E 测试

前置条件:
    在 tests/conftest.py 中添加:
        from df_test_framework.testing.decorators import load_api_fixtures

        load_api_fixtures(globals(), apis_package="{project_name}.apis")
"""

import pytest
import allure
from assertpy import assert_that

from df_test_framework import attach_json, step, DataGenerator

{imports_code}


{AUTO_GENERATED_START}
{AUTO_GENERATED_WARNING}


@allure.feature("{tag}")
class {class_name}:
    """{tag} API 测试类

    自动从 OpenAPI 规范生成。

    Fixture 依赖 (v3.41.0+):
        - {api_fixture_name}: API 客户端（由 @api_class 自动注册）
        - cleanup: 数据清理管理器（按需使用）

    Note:
        allure_observer 是 autouse fixture，无需声明即可自动记录请求/响应到 Allure
    """

{chr(10).join(test_methods)}

{e2e_test_class}
{negative_test_class}

{AUTO_GENERATED_END}


{USER_EXTENSIONS_START}
{USER_EXTENSIONS_HINT}
'''

    return code


def _build_e2e_test_class(
    tag: str, tag_id: str, endpoints: list[APIEndpoint], api_fixture: str, project_name: str
) -> str:
    """生成 E2E 测试类

    v3.40.0: 自动生成 CRUD 流程测试
    """
    # 查找 CRUD 操作
    create_endpoint = None
    list_endpoint = None
    detail_endpoint = None
    update_endpoint = None
    delete_endpoint = None

    for ep in endpoints:
        op_id = ep.operation_id or ""
        if _is_create_operation(op_id, ep.summary) and not create_endpoint:
            create_endpoint = ep
        elif _is_list_query_operation(op_id, ep.summary) and not list_endpoint:
            list_endpoint = ep
        elif _is_detail_operation(op_id, ep.summary) and not detail_endpoint:
            detail_endpoint = ep
        elif _is_update_operation(op_id, ep.summary) and not update_endpoint:
            update_endpoint = ep
        elif _is_delete_operation(op_id, ep.summary) and not delete_endpoint:
            delete_endpoint = ep

    # 如果没有完整的 CRUD 操作，不生成 E2E 测试
    if not (create_endpoint and list_endpoint):
        return ""

    class_name = "Test" + to_pascal_case(tag_id) + "E2E"

    # 生成方法名
    def get_method_name(ep):
        simplified = _simplify_operation_id(ep.operation_id)
        return to_snake_case(simplified)

    create_method = get_method_name(create_endpoint) if create_endpoint else None
    list_method = get_method_name(list_endpoint) if list_endpoint else None
    detail_method = get_method_name(detail_endpoint) if detail_endpoint else None
    update_method = get_method_name(update_endpoint) if update_endpoint else None
    delete_method = get_method_name(delete_endpoint) if delete_endpoint else None

    # 生成请求模型名称
    def get_request_model(ep):
        simplified = _simplify_operation_id(ep.operation_id)
        return to_pascal_case(simplified) + "Request"

    create_request = get_request_model(create_endpoint) if create_endpoint else None
    list_request = get_request_model(list_endpoint) if list_endpoint else None

    # 构建 E2E 测试代码
    e2e_steps = []

    # 创建步骤
    if create_endpoint:
        e2e_steps.append(f"""
        # 1. 创建数据
        with step("创建测试数据"):
            test_id = DataGenerator.test_id("E2E")
            create_request = {create_request}(
                # TODO: 根据实际需求填充创建参数
            )
            create_response = {api_fixture}.{create_method}(create_request)
            assert_that(create_response.status).is_in("ok", "success")""")

    # 查询列表验证
    if list_endpoint:
        e2e_steps.append(f"""
        # 2. 查询列表验证
        with step("查询列表验证创建成功"):
            list_request = {list_request}(pagination={{"pageSize": 10, "current": 1}})
            list_response = {api_fixture}.{list_method}(list_request)
            assert_that(list_response.status).is_in("ok", "success")
            # 获取创建的数据 ID
            if list_response.data and list_response.data.get("list"):
                created_id = list_response.data["list"][0].get("id")
            else:
                pytest.skip("未找到创建的数据")""")

    # 查询详情验证
    if detail_endpoint:
        detail_request = get_request_model(detail_endpoint)
        e2e_steps.append(f"""
        # 3. 查询详情验证
        with step("查询详情验证"):
            detail_request = {detail_request}(id=created_id)
            detail_response = {api_fixture}.{detail_method}(detail_request)
            assert_that(detail_response.status).is_in("ok", "success")""")

    # 更新验证
    if update_endpoint:
        update_request = get_request_model(update_endpoint)
        e2e_steps.append(f"""
        # 4. 更新数据
        with step("更新数据"):
            update_request = {update_request}(
                id=created_id,
                # TODO: 根据实际需求填充更新参数
            )
            update_response = {api_fixture}.{update_method}(update_request)
            assert_that(update_response.status).is_in("ok", "success")""")

    # 删除验证
    if delete_endpoint:
        delete_request = get_request_model(delete_endpoint)
        e2e_steps.append(f"""
        # 5. 删除数据
        with step("删除数据"):
            delete_request = {delete_request}(id=created_id)
            delete_response = {api_fixture}.{delete_method}(delete_request)
            assert_that(delete_response.status).is_in("ok", "success")""")

    e2e_code = "\n".join(e2e_steps)

    return f'''
@allure.feature("{tag}")
@allure.story("E2E 流程测试")
class {class_name}:
    """{tag} E2E 流程测试

    v3.41.0 自动生成：完整的 CRUD 流程测试
    """

    @allure.title("完整 CRUD 流程测试")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_crud_flow(self, {api_fixture}, cleanup):
        """完整的创建-查询-更新-删除流程测试

        测试步骤:
        1. 创建数据
        2. 查询列表验证
        3. 查询详情验证
        4. 更新数据
        5. 删除数据
        """{e2e_code}
'''


def _build_negative_test_class(
    tag: str, tag_id: str, endpoints: list[APIEndpoint], api_fixture: str, project_name: str
) -> str:
    """生成负向测试类

    v3.40.0: 自动生成边界条件和错误场景测试
    """
    # 查找详情和删除操作
    detail_endpoint = None
    delete_endpoint = None

    for ep in endpoints:
        op_id = ep.operation_id or ""
        if _is_detail_operation(op_id, ep.summary) and not detail_endpoint:
            detail_endpoint = ep
        elif _is_delete_operation(op_id, ep.summary) and not delete_endpoint:
            delete_endpoint = ep

    # 如果没有详情或删除操作，不生成负向测试
    if not detail_endpoint and not delete_endpoint:
        return ""

    class_name = "Test" + to_pascal_case(tag_id) + "Negative"

    def get_method_name(ep):
        simplified = _simplify_operation_id(ep.operation_id)
        return to_snake_case(simplified)

    def get_request_model(ep):
        simplified = _simplify_operation_id(ep.operation_id)
        return to_pascal_case(simplified) + "Request"

    negative_tests = []

    # 查询不存在的数据
    if detail_endpoint:
        detail_method = get_method_name(detail_endpoint)
        detail_request = get_request_model(detail_endpoint)
        negative_tests.append(f'''
    @allure.title("查询不存在的数据")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_find_non_existent(self, {api_fixture}):
        """查询不存在的数据应返回空或错误"""
        with step("查询不存在的ID"):
            request = {detail_request}(id=999999999)
            response = {api_fixture}.{detail_method}(request)

        with step("验证响应"):
            # 应该返回空数据或错误码
            # 具体行为取决于后端实现
            assert_that(response).is_not_none()''')

    # 删除不存在的数据
    if delete_endpoint:
        delete_method = get_method_name(delete_endpoint)
        delete_request = get_request_model(delete_endpoint)
        negative_tests.append(f'''
    @allure.title("删除不存在的数据")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_delete_non_existent(self, {api_fixture}):
        """删除不存在的数据应返回错误"""
        with step("删除不存在的ID"):
            request = {delete_request}(id=999999999)
            response = {api_fixture}.{delete_method}(request)

        with step("验证响应"):
            # 应该返回错误或特定状态
            assert_that(response).is_not_none()''')

    negative_code = "\n".join(negative_tests)

    return f'''
@allure.feature("{tag}")
@allure.story("负向测试")
class {class_name}:
    """{tag} 负向测试

    v3.41.0 自动生成：边界条件和错误场景测试
    """
{negative_code}
'''


# ========== v3.40.0 优化：操作类型识别和智能代码生成 ==========

# 操作类型中文映射
OPERATION_TYPE_CN = {
    "find": "查询",
    "get": "获取",
    "list": "列表",
    "query": "查询",
    "search": "搜索",
    "add": "新增",
    "create": "创建",
    "insert": "插入",
    "save": "保存",
    "update": "更新",
    "modify": "修改",
    "edit": "编辑",
    "delete": "删除",
    "del": "删除",
    "remove": "移除",
    "export": "导出",
    "import": "导入",
    "refresh": "刷新",
    "sync": "同步",
    # v3.41.0: 添加审批流程相关操作
    "confirm": "确认",
    "cancel": "取消",
    "approve": "审批",
    "reject": "拒绝",
    "submit": "提交",
    "revoke": "撤销",
    "enable": "启用",
    "disable": "禁用",
}


def _is_detail_operation(operation_id: str | None, summary: str | None) -> bool:
    """判断是否是详情查询操作（需要有效ID）

    详情查询操作特征:
        - findById, getById, findDetail, getDetail
        - 包含 "byId", "ById", "detail" 等关键词

    Args:
        operation_id: OpenAPI 的 operationId
        summary: 接口摘要

    Returns:
        True 如果是详情查询操作
    """
    detail_patterns = ("byid", "detail", "info", "getone", "findone")

    if operation_id:
        op_lower = operation_id.lower()
        for pattern in detail_patterns:
            if pattern in op_lower:
                return True

    if summary:
        summary_lower = summary.lower()
        cn_detail_keywords = ("详情", "详细", "单个", "根据id", "根据ID")
        for keyword in cn_detail_keywords:
            if keyword in summary_lower:
                return True

    return False


def _is_update_operation(operation_id: str | None, summary: str | None) -> bool:
    """判断是否是更新操作（需要有效ID）"""
    update_prefixes = ("update", "modify", "edit", "change", "set")

    if operation_id:
        op_lower = operation_id.lower()
        for prefix in update_prefixes:
            if op_lower.startswith(prefix):
                return True
            if f"_{prefix}" in op_lower:
                return True

    if summary:
        summary_lower = summary.lower()
        cn_keywords = ("更新", "修改", "编辑")
        for keyword in cn_keywords:
            if keyword in summary_lower:
                return True

    return False


def _is_delete_operation(operation_id: str | None, summary: str | None) -> bool:
    """判断是否是删除操作（需要有效ID）"""
    delete_prefixes = ("delete", "del", "remove")

    if operation_id:
        op_lower = operation_id.lower()
        for prefix in delete_prefixes:
            if op_lower.startswith(prefix):
                return True
            if f"_{prefix}" in op_lower:
                return True

    if summary:
        summary_lower = summary.lower()
        cn_keywords = ("删除", "移除")
        for keyword in cn_keywords:
            if keyword in summary_lower:
                return True

    return False


def _is_list_query_operation(operation_id: str | None, summary: str | None) -> bool:
    """判断是否是列表查询操作（通常有分页）

    列表查询操作特征:
        - findList, getList, queryList, searchList
        - find + 复数名词（如 findSuppliers）
        - 不包含 ById, Detail 等详情关键词
    """
    if _is_detail_operation(operation_id, summary):
        return False

    list_patterns = ("list", "all", "page", "search", "query")

    if operation_id:
        op_lower = operation_id.lower()
        # 以 find/get 开头且包含 list 或复数形式
        if op_lower.startswith(("find", "get", "query", "search")):
            for pattern in list_patterns:
                if pattern in op_lower:
                    return True
            # 检查是否是复数形式（简单判断：以 s 结尾但不是 ss）
            if op_lower.endswith("s") and not op_lower.endswith("ss"):
                return True

    if summary:
        summary_lower = summary.lower()
        cn_keywords = ("列表", "分页", "查询列表")
        for keyword in cn_keywords:
            if keyword in summary_lower:
                return True

    return False


def _needs_precondition_query(operation_id: str | None, summary: str | None) -> bool:
    """判断是否需要前置查询获取有效ID

    以下操作需要前置查询:
    - 详情查询（findById, getDetail）
    - 更新操作（update, modify）
    - 删除操作（delete, remove）
    """
    return (
        _is_detail_operation(operation_id, summary)
        or _is_update_operation(operation_id, summary)
        or _is_delete_operation(operation_id, summary)
    )


def _find_list_endpoint(endpoints: list, current_endpoint) -> tuple[str, str | None] | None:
    """查找对应的列表查询接口

    v3.41.0: 智能匹配同类实体的列表接口
    v3.41.1: 只返回有请求体的端点的 request_model，没有请求体的返回 None

    Args:
        endpoints: 同一 tag 下的所有端点
        current_endpoint: 当前端点

    Returns:
        (api_method_name, request_model_name | None) 或 None
        - request_model_name 为 None 时表示该列表接口没有请求体

    Example:
        updateSupplier -> findSupplierList
        updateSupplierAccount -> findSupplierAccountList
    """
    # 提取当前操作的实体名称
    current_simplified = _simplify_operation_id(current_endpoint.operation_id)
    current_lower = current_simplified.lower()

    # 移除操作前缀，获取实体名
    current_entity = current_lower
    for prefix in ["update", "modify", "edit", "delete", "del", "remove", "find", "get"]:
        if current_lower.startswith(prefix + "_"):
            current_entity = current_lower[len(prefix) + 1 :]
            break
        elif current_lower.startswith(prefix):
            current_entity = current_lower[len(prefix) :]
            break

    # 收集所有列表查询接口
    # v3.41.1: 优先收集有请求体的列表接口
    list_endpoints_with_body = []
    list_endpoints_without_body = []
    for ep in endpoints:
        if _is_list_query_operation(ep.operation_id, ep.summary):
            simplified_name = _simplify_operation_id(ep.operation_id)
            api_method = to_snake_case(simplified_name)
            has_request_body = ep.request_body is not None
            request_model = (
                to_pascal_case(simplified_name) + "Request" if has_request_body else None
            )
            ep_data = (ep, api_method, request_model, simplified_name.lower())
            if has_request_body:
                list_endpoints_with_body.append(ep_data)
            else:
                list_endpoints_without_body.append(ep_data)

    # 合并：优先考虑有请求体的端点
    list_endpoints = list_endpoints_with_body + list_endpoints_without_body

    if not list_endpoints:
        return None

    # 优先匹配同类实体的列表接口
    for ep, api_method, request_model, ep_lower in list_endpoints:
        # 提取列表接口的实体名
        list_entity = ep_lower
        for prefix in ["find", "get", "list", "query", "search"]:
            if ep_lower.startswith(prefix + "_"):
                list_entity = ep_lower[len(prefix) + 1 :]
                break
            elif ep_lower.startswith(prefix):
                list_entity = ep_lower[len(prefix) :]
                break

        # 移除 _list 后缀
        list_entity = list_entity.rstrip("_list").rstrip("list")

        # 精确匹配或包含匹配
        if current_entity == list_entity:
            return (api_method, request_model)
        # 当前实体以列表实体开头（如 supplier_account 包含 supplier_account）
        if current_entity.startswith(list_entity) and list_entity:
            return (api_method, request_model)

    # 如果没有精确匹配，返回第一个列表接口作为备选
    return (list_endpoints[0][1], list_endpoints[0][2])


def _generate_request_example(
    request_schema: dict, request_model_name: str, is_create: bool = False
) -> str:
    """根据 schema 生成智能请求示例

    v3.40.0: 智能识别分页、排序等常见字段，生成可运行的示例代码

    Args:
        request_schema: 请求体的 schema
        request_model_name: 请求模型名称
        is_create: 是否是创建操作

    Returns:
        生成的请求示例代码
    """
    props = request_schema.get("properties", {})
    if not props:
        return f"{request_model_name}()"

    example_fields = []

    # 1. 分页字段
    if "pagination" in props:
        example_fields.append('pagination={"pageSize": 10, "current": 1}')

    # 2. 排序字段
    if "sortName" in props or "sort_name" in props:
        example_fields.append('sort_name="id"')
    if "sortType" in props or "sort_type" in props:
        example_fields.append('sort_type="desc"')

    # 3. 创建操作的常见字段
    if is_create:
        # 名称字段
        for name_field in ["name", "supplierName", "supplier_name", "ruleName", "rule_name"]:
            if name_field in props:
                snake_name = to_snake_case(name_field)
                example_fields.append(f'{snake_name}=f"自动化测试_{{test_id}}"')
                break

        # 备注字段
        if "remarks" in props:
            example_fields.append('remarks=f"自动化测试创建 - {test_id}"')

        # 状态字段
        if "status" in props:
            example_fields.append("status=1")

        # 有效标志
        for eff_field in ["isEffective", "is_effective"]:
            if eff_field in props:
                example_fields.append("is_effective=1")
                break

    if example_fields:
        fields_str = ",\n                ".join(example_fields)
        return f"{request_model_name}(\n                {fields_str}\n            )"
    else:
        return f"{request_model_name}()"


def _split_camel_case(name: str) -> str:
    """将驼峰命名拆分为空格分隔的单词

    v3.41.0: 改进标题可读性

    Example:
        >>> _split_camel_case("SupplierAccountList")
        "Supplier Account List"
        >>> _split_camel_case("findById")
        "find By Id"
    """
    # 在大写字母前插入空格
    result = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    # 处理连续大写字母
    result = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", result)
    return result


def _generate_chinese_title(operation_id: str | None, summary: str | None) -> str:
    """生成中文测试标题

    v3.41.0: 优先使用 Swagger summary，否则智能翻译，并拆分驼峰命名

    Args:
        operation_id: OpenAPI 的 operationId
        summary: 接口摘要

    Returns:
        中文测试标题
    """
    # 优先使用 summary（如果是中文）
    if summary:
        # 检查是否包含中文字符
        if any("\u4e00" <= c <= "\u9fff" for c in summary):
            return summary

    # 根据操作类型生成中文标题
    if not operation_id:
        return summary or "未知操作"

    op_lower = operation_id.lower()
    simplified = _simplify_operation_id(operation_id)

    # 尝试识别操作类型
    for en_prefix, cn_prefix in OPERATION_TYPE_CN.items():
        if op_lower.startswith(en_prefix):
            # 提取实体名（去掉操作前缀）
            entity_part = simplified[len(en_prefix) :].strip("_")
            if entity_part:
                # v3.41.0: 将 snake_case 转为 PascalCase 再拆分
                pascal_name = to_pascal_case(entity_part)
                entity_name = _split_camel_case(pascal_name)
                # 特殊处理 ById
                if "by_id" in entity_part.lower() or "byid" in entity_part.lower():
                    return f"根据ID{cn_prefix}"
                return f"{cn_prefix} {entity_name}"
            return cn_prefix

    # 默认使用 summary 或格式化的 operation_id
    if summary:
        return summary
    # v3.41.0: 拆分驼峰命名
    pascal_name = to_pascal_case(simplified)
    return _split_camel_case(pascal_name)


def _get_pytest_mark(operation_id: str | None, summary: str | None) -> str:
    """根据操作类型获取 pytest mark

    v3.40.0: 智能区分 smoke 和 regression 测试

    规则:
    - smoke: 核心查询（列表、详情）、创建操作
    - regression: 更新、删除、导出、刷新等

    Returns:
        "smoke" 或 "regression"
    """
    if not operation_id:
        return "smoke"

    op_lower = operation_id.lower()

    # smoke 测试：核心功能
    smoke_patterns = ("findlist", "getlist", "findbyid", "getbyid", "add", "create", "insert")
    for pattern in smoke_patterns:
        if pattern in op_lower:
            return "smoke"

    # 简单的列表查询也是 smoke
    if _is_list_query_operation(operation_id, summary):
        return "smoke"

    # 其他都是 regression
    return "regression"


def _is_create_operation(operation_id: str | None, summary: str | None) -> bool:
    """判断是否是创建操作（需要数据清理）

    根据 operation_id 和 summary 的语义判断操作类型。

    创建类操作（需要清理）:
        - add*, create*, insert*, save*, new*, register*

    非创建类操作（不需要清理）:
        - find*, get*, list*, query*, search*, export* (查询)
        - delete*, remove*, del* (删除)
        - update*, modify*, edit*, change* (更新)
        - refresh*, sync*, init* (刷新/同步)

    Args:
        operation_id: OpenAPI 的 operationId
        summary: 接口摘要

    Returns:
        True 如果是创建操作，需要清理
    """
    # 创建类操作的前缀
    create_prefixes = ("add", "create", "insert", "save", "new", "register")

    # 检查 operation_id
    if operation_id:
        op_lower = operation_id.lower()
        # 检查是否以创建类前缀开头
        for prefix in create_prefixes:
            if op_lower.startswith(prefix):
                return True
            # 也检查下划线分隔的情况，如 "supplier_add"
            if f"_{prefix}" in op_lower or f"{prefix}_" in op_lower:
                return True

    # 检查 summary
    if summary:
        summary_lower = summary.lower()
        for prefix in create_prefixes:
            if prefix in summary_lower:
                return True

    return False


def _is_query_operation(operation_id: str | None, summary: str | None) -> bool:
    """判断是否是查询操作

    v3.39.1 新增：用于生成更精确的断言模板。

    查询类操作特征:
        - find*, get*, list*, query*, search*, select*, fetch*

    Args:
        operation_id: OpenAPI 的 operationId
        summary: 接口摘要

    Returns:
        True 如果是查询操作
    """
    # 查询类操作的前缀
    query_prefixes = ("find", "get", "list", "query", "search", "select", "fetch", "load")

    # 检查 operation_id
    if operation_id:
        op_lower = operation_id.lower()
        for prefix in query_prefixes:
            if op_lower.startswith(prefix):
                return True
            # 也检查下划线分隔的情况
            if f"_{prefix}" in op_lower or f"{prefix}_" in op_lower:
                return True

    # 检查 summary
    if summary:
        summary_lower = summary.lower()
        # 中文关键词
        cn_query_keywords = ("查询", "获取", "列表", "搜索", "查找")
        for keyword in cn_query_keywords:
            if keyword in summary_lower:
                return True
        # 英文关键词
        for prefix in query_prefixes:
            if prefix in summary_lower:
                return True

    return False


def _build_typed_test_method_code(
    endpoint: APIEndpoint,
    api_fixture: str,
    api_method: str,
    project_name: str,
    tag_id: str,
    endpoints: list | None = None,
    parser: OpenAPIParser | None = None,
) -> str:
    """构建类型化的测试方法代码（v3.40.0 增强版）

    使用 AAA（Arrange-Act-Assert）模式：
    - Arrange: 准备测试数据（包括路径参数和请求体）
    - Act: 调用接口
    - Assert: 验证响应

    v3.40.0 增强:
    - 智能生成分页查询请求示例（不再是空占位符）
    - 前置查询生成（详情/更新/删除操作自动查询获取ID）
    - 中文测试标题
    - 智能区分 smoke/regression 测试
    - 增强的列表查询断言
    """
    test_name = f"test_{api_method}"

    # v3.40.0: 生成中文测试标题
    title = _generate_chinese_title(endpoint.operation_id, endpoint.summary)

    # v3.40.0: 智能获取 pytest mark
    pytest_mark = _get_pytest_mark(endpoint.operation_id, endpoint.summary)

    # 检查是否有请求体
    has_request_model = endpoint.request_body is not None

    # 获取路径参数和 query 参数（分离必填和可选）
    path_params = endpoint.get_path_params()
    query_params = endpoint.get_query_params()
    required_query_params = [qp for qp in query_params if qp.required]
    optional_query_params = [qp for qp in query_params if not qp.required]
    has_path_params = bool(path_params)
    has_query_params = bool(query_params)

    # 判断操作类型
    needs_cleanup = _is_create_operation(endpoint.operation_id, endpoint.summary)
    is_list_query = _is_list_query_operation(endpoint.operation_id, endpoint.summary)
    needs_precondition = _needs_precondition_query(endpoint.operation_id, endpoint.summary)

    # 获取请求模型名称（使用简化后的名称）
    simplified_name = _simplify_operation_id(endpoint.operation_id)
    request_model = to_pascal_case(simplified_name) + "Request"

    # 获取请求 schema（用于智能生成示例）
    request_schema = {}
    if endpoint.request_body:
        request_schema = endpoint.request_body.get("schema", {})
        if "$ref" in request_schema and parser:
            request_schema = parser._resolve_ref(request_schema["$ref"])

    # v3.40.0: 查找列表查询接口（用于前置查询）
    list_api_info = None
    if needs_precondition and endpoints:
        list_api_info = _find_list_endpoint(endpoints, endpoint)

    # ========== Arrange 阶段 ==========
    arrange_parts = []
    imports_needed = []

    # v3.40.0: 如果需要前置查询，生成前置查询代码
    if needs_precondition and list_api_info:
        list_method, list_request_model = list_api_info
        # v3.41.1: 只有当列表接口有请求体时才添加到导入
        if list_request_model:
            imports_needed.append(list_request_model)
        if has_request_model:
            imports_needed.append(request_model)

        # 确定要获取的 ID 字段名
        id_field = "id"
        for param in path_params:
            if "id" in param.name.lower():
                id_field = param.name
                break

        # v3.41.1: 根据列表接口是否有请求体生成不同的代码
        if list_request_model:
            arrange_parts.append(f"""# 前置查询：获取有效的 {id_field}
            list_request = {list_request_model}(pagination={{"pageSize": 1, "current": 1}})
            list_response = {api_fixture}.{list_method}(list_request)
            assert_that(list_response.status).is_in("ok", "success")
            if not list_response.data or not list_response.data.get("list"):
                pytest.skip("没有可用的测试数据")
            {id_field} = list_response.data["list"][0].get("id")""")
        else:
            # 列表接口没有请求体，直接调用无参方法
            arrange_parts.append(f"""# 前置查询：获取有效的 {id_field}
            list_response = {api_fixture}.{list_method}()
            assert_that(list_response.status).is_in("ok", "success")
            if not list_response.data or not list_response.data.get("list"):
                pytest.skip("没有可用的测试数据")
            {id_field} = list_response.data["list"][0].get("id")""")

        # 更新/详情操作的请求体
        if has_request_model and not needs_cleanup:
            if _is_update_operation(endpoint.operation_id, endpoint.summary):
                arrange_parts.append(f"""
            # 构造更新请求
            existing_data = list_response.data["list"][0]
            request = {request_model}(
                id={id_field},
                # 保留原有数据，只修改需要更新的字段
            )""")
            else:
                # 详情查询
                arrange_parts.append(f"""
            # 构造详情查询请求
            request = {request_model}(id={id_field})""")

    # 1. 路径参数准备（如果没有前置查询）
    elif has_path_params:
        path_param_lines = []
        for param in path_params:
            param_type = _get_python_type(param.schema)
            if param_type == "int":
                path_param_lines.append(f"{param.name} = 1  # TODO: 替换为实际的 {param.name}")
            elif param_type == "str":
                path_param_lines.append(f'{param.name} = "test"  # TODO: 替换为实际的 {param.name}')
            else:
                path_param_lines.append(f"{param.name} = None  # TODO: 替换为实际的 {param.name}")
        arrange_parts.append("\n            ".join(path_param_lines))

    # 2. Query 参数准备
    if has_query_params and not needs_precondition:
        query_param_lines = []
        for param in query_params:
            param_type = _get_python_type(param.schema)
            if param_type == "int":
                query_param_lines.append(f"{param.name} = 1  # TODO: 替换为实际的 {param.name}")
            elif param_type == "str":
                query_param_lines.append(
                    f'{param.name} = "test"  # TODO: 替换为实际的 {param.name}'
                )
            else:
                query_param_lines.append(f"{param.name} = None  # TODO: 替换为实际的 {param.name}")
        arrange_parts.append("\n            ".join(query_param_lines))

    # 3. 请求体准备（如果没有在前置查询中处理）
    if not needs_precondition or not list_api_info:
        if needs_cleanup:
            # 创建操作：需要 DataGenerator 生成唯一标识符
            imports_needed.append(request_model)
            # v3.40.0: 使用智能请求示例生成
            request_example = _generate_request_example(
                request_schema, request_model, is_create=True
            )
            arrange_parts.append(f"""test_id = DataGenerator.test_id("TEST")  # 生成唯一标识符
            request = {request_example}""")
        elif has_request_model:
            # 有请求体但非创建操作（查询等）
            imports_needed.append(request_model)
            # v3.40.0: 使用智能请求示例生成
            request_example = _generate_request_example(
                request_schema, request_model, is_create=False
            )
            arrange_parts.append(f"request = {request_example}")

    # 组合 Arrange 代码
    if arrange_parts:
        arrange_code = "\n            ".join(arrange_parts)
    else:
        arrange_code = "# 无需准备请求数据\n            pass"

    # ========== Act 阶段 ==========
    # 构建调用参数（与 API 客户端方法签名顺序一致）
    call_args = []
    # 1. 路径参数（位置参数）
    if has_path_params:
        call_args.extend([p.name for p in path_params])
    # 2. 必填 query 参数（位置参数）
    if required_query_params:
        call_args.extend([qp.name for qp in required_query_params])
    # 3. 请求体（位置参数）
    if has_request_model or needs_cleanup:
        call_args.append("request")
    # 4. 可选 query 参数（关键字参数）
    if optional_query_params:
        call_args.extend([f"{qp.name}={qp.name}" for qp in optional_query_params])

    if call_args:
        act_code = f"response = {api_fixture}.{api_method}({', '.join(call_args)})"
    else:
        act_code = f"response = {api_fixture}.{api_method}()"

    # 清理注册（在 Act 之后）
    cleanup_code = ""
    if needs_cleanup:
        cleanup_code = """

            # 注册数据清理（创建成功后清理）
            # cleanup.add("resource_type", test_id)"""

    # ========== Assert 阶段 ==========
    # v3.40.0: 增强的断言模板
    if is_list_query:
        # 列表查询操作：验证列表结构和分页
        assert_code = """# 验证响应状态
            assert_that(response.status).is_in("ok", "success")
            # 验证列表数据结构
            assert_that(response.data).is_not_none()
            if "list" in response.data:
                assert_that(response.data["list"]).is_instance_of(list)
            # 验证分页信息
            if "pagination" in response.data:
                assert_that(response.data["pagination"]).contains_key("total")
                assert_that(response.data["pagination"]["total"]).is_greater_than_or_equal_to(0)"""
    elif _is_detail_operation(endpoint.operation_id, endpoint.summary):
        # 详情查询：验证返回的数据
        assert_code = """# 验证响应状态
            assert_that(response.status).is_in("ok", "success")
            # 验证详情数据
            assert_that(response.data).is_not_none()"""
    elif needs_cleanup:
        # 创建操作：验证创建成功
        assert_code = """# 验证创建成功
            assert_that(response.status).is_in("ok", "success")
            # 验证返回数据（如果有）
            # assert_that(response.data).is_not_none()"""
    elif _is_update_operation(endpoint.operation_id, endpoint.summary):
        # 更新操作
        assert_code = """# 验证更新成功
            assert_that(response.status).is_in("ok", "success")"""
    elif _is_delete_operation(endpoint.operation_id, endpoint.summary):
        # 删除操作
        assert_code = """# 验证删除成功
            assert_that(response.status).is_in("ok", "success")"""
    elif _is_query_operation(endpoint.operation_id, endpoint.summary):
        # 其他查询操作
        assert_code = """# 验证响应状态
            assert_that(response.status).is_in("ok", "success")
            assert_that(response.data).is_not_none()"""
    else:
        # 其他操作：通用断言
        assert_code = """# 验证响应状态
            assert_that(response.status).is_in("ok", "success")"""

    # 构建 fixture 参数和文档
    if needs_cleanup:
        fixture_params = f"{api_fixture}, cleanup"
        fixture_docs = f"""{api_fixture}: API 客户端（自动注册）
            cleanup: 数据清理管理器（创建操作需要）"""
    else:
        fixture_params = api_fixture
        fixture_docs = f"{api_fixture}: API 客户端（自动注册）"

    # 构建完整的测试方法（AAA 模式）
    code = f'''    @allure.title("{title}")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.{pytest_mark}
    def {test_name}(self, {fixture_params}):
        """{title}

        Args:
            {fixture_docs}

        Note:
            allure_observer 是 autouse fixture，自动记录请求/响应到 Allure 报告
        """
        # Arrange - 准备测试数据
        with step("准备测试数据"):
            {arrange_code}

        # Act - 执行操作
        with step("调用接口"):
            {act_code}{cleanup_code}

        # Assert - 验证结果
        with step("验证响应"):
            {assert_code}
'''

    return code


__all__ = ["generate_from_openapi"]
