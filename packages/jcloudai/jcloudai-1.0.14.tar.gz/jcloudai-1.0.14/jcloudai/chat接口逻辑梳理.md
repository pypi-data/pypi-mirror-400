# Chat 接口逻辑梳理

## 概述

`chat` 接口是 JCloud-AI 的核心入口，用于通过自然语言与数据进行对话式交互。本文档详细梳理了从调用入口到返回结果的完整执行流程。

---

## 调用入口

### 入口函数位置
**文件**: `jcloudai/__init__.py` (第 214 行)

```python
def chat(query: str, *dataframes: DataFrame, sandbox: Optional[Sandbox] = None):
    """
    Start a new chat interaction with the assistant on Dataframe(s).

    Args:
        query (str): The query to run against the dataframes.
        *dataframes: Variable number of dataframes to query.
        sandbox (Sandbox, optional): The sandbox to execute code securely.

    Returns:
        The result of the query.
    """
    global _current_agent
    if not dataframes:
        raise ValueError("At least one dataframe must be provided.")

    _current_agent = Agent(list(dataframes), sandbox=sandbox)
    return _current_agent.chat(query)
```

### 调用方式
```python
import jcloudai as jai

# 方式1: 模块级函数调用
result = jai.chat("查询问题", dataset)

# 方式2: DataFrame 方法调用
result = df.chat("查询问题")

# 方式3: Agent 实例调用
agent = Agent(df)
result = agent.chat("查询问题")
```

---

## 完整调用链

```
jai.chat(query, dataset)
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: 创建 Agent 实例                                          │
│ 文件: jcloudai/agent/base.py                                     │
│ - 初始化 AgentState (状态管理)                                    │
│ - 初始化 CodeGenerator (代码生成器)                               │
│ - 初始化 ResponseParser (响应解析器)                              │
│ - 验证数据源兼容性                                                │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: Agent.chat() 方法                                        │
│ 文件: jcloudai/agent/base.py (第 89 行)                          │
│ - 检查 LLM 配置                                                   │
│ - 调用 start_new_conversation() 清空对话历史                      │
│ - 调用 _process_query() 处理查询                                  │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: _process_query() 处理查询                                │
│ 文件: jcloudai/agent/base.py (第 291 行)                         │
│ - 将查询封装为 UserQuery 对象                                     │
│ - 分配 prompt_id                                                  │
│ - 调用 generate_code_with_retries() 生成代码                      │
│ - 调用 execute_with_retries() 执行代码                            │
└─────────────────────────────────────────────────────────────────┘
    │
    ├──────────────────────────────────────┐
    ▼                                      ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│ Step 4A: 代码生成         │    │ Step 4B: 代码执行         │
│ generate_code_with_retries│    │ execute_with_retries     │
└──────────────────────────┘    └──────────────────────────┘
```

---

## 详细步骤说明

### Step 1: Agent 初始化

**文件**: `jcloudai/agent/base.py`

```python
class Agent:
    def __init__(self, dfs, config=None, memory_size=10, vectorstore=None, description=None, sandbox=None):
        # 1. 验证数据源兼容性
        if isinstance(dfs, list):
            sources = [df.schema.source or df._loader.source for df in dfs]
            if not BaseQueryBuilder.check_compatible_sources(sources):
                raise ValueError("数据源不兼容")

        # 2. 初始化状态
        self._state = AgentState()
        self._state.initialize(dfs, config, memory_size, vectorstore, description)

        # 3. 初始化组件
        self._code_generator = CodeGenerator(self._state)
        self._response_parser = ResponseParser()
        self._sandbox = sandbox
```

**AgentState 初始化** (`jcloudai/agent/state.py`):
- `dfs`: DataFrame 列表
- `config`: 配置对象 (LLM、日志、重试次数等)
- `memory`: 对话记忆 (Memory 对象)
- `logger`: 日志记录器
- `vectorstore`: 向量存储 (用于训练)

---

### Step 2: Agent.chat() 方法

**文件**: `jcloudai/agent/base.py` (第 89 行)

```python
def chat(self, query: str, output_type: Optional[str] = None):
    # 1. 检查 LLM 配置
    if self._state.config.llm is None:
        raise ValueError("LLM 未配置")

    # 2. 开始新对话 (清空历史)
    self.start_new_conversation()

    # 3. 处理查询
    return self._process_query(query, output_type)
```

---

### Step 3: _process_query() 处理查询

**文件**: `jcloudai/agent/base.py` (第 291 行)

