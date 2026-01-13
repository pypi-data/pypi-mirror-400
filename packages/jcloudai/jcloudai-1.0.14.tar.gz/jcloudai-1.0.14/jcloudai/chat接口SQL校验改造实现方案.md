# Chat 接口 SQL 校验改造实现方案

## 1. 需求背景

### 1.1 当前问题
当前 chat 接口在 LLM 生成 SQL 后直接执行，缺少对生成 SQL 的校验环节。这可能导致：
- SQL 选择的字段与用户问题不匹配
- SQL 语法正确但语义错误
- 聚合函数、JOIN 条件等使用不当

### 1.2 改造目标
在 SQL 生成后、执行前增加一个 **SQL 校验节点**，使用 LLM 对生成的 SQL 进行二次校验：
- 根据数据源信息（表结构、字段定义）验证 SQL 正确性
- 根据用户问题验证 SQL 语义是否匹配
- 重点检查 SQL 选择的字段是否正确
- 如果发现问题，自动修正 SQL

---

## 2. 当前架构分析

### 2.1 现有流程
```
用户查询 → generate_code() → execute_code() → 返回结果
              ↓
         LLM 生成 SQL
              ↓
         直接执行 SQL
```

### 2.2 关键代码位置

| 组件 | 文件位置 | 说明 |
|------|----------|------|
| Agent._process_query() | jcloudai/agent/base.py:291 | 查询处理主流程 |
| Agent.generate_code() | jcloudai/agent/base.py:108 | 代码生成入口 |
| CodeGenerator.generate_code() | jcloudai/core/code_generation/base.py:29 | 代码生成核心 |
| Agent.execute_code() | jcloudai/agent/base.py:120 | 代码执行入口 |
| Agent._execute_sql_query() | jcloudai/agent/base.py:132 | SQL 执行方法 |

### 2.3 数据源信息获取
- **表结构信息**: `df.schema` (SemanticLayerSchema)
- **字段信息**: `df.schema.columns` (List[Column])
- **数据源类型**: `df.schema.source.type` (mysql/postgres/etc)
- **序列化方法**: `df.serialize_dataframe()` → 生成包含表名、字段、示例数据的 XML

---

## 3. 改造方案设计

### 3.1 新增流程
```
用户查询 → generate_code() → validate_sql() → execute_code() → 返回结果
              ↓                    ↓
         LLM 生成 SQL         LLM 校验 SQL
                                   ↓
                            正确 → 继续执行
                            错误 → 修正 SQL → 重新校验
```

### 3.2 核心组件设计

#### 3.2.1 新增 Prompt 模板
**文件**: `jcloudai/core/prompts/templates/validate_sql_prompt.tmpl`

```jinja2
<tables>
{% for df in context.dfs %}
{% include 'shared/dataframe.tmpl' with context %}
{% endfor %}
</tables>

## 用户问题
{{ user_query }}

## 生成的 SQL
```sql
{{ generated_sql }}
```

## 校验任务
请仔细检查上述 SQL 是否正确回答了用户的问题。重点检查：

1. **字段选择**: SQL 选择的字段是否与用户问题相关？是否遗漏了必要字段？
2. **条件过滤**: WHERE 条件是否正确理解了用户意图？

## 输出格式
请以 JSON 格式返回校验结果：
```json
{
    "is_valid": true/false,
    "issues": ["问题1", "问题2"],  // 如果有问题
    "corrected_sql": "修正后的SQL"  // 如果需要修正
}
```
```

#### 3.2.2 新增 Prompt 类
**文件**: `jcloudai/core/prompts/validate_sql_prompt.py`

```python
from jcloudai.core.prompts.base import BasePrompt

class ValidateSQLPrompt(BasePrompt):
    """Prompt to validate generated SQL against user query and schema."""
    
    template_path = "validate_sql_prompt.tmpl"
    
    def to_json(self):
        context = self.props["context"]
        user_query = self.props["user_query"]
        generated_sql = self.props["generated_sql"]
        
        return {
            "datasets": [df.to_json() for df in context.dfs],
            "user_query": user_query,
            "generated_sql": generated_sql,
        }
```

#### 3.2.3 新增 SQL 校验器
**文件**: `jcloudai/core/code_generation/sql_validator.py`

