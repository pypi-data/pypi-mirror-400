# NStudyPy 
NStudyPy 工具包

## 要求
- Python 3.10+

## 安装方法

### 使用 pip
```bash
pip install -U NStudyPy -i https://pypi.org/simple
```

### 使用 uv
```bash
uv add NStudyPy
```

## 开发

本项目使用 `uv` 进行依赖管理。

### 环境准备

1. 安装 uv
```bash
# Windows
pip install uv

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. 克隆项目仓库
```bash
git clone https://github.com/lizhq/NStudyPy.git
cd NStudyPy
```

3. 同步项目依赖
```bash
# uv 会自动读取 pyproject.toml 并同步所有依赖
uv sync
```

### 开发工作流

**添加新依赖**
```bash
# 添加运行时依赖
uv add requests

# 添加开发依赖
uv add --dev pytest
```

**更新依赖**
```bash
# 更新所有依赖到最新版本
uv lock --upgrade

# 同步更新后的依赖
uv sync
```

**运行 Python 脚本**
```bash
# 在 uv 管理的环境中运行
uv run python your_script.py
```

## 版本更新历史

查看完整的版本更新历史，请参考 [CHANGELOG.md](CHANGELOG.md)