```python
def _process_query(self, query: str, output_type: Optional[str] = None):
    # 1. 封装用户查询
    query = UserQuery(query)

    # 2. 记录日志
    self._state.logger.log(f"Question: {query}")
    self._state.logger.log(f"Running PandasAI with {self._state.config.llm.type} LLM...")

    # 3. 设置输出类型
    self._state.output_type = output_type

    try:
        # 4. 分配 prompt ID
        self._state.assign_prompt_id()

        # 5. 生成代码 (带重试)
        code = self.generate_code_with_retries(query)

        # 6. 执行代码 (带重试)
        result = self.execute_with_retries(code)

        return result

    except CodeExecutionError:
        return self._handle_exception(code)
```

---

### Step 4A: 代码生成流程

#### 4A.1 generate_code_with_retries()

**文件**: `jcloudai/agent/base.py` (第 191 行)

```python
def generate_code_with_retries(self, query: str) -> Any:
    max_retries = self._state.config.max_retries  # 默认 3 次
    attempts = 0

    try:
        return self.generate_code(query)
    except Exception as e:
        # 重试逻辑
        while attempts <= max_retries:
            try:
                return self._regenerate_code_after_error(code, exception)
            except Exception as e:
                attempts += 1
                if attempts > max_retries:
                    raise
```

#### 4A.2 generate_code()

**文件**: `jcloudai/agent/base.py` (第 108 行)

```python
def generate_code(self, query: Union[UserQuery, str]) -> str:
    # 1. 添加用户消息到记忆
    self._state.memory.add(str(query), is_user=True)

    # 2. 构建 Prompt
    prompt = get_chat_prompt_for_sql(self._state)

    # 3. 调用 LLM 生成代码
    code = self._code_generator.generate_code(prompt)

    # 4. 保存最后使用的 prompt
    self._state.last_prompt_used = prompt

    return code
```

#### 4A.3 CodeGenerator.generate_code()

**文件**: `jcloudai/core/code_generation/base.py`

```python
class CodeGenerator:
    def generate_code(self, prompt: BasePrompt) -> str:
        # 1. 调用 LLM 生成代码
        code = self._context.config.llm.generate_code(prompt, self._context)

        # 2. 保存生成的代码
        self._context.last_code_generated = code

        # 3. 验证和清理代码
        return self.validate_and_clean_code(code)

    def validate_and_clean_code(self, code: str) -> str:
        # 验证代码要求
        if not self._code_validator.validate(code):
            raise ValueError("Code validation failed")

        # 清理代码
        cleaned_code = self._code_cleaner.clean_code(code)
        return cleaned_code
```

#### 4A.4 Prompt 模板

**文件**: `jcloudai/core/prompts/templates/generate_python_code_with_sql.tmpl`

```
<tables>
{% for df in context.dfs %}
{% include 'shared/dataframe.tmpl' with context %}
{% endfor %}
</tables>

You are already provided with the following functions that you can call:
<function>
def execute_sql_query(sql_query: str) -> pd.Dataframe
    """This method connects to the database, executes the sql query and returns the dataframe"""
</function>

Update this initial code:
```python
import pandas as pd
# Write code here
# Declare result var: ...
```

{{ context.memory.get_last_message() }}

At the end, declare "result" variable as a dictionary of type and value.
Generate python code and return full updated code:
```

---

## 返回类型确定机制

### 类型确定流程

Chat 接口的返回类型是通过以下流程确定的：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           返回类型确定流程                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 1: Prompt 模板指导 LLM                                                  │
│ 文件: jcloudai/core/prompts/templates/shared/output_type_template.tmpl      │
│ - 告诉 LLM 可选的类型: "string", "number", "dataframe", "plot"              │
│ - LLM 根据用户问题自动选择合适的类型                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 2: LLM 生成代码，声明 result 变量                                       │
│ 生成的代码格式:                                                              │
│   result = {"type": "number", "value": 12345}                               │
│   result = {"type": "string", "value": "答案是..."}                         │
│   result = {"type": "dataframe", "value": df}                               │
│   result = {"type": "plot", "value": "temp_chart.png"}                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 3: 代码执行后获取 result 字典                                           │
│ 文件: jcloudai/core/code_execution/code_executor.py                         │
│ - exec(code) 执行代码                                                        │
│ - 从环境中获取 result 变量                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 4: ResponseParser 验证并解析                                            │
│ 文件: jcloudai/core/response/parser.py                                       │
│ - 验证 result["type"] 和 result["value"] 的类型匹配                         │
│ - 根据 type 创建对应的 Response 对象                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 关键文件说明

#### 1. output_type_template.tmpl (类型指导模板)

**文件**: `jcloudai/core/prompts/templates/shared/output_type_template.tmpl`