```python
import json
import re
from typing import Optional, Tuple
from jcloudai.agent.state import AgentState
from jcloudai.core.prompts.validate_sql_prompt import ValidateSQLPrompt

class SQLValidator:
    """Validates generated SQL using LLM."""
    
    def __init__(self, context: AgentState):
        self._context = context
        self._max_validation_retries = 2
    
    def validate_and_correct(
        self, 
        code: str, 
        user_query: str
    ) -> Tuple[str, bool]:
        """
        Validate SQL in the generated code and correct if needed.
        
        Returns:
            Tuple[str, bool]: (corrected_code, was_corrected)
        """
        # 1. 从代码中提取 SQL
        sql = self._extract_sql_from_code(code)
        if not sql:
            return code, False
        
        # 2. 调用 LLM 校验 SQL
        validation_result = self._validate_sql(sql, user_query)
        
        # 3. 如果 SQL 有效，直接返回
        if validation_result.get("is_valid", True):
            return code, False
        
        # 4. 如果 SQL 无效，使用修正后的 SQL 替换原代码
        corrected_sql = validation_result.get("corrected_sql")
        if corrected_sql:
            corrected_code = self._replace_sql_in_code(code, sql, corrected_sql)
            return corrected_code, True

        return code, False

    def _extract_sql_from_code(self, code: str) -> Optional[str]:
        """Extract SQL from execute_sql_query() call."""
        pattern = r'execute_sql_query\s*\(\s*["\'](.+?)["\']\s*\)'
        matches = re.findall(pattern, code, re.DOTALL)
        return matches[0] if matches else None

    def _validate_sql(self, sql: str, user_query: str) -> dict:
        """Call LLM to validate SQL."""
        prompt = ValidateSQLPrompt(
            context=self._context,
            user_query=user_query,
            generated_sql=sql,
        )

        response = self._context.config.llm.call(prompt, self._context)
        return self._parse_validation_response(response)

    def _parse_validation_response(self, response: str) -> dict:
        """Parse LLM validation response."""
        try:
            # 尝试提取 JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        return {"is_valid": True}  # 解析失败时默认有效

    def _replace_sql_in_code(self, code: str, old_sql: str, new_sql: str) -> str:
        """Replace SQL in the generated code."""
        return code.replace(old_sql, new_sql)
```

---

## 4. 代码修改详情

### 4.1 修改 Agent._process_query()

**文件**: `jcloudai/agent/base.py`

```python
def _process_query(self, query: str, output_type: Optional[str] = None):
    """Process a user query and return the result."""
    query_obj = UserQuery(query)
    self._state.logger.log(f"Question: {query_obj}")
    self._state.logger.log(
        f"Running PandasAI with {self._state.config.llm.type} LLM..."
    )

    self._state.output_type = output_type
    try:
        self._state.assign_prompt_id()

        # Generate code
        code = self.generate_code_with_retries(query_obj)

        # ========== 新增: SQL 校验 ==========
        if self._state.config.enable_sql_validation:
            code, was_corrected = self._validate_sql(code, str(query_obj))
            if was_corrected:
                self._state.logger.log("SQL was corrected by validation.")
        # ====================================

        # Execute code with retries
        result = self.execute_with_retries(code)

        self._state.logger.log("Response generated successfully.")
        return result

    except CodeExecutionError:
        return self._handle_exception(code)
```

### 4.2 新增 Agent._validate_sql() 方法

**文件**: `jcloudai/agent/base.py`

```python
def _validate_sql(self, code: str, user_query: str) -> Tuple[str, bool]:
    """
    Validate and potentially correct SQL in the generated code.

    Args:
        code: Generated Python code containing SQL
        user_query: Original user query

    Returns:
        Tuple of (potentially corrected code, whether correction was made)
    """
    from jcloudai.core.code_generation.sql_validator import SQLValidator

    validator = SQLValidator(self._state)
    return validator.validate_and_correct(code, user_query)
```

### 4.3 修改 Config 类添加配置项

**文件**: `jcloudai/config.py`

```python
class Config:
    # ... 现有配置 ...

    # 新增配置项
    enable_sql_validation: bool = True  # 是否启用 SQL 校验
    sql_validation_max_retries: int = 2  # SQL 校验最大重试次数
```

---

## 5. 新增文件清单

| 文件路径 | 说明 |
|----------|------|
| `jcloudai/core/prompts/validate_sql_prompt.py` | SQL 校验 Prompt 类 |
| `jcloudai/core/prompts/templates/validate_sql_prompt.tmpl` | SQL 校验 Prompt 模板 |
| `jcloudai/core/code_generation/sql_validator.py` | SQL 校验器 |

---

## 6. 修改文件清单

