# Paper Reading Skill

快速上手指南：使用论文阅读技能下载和分析学术论文。

## 快速开始

### 1. 配置 API Key

在项目根目录的 `config.yaml` 中设置：

```yaml
moonshot:
  api_key: "your-api-key-here"
```

### 2. 使用技能

#### Python 代码

```python
from skills.paper_reading.scripts.paper_skill import PaperSkill

skill = PaperSkill()
result = skill.download_and_analyze("2301.12345")
```

#### 命令行

```bash
python skills/paper_reading/scripts/paper_skill.py 2301.12345
```

## 输出结果

分析完成后，结果保存在 `data/papers/<paper_id>/` 目录：

- **笔记**: `notes/YYYYMMDD_HHMMSS_note.md`
- **摘要**: `summaries/summary.md`
- **代码**: `code/` (完整项目框架)
- **阅读指南**: `guides/reading_guide.md`

## 更多信息

详细文档请查看 [skill.md](skill.md)
