# Paper Reading Skill - 论文阅读技能使用指南

## 概述

`paper_skill.py` 是一个统一的 API 接口，为 Cursor 等 AI IDE 提供便捷的论文下载和分析功能。

## 快速开始

### 安装和配置

1. 确保已安装所有依赖：
```bash
pip install -r requirements.txt
```

2. 配置 API Key（在 `config.yaml` 中）：
```yaml
moonshot:
  api_key: "your-api-key-here"
```

### 基本使用

#### 方式 1: Python API（推荐）

```python
from paper_skill import PaperSkill

# 创建技能实例
skill = PaperSkill()

# 一键下载和分析
result = skill.download_and_analyze("2301.12345")
```

#### 方式 2: 命令行

```bash
# 完整流程
python paper_skill.py 2301.12345

# 仅下载
python paper_skill.py 2301.12345 --action download
```

## API 参考

### PaperSkill 类

#### `__init__(config_path: str = "config.yaml")`

初始化技能实例。

**参数：**
- `config_path`: 配置文件路径（默认: "config.yaml"）

#### `download_and_analyze(arxiv_id: str) -> Dict[str, Any]`

下载论文并运行完整分析（一键操作）。

**参数：**
- `arxiv_id`: arXiv ID 或 URL（如 "2301.12345" 或 "https://arxiv.org/abs/2301.12345"）

**返回：**
```python
{
    "success": True,
    "paper_id": "2301.12345",
    "paper_path": "papers/2301.12345/paper.pdf",
    "note_path": "data/papers/2301.12345/notes/...",
    "summary_path": "data/papers/2301.12345/summaries/summary.md",
    "code_dir": "data/papers/2301.12345/code",
    "reading_guide_path": "data/papers/2301.12345/guides/reading_guide.md",
    "knowledge_graph_path": "data/knowledge/knowledge_graph.json",
}
```

**示例：**
```python
skill = PaperSkill()
result = skill.download_and_analyze("2301.12345")
print(f"笔记: {result['note_path']}")
print(f"代码: {result['code_dir']}")
```

#### `download_paper(arxiv_id: str) -> Optional[Path]`

仅下载论文。

**参数：**
- `arxiv_id`: arXiv ID 或 URL

**返回：**
- 下载的文件路径（`Path` 对象），失败返回 `None`

**示例：**
```python
skill = PaperSkill()
paper_path = skill.download_paper("2301.12345")
if paper_path:
    print(f"下载成功: {paper_path}")
```

#### `analyze_paper(paper_path: str, analysis_type: str = "full") -> Dict[str, Any]`

分析已有论文。

**参数：**
- `paper_path`: 论文文件路径
- `analysis_type`: 分析类型
  - `"full"`: 完整分析（包含关键点提取和实现指南）
  - `"summary"`: 仅摘要
  - `"innovation"`: 仅创新点
  - `"implementation"`: 仅实现指南

**返回：**
分析结果字典

**示例：**
```python
skill = PaperSkill()
result = skill.analyze_paper("papers/2301.12345/paper.pdf", "summary")
print(result["analysis"])
```

#### `quick_summary(arxiv_id: str) -> str`

快速获取论文摘要（不保存文件，仅返回文本）。

**参数：**
- `arxiv_id`: arXiv ID

**返回：**
摘要文本字符串

**示例：**
```python
skill = PaperSkill()
summary = skill.quick_summary("2301.12345")
print(summary)
```

## 使用场景

### 场景 1: 快速了解一篇论文

```python
from paper_skill import PaperSkill

skill = PaperSkill()
summary = skill.quick_summary("2301.12345")
print(summary)
```

### 场景 2: 完整分析并生成代码

```python
from paper_skill import PaperSkill

skill = PaperSkill()
result = skill.download_and_analyze("2301.12345")

# 查看生成的代码
code_dir = result["code_dir"]
print(f"代码项目: {code_dir}")
```

### 场景 3: 批量处理多篇论文

```python
from paper_skill import PaperSkill

skill = PaperSkill()
paper_ids = ["2301.12345", "2301.12345", "2301.12345"]

for paper_id in paper_ids:
    print(f"\n处理论文: {paper_id}")
    result = skill.download_and_analyze(paper_id)
    if result.get("success"):
        print(f"✓ 完成: {result['note_path']}")
    else:
        print(f"✗ 失败: {result.get('error')}")
```

### 场景 4: 在 Cursor 中使用

在 Cursor 的 AI 对话中，可以直接说：

```
请帮我下载并分析这篇论文：https://arxiv.org/abs/2301.12345
```

然后 AI 可以调用：

```python
from paper_skill import PaperSkill
skill = PaperSkill()
result = skill.download_and_analyze("2301.12345")
```

## 输出文件结构

```
data/papers/<paper_id>/
├── notes/
│   └── YYYYMMDD_HHMMSS_note.md    # 详细笔记
├── summaries/
│   └── summary.md                  # 快速摘要
├── code/
│   ├── README.md                   # 项目说明
│   ├── implementation_guide.md    # 实现指南
│   ├── main.py                     # 主程序
│   ├── algorithm.py                # 核心算法
│   └── tests/                      # 测试代码
├── guides/
│   └── reading_guide.md           # 阅读指南（包含术语解释）
└── knowledge/
    └── knowledge_graph.json       # 知识图谱更新
```

## 错误处理

所有方法在失败时会返回包含 `error` 键的字典：

```python
result = skill.download_and_analyze("invalid_id")
if "error" in result:
    print(f"错误: {result['error']}")
```

## 配置说明

在 `config.yaml` 中可以配置：

- **API Key**: `moonshot.api_key`
- **模型选择**: `moonshot.model` (moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k)
- **输出目录**: `paper_reading.paper_workspace_dir`

## 注意事项

1. **API 费用**: 每次分析会消耗 API 额度，请合理使用
2. **大论文**: 超过 32K tokens 的论文建议使用 `moonshot-v1-128k` 模型
3. **网络**: 下载论文需要网络连接
4. **存储**: 确保有足够的磁盘空间存储论文和分析结果

## 故障排除

### 问题 1: 下载失败

- 检查网络连接
- 确认 arXiv ID 格式正确
- 查看错误信息

### 问题 2: API 调用失败

- 检查 `config.yaml` 中的 API Key 是否正确
- 确认 API 额度是否充足
- 查看控制台错误信息

### 问题 3: 分析结果不完整

- 对于长论文，尝试使用更大的模型（moonshot-v1-128k）
- 检查 PDF 文件是否完整
- 查看日志了解具体错误

## 相关文档

- [快速开始指南](../START_HERE.md)
- [API 配置指南](api_setup.md)
- [使用示例](usage_examples.md)