```jinja2
{% if not output_type %}
type (possible values "string", "number", "dataframe", "plot").
Examples:
  { "type": "string", "value": f"The highest salary is {highest_salary}." }
  { "type": "number", "value": 125 }
  { "type": "dataframe", "value": pd.DataFrame({...}) }
  { "type": "plot", "value": "temp_chart.png" }
{% elif output_type == "number" %}
type (must be "number"), value must int. Example: { "type": "number", "value": 125 }
{% elif output_type == "string" %}
type (must be "string"), value must be string. Example: { "type": "string", "value": f"..." }
{% elif output_type == "dataframe" %}
type (must be "dataframe"), value must be pd.DataFrame or pd.Series.
{% elif output_type == "plot" %}
type (must be "plot"), value must be string. Example: { "type": "plot", "value": "temp_chart.png" }
{% endif %}
```

#### 2. ResponseParser (响应解析器)

**文件**: `jcloudai/core/response/parser.py`

```python
class ResponseParser:
    def parse(self, result: dict, last_code_executed: str = None, last_sql_executed: str = None) -> BaseResponse:
        # 1. 验证响应格式
        self._validate_response(result)
        # 2. 生成对应类型的响应对象
        return self._generate_response(result, last_code_executed, last_sql_executed)

    def _generate_response(self, result: dict, last_code_executed, last_sql_executed):
        if result["type"] == "number":
            return NumberResponse(result["value"], last_code_executed, last_sql_executed)
        elif result["type"] == "string":
            return StringResponse(result["value"], last_code_executed, last_sql_executed)
        elif result["type"] == "dataframe":
            return DataFrameResponse(result["value"], last_code_executed, last_sql_executed)
        elif result["type"] == "plot":
            return ChartResponse(result["value"], last_code_executed, last_sql_executed)
        else:
            raise InvalidOutputValueMismatch(f"Invalid output type: {result['type']}")

    def _validate_response(self, result: dict):
        # 验证 type 和 value 的类型匹配
        if result["type"] == "number":
            if not isinstance(result["value"], (int, float, np.int64)):
                raise InvalidOutputValueMismatch("Expected numeric value")
        elif result["type"] == "string":
            if not isinstance(result["value"], str):
                raise InvalidOutputValueMismatch("Expected string value")
        elif result["type"] == "dataframe":
            if not isinstance(result["value"], (pd.DataFrame, pd.Series, dict)):
                raise InvalidOutputValueMismatch("Expected DataFrame or Series")
        elif result["type"] == "plot":
            if not isinstance(result["value"], (str, dict)):
                raise InvalidOutputValueMismatch("Expected plot path string")
```

### 类型确定方式

| 确定方式 | 说明 | 示例 |
|----------|------|------|
| **自动确定** | LLM 根据用户问题自动选择类型 | `df.chat("有多少用户?")` → `number` |
| **手动指定** | 通过 `output_type` 参数强制指定 | `df.chat("统计数据", output_type="dataframe")` |

### 自动类型选择规则

LLM 会根据用户问题的语义自动选择合适的返回类型：

| 问题类型 | 返回类型 | 示例问题 |
|----------|----------|----------|
| 计数/求和/平均值 | `number` | "有多少用户?" "总销售额是多少?" |
| 描述性回答 | `string` | "谁是销售额最高的客户?" "描述一下数据特征" |
| 数据展示 | `dataframe` | "显示前10条数据" "列出所有产品" |
| 可视化 | `plot` | "画一个销售趋势图" "绘制分布图" |

### 手动指定类型

可以通过 `output_type` 参数强制指定返回类型：

```python
# 强制返回数字
result = df.chat("统计用户数量", output_type="number")

# 强制返回字符串
result = df.chat("分析销售趋势", output_type="string")

# 强制返回 DataFrame
result = df.chat("查询销售数据", output_type="dataframe")

# 强制返回图表
result = df.chat("展示销售分布", output_type="plot")
```

### 类型验证与错误处理

如果 LLM 生成的代码返回的类型与值不匹配，会触发错误修复流程：

**文件**: `jcloudai/core/prompts/correct_output_type_error_prompt.py`

```python
class CorrectOutputTypeErrorPrompt(BasePrompt):
    """当输出类型错误时，用于修复代码的 Prompt"""
    template_path = "correct_output_type_error_prompt.tmpl"
```

**模板内容** (`correct_output_type_error_prompt.tmpl`):
```
You generated the following Python code:
{{code}}

However, it resulted in the following error:
{{error}}

Fix the python code above and return the new python code but the result type should be: {{output_type}}
```

### 响应类型汇总

| 类型 | 响应类 | value 类型 | 说明 |
|------|--------|------------|------|
| `number` | `NumberResponse` | `int`, `float`, `np.int64` | 数值结果 |
| `string` | `StringResponse` | `str` | 文本回答 |
| `dataframe` | `DataFrameResponse` | `pd.DataFrame`, `pd.Series`, `dict` | 表格数据 |
| `plot` | `ChartResponse` | `str` (路径) 或 `dict` (Base64) | 图表 |

---