| 文件路径 | 修改内容 |
|----------|----------|
| `jcloudai/agent/base.py` | 添加 `_validate_sql()` 方法，修改 `_process_query()` |
| `jcloudai/config.py` | 添加 `enable_sql_validation` 配置项 |
| `jcloudai/core/prompts/__init__.py` | 导出 `ValidateSQLPrompt` |

---

## 7. 流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           改造后的 Chat 接口流程                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 1: 用户发起查询                                                          │
│ df.chat("查询销售额最高的产品")                                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 2: generate_code_with_retries()                                         │
│ - 构建 Prompt (包含表结构、字段信息)                                           │
│ - 调用 LLM 生成 Python 代码 (包含 SQL)                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 3: _validate_sql() [新增]                                               │
│ - 从代码中提取 SQL                                                            │
│ - 构建校验 Prompt (包含表结构、用户问题、生成的 SQL)                            │
│ - 调用 LLM 校验 SQL                                                           │
│ - 如果 SQL 有问题，使用修正后的 SQL 替换                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
            ┌──────────────┐                ┌──────────────┐
            │ SQL 有效      │                │ SQL 需修正    │
            │ 继续执行      │                │ 替换后继续    │
            └──────────────┘                └──────────────┘
                    │                               │
                    └───────────────┬───────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 4: execute_with_retries()                                               │
│ - 执行 Python 代码                                                            │
│ - 执行 SQL 查询                                                               │
│ - 返回结果                                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. 校验 Prompt 设计细节

### 8.1 完整 Prompt 模板

**文件**: `jcloudai/core/prompts/templates/validate_sql_prompt.tmpl`

```jinja2
你是一个 SQL 专家，负责校验 SQL 查询是否正确回答了用户的问题。

## 数据源信息
<tables>
{% for df in context.dfs %}
{% include 'shared/dataframe.tmpl' with context %}
{% endfor %}
</tables>

## 用户问题
{{ user_query }}

## 生成的 SQL
```sql
{{ generated_sql }}
```

## 校验要求
请仔细检查上述 SQL 是否正确回答了用户的问题。重点检查以下方面：

### 1. 字段选择 (最重要)
- SQL 选择的字段是否与用户问题直接相关？
- 是否遗漏了用户需要的字段？
- 是否选择了不必要的字段？
- 字段名称是否正确（检查拼写和大小写）？

### 2. 条件过滤
- WHERE 条件是否正确理解了用户意图？
- 条件值是否正确？

## 输出格式
请严格按照以下 JSON 格式返回校验结果：

如果 SQL 正确：
```json
{
    "is_valid": true,
    "reason": "SQL 正确的原因说明"
}
```

如果 SQL 有问题：
```json
{
    "is_valid": false,
    "issues": [
        "问题1: 具体描述",
        "问题2: 具体描述"
    ],
    "corrected_sql": "修正后的完整 SQL 语句"
}
```

注意：
- 只返回 JSON，不要有其他内容
- corrected_sql 必须是完整的、可执行的 SQL 语句
- 保持原 SQL 的方言和风格
```

### 8.2 Prompt 类实现

**文件**: `jcloudai/core/prompts/validate_sql_prompt.py`

```python
from jcloudai.core.prompts.base import BasePrompt


class ValidateSQLPrompt(BasePrompt):
    """Prompt to validate generated SQL against user query and schema."""

    template_path = "validate_sql_prompt.tmpl"

    def to_json(self):
        """Convert prompt to JSON for API calls."""
        context = self.props["context"]
        user_query = self.props["user_query"]
        generated_sql = self.props["generated_sql"]
        memory = context.memory

        # Prepare datasets info
        datasets = [dataset.to_json() for dataset in context.dfs]

        return {
            "datasets": datasets,
            "user_query": user_query,
            "generated_sql": generated_sql,
            "system_prompt": memory.agent_description if memory else None,
        }
```

---

## 9. 测试方案

### 9.1 单元测试

**文件**: `tests/unit_tests/core/code_generation/test_sql_validator.py`

