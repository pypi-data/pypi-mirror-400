# Paper Reading Skill 目录结构

## 标准 Skill 格式

```
skills/
└── paper_reading/
    ├── data/
    │   ├── input_data/      # 输入数据目录
    │   └── output_data/     # 输出数据目录（实际输出在项目根目录的 data/papers/）
    ├── scripts/
    │   ├── paper_skill.py   # 主脚本：PaperSkill 类
    │   └── example_usage.py # 使用示例
    ├── skill.md             # 详细技能文档
    ├── README.md            # 快速上手指南
    └── STRUCTURE.md         # 本文件：结构说明
```

## 文件说明

### scripts/paper_skill.py
- **PaperSkill 类**: 统一的 API 接口
- **主要方法**:
  - `download_and_analyze()`: 一键下载和分析
  - `download_paper()`: 仅下载论文
  - `analyze_paper()`: 分析已有论文
  - `quick_summary()`: 快速获取摘要
- **命令行入口**: 支持 `--action` 和 `--type` 参数

### skill.md
- 详细的功能描述
- 完整的使用方法
- 配置要求
- 故障排除指南

### README.md
- 快速上手指南
- 基本使用示例
- 输出结果说明

### data/
- **input_data/**: 用于存放输入数据（如待处理的论文列表）
- **output_data/**: 输出数据目录（注意：实际输出在项目根目录的 `data/papers/` 下）

## 使用方式

### 在代码中使用

```python
from skills.paper_reading.scripts.paper_skill import PaperSkill

skill = PaperSkill()
result = skill.download_and_analyze("2301.12345")
```

### 命令行使用

```bash
python skills/paper_reading/scripts/paper_skill.py 2301.12345
```

### 在 Cursor 中使用

直接在对话中说：
```
请帮我下载并分析这篇论文：https://arxiv.org/abs/2301.12345
```

Cursor AI 会自动调用 `skills/paper_reading/scripts/paper_skill.py`。

## 路径说明

- **技能目录**: `skills/paper_reading/`
- **主脚本**: `skills/paper_reading/scripts/paper_skill.py`
- **项目根目录**: 技能目录的父目录的父目录（`../../`）
- **配置文件**: 项目根目录的 `config.yaml`
- **论文存储**: 项目根目录的 `papers/<paper_id>/paper.pdf`
- **分析结果**: 项目根目录的 `data/papers/<paper_id>/`

## 与项目其他部分的关系

```
项目根目录/
├── skills/
│   └── paper_reading/      # Skill 目录
├── src/                    # 源代码（被 skill 调用）
├── papers/                 # 论文存储（输入）
├── data/                   # 分析结果（输出）
└── config.yaml             # 配置文件
```

Skill 是对项目核心功能的封装，提供了统一的 API 接口，便于在 AI IDE 中快速调用。
