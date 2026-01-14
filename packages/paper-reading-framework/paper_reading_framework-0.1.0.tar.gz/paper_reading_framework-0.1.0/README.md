# 论文阅读试验田

使用 Moonshot AI (Kimi) 进行论文的精度阅读、内化和落地的完整框架。

## 📁 项目结构

```
Architechture/
├── src/                   # 源代码
│   ├── api/               # Moonshot AI 客户端
│   ├── paper/             # 论文处理模块
│   ├── knowledge/         # 知识内化模块
│   ├── reading/           # 辅助阅读（术语/导读）
│   └── implementation/    # 代码生成模块
├── docs/                  # 详细文档
│   ├── api_setup.md       # API 配置指南
│   ├── usage_examples.md  # 使用示例
│   └── ...                # 其他文档
├── config.yaml            # 配置文件
├── quick_start.py         # 快速测试 SIGGRAPH 信息获取（无需 API Key）
├── test_api.py            # 测试 Moonshot API 连接
├── test_arm_paper.py      # 测试 arXiv 下载
├── data/                  # 产出数据（所有生成的内容）
│   ├── papers/           # 论文工作空间（按论文ID组织）
│   ├── notes/            # 笔记（兼容旧结构）
│   ├── code/             # 代码项目（兼容旧结构）
│   └── summaries/        # 摘要（兼容旧结构）
├── papers/                # 论文文件存储目录（每篇论文一个子文件夹）
│   ├── <paper_id>/        # 论文ID子文件夹
│   │   └── paper.pdf      # 论文PDF文件
│   └── siggraph/          # SIGGRAPH 相关文件
├── README.md              # 主文档
└── START_HERE.md          # 快速开始文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

在 `config.yaml` 文件中设置：
```yaml
moonshot:
  api_key: "your-api-key-here"
```

### 3. 开始使用

#### 方式 1: 使用 Paper Skill（推荐，适合 AI IDE）

```python
from skills.paper_reading.scripts.paper_skill import PaperSkill

skill = PaperSkill()
result = skill.download_and_analyze("2301.12345")  # 示例 arXiv ID
```

或使用命令行：
```bash
python skills/paper_reading/scripts/paper_skill.py 2301.12345
```

> **Skill 文档**: 详细使用说明请查看 [skills/paper_reading/skill.md](skills/paper_reading/skill.md)

#### 方式 2: 使用主程序

```bash
# 完整流程（推荐）
python src/main.py full papers/<paper_id>/paper.pdf

# 快速分析
python src/main.py analyze papers/<paper_id>/paper.pdf --type summary

# 自动下载并分析
python src/main.py download https://arxiv.org/abs/2301.12345
python src/main.py full papers/2301.12345/paper.pdf
```

#### 方式 3: 直接使用 arXiv URL 分析（推荐，当 PDF 无法提取文本时）

```bash
# 使用 arXiv URL 或 ID 直接分析（无需下载 PDF）
python analyze_arxiv_paper.py https://arxiv.org/abs/2301.12345
# 或
python analyze_arxiv_paper.py 2301.12345
```

这种方式会：
1. 从 arXiv API 获取论文信息（标题、作者、摘要）
2. 使用 Moonshot AI 进行深度分析
3. 生成笔记、摘要和代码项目

> **优势**: 当 PDF 文件无法提取文本时（如扫描版 PDF），可以使用此方法直接基于 arXiv 摘要进行分析。

> **注意**: 每篇论文使用独立子文件夹 `papers/<paper_id>/paper.pdf`，便于管理多篇论文。

> **注意**: 确保论文文件放在 `papers/` 目录下，输出文件会保存在 `data/` 目录中。

## 📖 详细文档

- [快速开始指南](START_HERE.md)
- [Paper Skill 使用指南](skills/paper_reading/skill.md) - **推荐：AI IDE 快速调用**
- [Paper Skill 快速上手](skills/paper_reading/README.md)
- [使用示例](docs/usage_examples.md)
- [API 配置](docs/api_setup.md)
- [项目总结](docs/project_summary.md)


## ✨ 功能特性

- 📚 **论文获取**: 支持从 arXiv、SIGGRAPH 等获取论文
- 🔍 **智能分析**: 使用 Moonshot AI 进行深度论文分析
- 📖 **辅助阅读**: 根据读者背景提供个性化教学引导和术语解释（新增）
- 📝 **知识内化**: 自动生成笔记、摘要和知识图谱
- 💻 **代码落地**: 基于论文分析生成实现代码框架

## 📝 注意事项

1. **API Key**: 需要有效的 Moonshot AI API Key（国内版本）
2. **论文格式**: 主要支持 PDF 格式
3. **产出数据**: 所有生成的内容保存在 `data/` 目录
   - 新结构：按论文ID组织在 `data/papers/<paper_id>/` 下
   - 旧结构（兼容）：分散在 `data/notes/`, `data/code/`, `data/summaries/` 等目录
4. **读者预设**: 默认使用业余读者模式，可在 `config.yaml` 中调整


## 📖 辅助阅读功能

新增的辅助阅读功能为不同背景的读者提供个性化支持：

- **业余读者**（默认）: 提供详细的教学引导、术语解释和阅读指南
- **专业读者**: 提供简要的分析，直接切入重点

详细说明请查看 [辅助阅读功能文档](docs/assistant_reading_feature.md)

## 📄 许可证

本项目仅供学习和研究使用。
