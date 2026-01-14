# 使用示例

本文档提供详细的使用示例，帮助您快速上手论文阅读试验田。

## 示例 1: 获取 SIGGRAPH 信息

首先，让我们测试一下从 SIGGRAPH 网站获取信息的功能（无需 API Key）：

```bash
python quick_start.py
```

或者使用主程序：

```bash
python src/main.py fetch
```

输出示例：
```
============================================================
SIGGRAPH 网站信息
============================================================
标题: ACM SIGGRAPH

最新新闻 (5 条):
  - ACM Open, ACM Digital Library, and publishing with ACM
  - ACM SIGGRAPH Early Career Development Committee Announces Webinar...
  ...

会议信息 (2 条):
  - SIGGRAPH 2026
  - SIGGRAPH Asia 2025
  ...

论文相关链接 (10 条):
  - Publications: https://www.siggraph.org/publications
  ...
```

## 示例 2: 分析单篇论文

假设您有一篇 PDF 论文文件 `papers/example.pdf`，您可以这样分析：

### 全面分析（默认）

```bash
python src/main.py analyze papers/example.pdf
```

### 只生成摘要

```bash
python src/main.py analyze papers/example.pdf --type summary
```

### 分析方法论

```bash
python src/main.py analyze papers/example.pdf --type methodology
```

### 提取创新点

```bash
python src/main.py analyze papers/example.pdf --type innovation
```

### 生成实现指南

```bash
python src/main.py analyze papers/example.pdf --type implementation
```

## 示例 3: 完整流程（推荐）

这是最强大的功能，将执行完整的论文处理流程：

```bash
python src/main.py full papers/example.pdf
```

这将：
1. ✅ 解析论文（提取标题、作者、摘要、章节等）
2. ✅ 使用 AI 进行全面分析
3. ✅ 提取关键点（贡献、方法、技术等）
4. ✅ 生成实现指南
5. ✅ 创建详细笔记（Markdown 格式）
6. ✅ 更新知识图谱
7. ✅ 生成摘要
8. ✅ 创建代码项目框架（Python）

### 生成 C++ 项目

```bash
python src/main.py full papers/example.pdf --language cpp
```

## 输出文件说明

运行完整流程后，您将得到以下文件：

### 1. 笔记文件

位置: `notes/YYYYMMDD_HHMMSS_论文标题.md`

包含：
- 论文基本信息
- 核心贡献
- 方法摘要
- 关键技术列表
- 详细分析
- 实验与结果
- 局限性和未来工作
- 个人思考区域（可编辑）

### 2. 代码项目

位置: `code/论文标题/`

Python 项目结构：
```
论文标题/
├── README.md          # 项目说明和实现指南
├── requirements.txt   # Python 依赖
├── main.py           # 主程序入口
├── algorithm.py      # 核心算法实现
├── config.py         # 配置文件
├── utils.py          # 工具函数
└── tests/            # 测试代码
    └── test_algorithm.py
```

C++ 项目结构：
```
论文标题/
├── README.md         # 项目说明
├── CMakeLists.txt    # CMake 配置
├── main.cpp          # 主程序
├── algorithm.h       # 算法头文件
└── algorithm.cpp     # 算法实现
```

### 3. 摘要文件

位置: `summaries/论文标题_summary.md`

包含论文的快速摘要，便于快速回顾。

### 4. 实现指南

位置: `code/论文标题_implementation_guide.md`

包含详细的实现指导，包括：
- 技术栈选择
- 核心算法实现步骤
- 关键代码结构
- 参数配置建议
- 测试和验证方法
- 常见问题和解决方案

### 5. 知识图谱

位置: `notes/knowledge_graph.json`

累积的知识图谱，包含所有已分析论文的关键信息，便于：
- 查找相关论文
- 发现技术关联
- 构建知识体系

## 示例 4: 处理文本格式论文

如果您的论文是文本格式（.txt 或 .md），也可以直接处理：

```bash
python src/main.py full papers/example.txt
```

## 工作流程建议

### 第一步：获取论文

1. 使用 `python src/main.py fetch` 查看 SIGGRAPH 最新论文
2. 手动下载感兴趣的论文到 `papers/` 目录

### 第二步：初步分析

```bash
python src/main.py analyze papers/your_paper.pdf --type summary
```

快速了解论文内容。

### 第三步：深度处理

```bash
python src/main.py full papers/your_paper.pdf
```

获得完整的分析、笔记和代码框架。

### 第四步：内化和落地

1. 阅读生成的笔记，在"个人思考"部分添加自己的想法
2. 查看实现指南，开始编写代码
3. 在代码项目中实现论文中的算法
4. 运行测试，验证实现

## 高级用法

### 批量处理多篇论文

创建一个简单的脚本 `batch_process.py`：

```python
import subprocess
from pathlib import Path

papers_dir = Path("papers")
for pdf_file in papers_dir.glob("*.pdf"):
    print(f"处理: {pdf_file}")
    subprocess.run([
        "python", "src/main.py", "full", str(pdf_file)
    ])
```

### 自定义分析提示

修改 `src/api/moonshot_client.py` 中的 `analyze_paper` 方法，可以自定义分析提示词。

### 扩展知识图谱

在 `src/knowledge/internalizer.py` 中可以添加更多知识图谱字段，如：
- 相关领域
- 应用场景
- 技术难度评级
- 个人评分

## 常见问题

### Q: API Key 在哪里获取？

A: 访问 [Moonshot AI 平台](https://platform.moonshot.ai/) 注册并获取 API Key。

### Q: 支持哪些论文格式？

A: 目前主要支持 PDF 格式，文本格式（.txt, .md）也可以使用。

### Q: 如何提高分析质量？

A: 
1. 确保 PDF 质量良好，文字可提取
2. 在 `config.yaml` 中调整 `temperature` 参数（较低值更精确）
3. 使用更大的模型（如 `moonshot-v1-128k`）处理长论文

### Q: 生成的代码是完整的吗？

A: 生成的代码是框架和模板，需要根据论文的具体内容进行实现。实现指南会提供详细的指导。

## 下一步

- 阅读 [README.md](README.md) 了解完整功能
- 查看 `config.yaml` 自定义配置
- 开始处理您的第一篇论文！
