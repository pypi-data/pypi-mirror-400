# 快速开始指南

## 环境要求

- Python 3.10+
- **uv** (推荐) 或 pip

### 安装 uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip
pip install uv
```

## 安装步骤

### 方式一：使用 uv（推荐）

```bash
cd phone_py

# 创建虚拟环境并安装依赖（一条命令）
uv venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows

# 安装开发依赖
uv pip install -e ".[dev]"

# 或者使用 uv sync（如果有 uv.lock）
uv sync --all-extras
```

### 方式二：使用 pip

```bash
cd phone_py
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows

pip install -e ".[dev]"
```

## 开发工具使用

### 代码格式化和检查

```bash
# 格式化代码（自动修复）
ruff format src tests

# 检查代码（显示问题）
ruff check src tests

# 自动修复可修复的问题
ruff check --fix src tests
```

### 类型检查

```bash
# 运行 MyPy 类型检查
mypy src
```

### 运行测试

```bash
# 运行所有测试
pytest

# 带覆盖率报告
pytest --cov=phone_parser

# 详细输出
pytest -v

# 运行特定测试
pytest tests/test_phone.py::TestPhoneParsing::test_parse_with_country_code
```

## 构建和发布

### 构建包

```bash
# 使用 uv（推荐）
uv pip install build
python -m build

# 或使用 pip
pip install build
python -m build
```

### 发布到 PyPI

```bash
# 使用 uv 安装 twine
uv pip install twine

# 检查包
twine check dist/*

# 上传到 TestPyPI（测试）
twine upload --repository testpypi dist/*

# 上传到 PyPI（正式）
twine upload dist/*
```

## 常见任务

### 使用 Makefile（推荐）

项目包含 Makefile 简化常用操作：

```bash
# 查看所有可用命令
make help

# 完整设置（创建 venv + 安装依赖）
make setup

# 仅安装依赖
make install-dev

# 运行测试
make test

# 代码检查和格式化
make lint
make format

# 类型检查
make type-check

# 运行所有质量检查
make qa

# 构建和发布
make build
make publish-test  # TestPyPI
make publish       # PyPI
```

Makefile 会自动检测是否安装了 uv，优先使用 uv，回退到 pip。

### 添加新的国家支持

编辑 `src/phone_parser/country.py` 中的 `COUNTRIES_YAML` 常量：

```yaml
"新国家代码":
  country_code: "代码"
  name: "国家名称"
  char_3_code: ISO代码
  area_code: "区号正则表达式"
  max_num_length: "最大号码长度"
```

### 添加新的格式化样式

编辑 `src/phone_parser/phone.py` 中的 `NAMED_FORMATS` 字典：

```python
NAMED_FORMATS = {
    "新格式": "%c (%a) %n",
    # ...
}
```

## 提交代码前检查清单

- [ ] 代码通过 `ruff check`
- [ ] 代码通过 `ruff format --check`
- [ ] 类型检查通过 `mypy src`
- [ ] 所有测试通过 `pytest`
- [ ] 测试覆盖率 > 80%
- [ ] 添加了必要的文档字符串
- [ ] 更新了 README（如果有 API 变更）