```python
import pytest
from unittest.mock import MagicMock, patch
from jcloudai.core.code_generation.sql_validator import SQLValidator


class TestSQLValidator:

    def setup_method(self):
        self.context = MagicMock()
        self.context.config.llm = MagicMock()
        self.validator = SQLValidator(self.context)

    def test_extract_sql_from_code(self):
        """Test SQL extraction from generated code."""
        code = '''
import pandas as pd
result = execute_sql_query("SELECT * FROM users WHERE age > 18")
'''
        sql = self.validator._extract_sql_from_code(code)
        assert sql == "SELECT * FROM users WHERE age > 18"

    def test_extract_sql_multiline(self):
        """Test SQL extraction with multiline SQL."""
        code = '''
result = execute_sql_query("""
    SELECT name, age
    FROM users
    WHERE age > 18
""")
'''
        sql = self.validator._extract_sql_from_code(code)
        assert "SELECT name, age" in sql

    def test_validate_valid_sql(self):
        """Test validation of valid SQL."""
        self.context.config.llm.call.return_value = '{"is_valid": true}'

        code = 'execute_sql_query("SELECT * FROM users")'
        result_code, was_corrected = self.validator.validate_and_correct(
            code, "查询所有用户"
        )

        assert result_code == code
        assert was_corrected is False

    def test_validate_and_correct_invalid_sql(self):
        """Test validation and correction of invalid SQL."""
        self.context.config.llm.call.return_value = '''
{
    "is_valid": false,
    "issues": ["字段选择错误"],
    "corrected_sql": "SELECT id, name FROM users"
}
'''
        code = 'execute_sql_query("SELECT * FROM users")'
        result_code, was_corrected = self.validator.validate_and_correct(
            code, "查询用户ID和姓名"
        )

        assert "SELECT id, name FROM users" in result_code
        assert was_corrected is True
```

### 9.2 集成测试场景

| 测试场景 | 用户问题 | 预期行为 |
|----------|----------|----------|
| 字段选择正确 | "查询销售总额" | SQL 有效，不修正 |
| 字段选择错误 | "查询产品名称" 但 SQL 选了 product_id | 检测到问题，修正为 product_name |
| 缺少必要字段 | "查询用户姓名和年龄" 但 SQL 只选了 name | 检测到问题，添加 age 字段 |
| 条件过滤错误 | "查询2024年数据" 但 SQL 条件是 2023 | 检测到问题，修正条件 |

---

## 10. 配置选项

### 10.1 全局配置

```python
import jcloudai as pai

# 启用 SQL 校验 (默认启用)
pai.config.enable_sql_validation = True

# 设置校验最大重试次数
pai.config.sql_validation_max_retries = 2
```

### 10.2 单次调用配置

```python
# 可以在 Agent 初始化时配置
agent = Agent(df, config=Config(enable_sql_validation=False))
```

---

## 11. 性能考虑

### 11.1 额外开销
- 每次查询增加一次 LLM 调用
- 预计增加 1-3 秒延迟

### 11.2 优化策略
1. **可选启用**: 通过配置项控制是否启用校验
2. **缓存机制**: 对相同的 SQL 和问题组合缓存校验结果
3. **并行处理**: 未来可考虑与代码生成并行执行

---

## 12. 注意事项

### 12.1 兼容性
- 保持与现有 API 完全兼容
- 默认启用校验，可通过配置关闭
- 不影响现有的错误重试机制

### 12.2 错误处理
- 校验 LLM 调用失败时，跳过校验继续执行
- 校验结果解析失败时，默认 SQL 有效
- 记录详细日志便于调试

### 12.3 日志记录
```python
# 校验相关日志
self._state.logger.log("[SQL_VALIDATION] Starting SQL validation...")
self._state.logger.log(f"[SQL_VALIDATION] Original SQL: {sql}")
self._state.logger.log(f"[SQL_VALIDATION] Validation result: {result}")
self._state.logger.log(f"[SQL_VALIDATION] Corrected SQL: {corrected_sql}")
```

---

## 13. 实施步骤

### Phase 1: 基础实现 (预计 2 天)
1. 创建 `ValidateSQLPrompt` 类和模板
2. 创建 `SQLValidator` 类
3. 修改 `Agent._process_query()` 集成校验

### Phase 2: 配置和测试 (预计 1 天)
1. 添加配置项
2. 编写单元测试
3. 编写集成测试

### Phase 3: 优化和文档 (预计 1 天)
1. 性能优化
2. 日志完善
3. 更新文档

---

## 14. 总结

本方案通过在 SQL 生成后增加 LLM 校验节点，实现了对生成 SQL 的二次验证和自动修正。主要特点：

1. **非侵入式设计**: 通过新增组件实现，最小化对现有代码的修改
2. **可配置**: 支持全局和单次调用级别的配置
3. **容错性强**: 校验失败不影响主流程
4. **可扩展**: 校验规则可通过修改 Prompt 模板灵活调整

