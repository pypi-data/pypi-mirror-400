# Paper Reading Skill - 论文阅读技能

## 功能描述

此技能用于下载并分析学术论文（主要支持 arXiv），使用 Moonshot AI (Kimi) 进行深度分析，生成笔记、摘要、代码项目和阅读指南。

## 主要功能

1. **论文下载**: 从 arXiv 自动下载论文 PDF
2. **论文解析**: 提取标题、作者、摘要、章节等结构化信息
3. **AI 分析**: 使用 Moonshot AI 进行深度分析
   - 全面分析
   - 关键点提取
   - 实现指南生成
4. **知识内化**: 生成 Markdown 笔记和摘要
5. **代码生成**: 基于论文分析生成实现代码框架
6. **辅助阅读**: 生成阅读指南和术语解释

## 使用方法

### 方式 1: Python API（推荐）

```python
import sys
from pathlib import Path

# 添加 skill 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from skills.paper_reading.scripts.paper_skill import PaperSkill

# 创建技能实例
skill = PaperSkill()

# 一键下载和分析
result = skill.download_and_analyze("2301.12345")
# 或使用 URL
result = skill.download_and_analyze("https://arxiv.org/abs/2301.12345")

# 结果包含：
# - paper_path: 论文文件路径
# - note_path: 笔记文件路径
# - summary_path: 摘要文件路径
# - code_dir: 代码项目目录
# - reading_guide_path: 阅读指南路径
```

### 方式 2: 命令行

```bash
# 从项目根目录运行
python skills/paper_reading/scripts/paper_skill.py 2301.12345

# 仅下载
python skills/paper_reading/scripts/paper_skill.py 2301.12345 --action download

# 仅分析（需要先下载）
python skills/paper_reading/scripts/paper_skill.py 2301.12345 --action analyze --type summary
```

### 方式 3: 使用主程序

```bash
# 下载
python src/main.py download https://arxiv.org/abs/2301.12345

# 完整分析
python src/main.py full papers/2301.12345/paper.pdf

# 快速分析
python src/main.py analyze papers/2301.12345/paper.pdf --type summary
```

## 输入数据

### 输入方式

1. **arXiv ID**: 直接提供论文 ID（如 "2301.12345"）
2. **arXiv URL**: 提供完整 URL（如 "https://arxiv.org/abs/2301.12345"）
3. **本地文件**: 提供已下载的 PDF 文件路径

### 输入数据位置

- 论文会自动下载到 `papers/<paper_id>/paper.pdf`
- 可以在 `data/input_data/` 目录下放置待处理的论文列表

## 输出数据

所有分析结果保存在 `data/papers/<paper_id>/` 目录下：

- **笔记**: `data/papers/<paper_id>/notes/YYYYMMDD_HHMMSS_note.md`
- **摘要**: `data/papers/<paper_id>/summaries/summary.md`
- **代码项目**: `data/papers/<paper_id>/code/`
- **阅读指南**: `data/papers/<paper_id>/guides/reading_guide.md`
- **知识图谱**: `data/papers/<paper_id>/knowledge/knowledge_graph.json`

## 配置要求

### 必需配置

在项目根目录的 `config.yaml` 中配置：

```yaml
moonshot:
  api_key: "your-api-key-here"  # Moonshot AI API Key
  base_url: "https://api.moonshot.cn/v1"
  model: "moonshot-v1-32k"  # 可选: moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k
```

### 可选配置

```yaml
paper_reading:
  papers_dir: "papers"  # 论文存储目录
  paper_workspace_dir: "data/papers"  # 分析结果存储目录
```

## 常用操作示例

### 1. 下载并完整分析一篇论文

```python
from skills.paper_reading.scripts.paper_skill import PaperSkill

skill = PaperSkill()
result = skill.download_and_analyze("2301.12345")
```

### 2. 仅获取快速摘要

```python
skill = PaperSkill()
summary = skill.quick_summary("2301.12345")
print(summary)
```

### 3. 分析已有论文

```python
skill = PaperSkill()
result = skill.analyze_paper("papers/2301.12345/paper.pdf", "summary")
```

### 4. 批量处理多篇论文

```python
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

## 注意事项

1. **API Key**: 需要有效的 Moonshot AI API Key（国内版本）
2. **API 费用**: 每次分析会消耗 API 额度，请合理使用
3. **大论文**: 超过 32K tokens 的论文建议使用 `moonshot-v1-128k` 模型
4. **网络连接**: 下载论文需要网络连接
5. **存储空间**: 确保有足够的磁盘空间存储论文和分析结果
6. **PDF 质量**: 确保 PDF 文件文字可提取，扫描版可能效果不佳

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

- [README.md](README.md) - 快速上手指南
- [项目主文档](../../README.md) - 完整项目文档
- [API 配置指南](../../docs/api_setup.md) - API 配置详细说明
