# 目录结构说明

## 目录用途说明

### ✅ 合法目录（保留）

#### 1. `papers/` - 论文输入目录
**用途**: 存储原始论文 PDF 文件（输入）

**结构**:
```
papers/
├── <paper_id>/          # 论文ID子文件夹
│   └── paper.pdf        # 论文PDF文件
└── siggraph/            # SIGGRAPH相关文件
```

**说明**: 这是输入目录，存储下载的原始论文文件。**不能删除**。

#### 2. `data/` - 分析结果输出目录
**用途**: 存储所有分析结果（输出）

**新结构（当前使用）**:
```
data/
└── papers/              # 按论文ID组织的分析结果
    └── <paper_id>/      # 论文ID子文件夹
        ├── notes/       # 笔记文件
        ├── summaries/   # 摘要文件
        ├── code/        # 代码项目
        ├── guides/      # 阅读指南
        └── knowledge/   # 知识图谱（论文级别）
```

**说明**: 这是输出目录，存储所有分析结果。**不能删除**。

### ❌ 废弃目录（可删除）

以下目录是旧结构的兼容目录，**已经废弃且为空**，可以安全删除：

- `data/notes/` - 空目录，已迁移到 `data/papers/<paper_id>/notes/`
- `data/code/` - 空目录，已迁移到 `data/papers/<paper_id>/code/`
- `data/summaries/` - 空目录，已迁移到 `data/papers/<paper_id>/summaries/`
- `data/guides/` - 空目录，已迁移到 `data/papers/<paper_id>/guides/`

**注意**: `data/knowledge/` 目录在代码中作为全局知识图谱存储位置，但当前为空。如果确认不需要全局知识图谱，也可以删除。

## 目录关系

```
papers/                    data/
  ├── 2301.12345/    →      └── papers/
  │   └── paper.pdf            └── 2301.12345/
  │                                  ├── notes/
  │                                  ├── summaries/
  │                                  ├── code/
  │                                  ├── guides/
  │                                  └── knowledge/
```

- **`papers/`**: 输入（原始PDF）
- **`data/papers/`**: 输出（分析结果）

两者**不重复**，有不同的用途。

## 清理废弃目录

可以使用以下命令清理废弃的空目录：

```bash
# Windows PowerShell
Remove-Item -Path "data\notes" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "data\code" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "data\summaries" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "data\guides" -Force -ErrorAction SilentlyContinue
# 可选：如果不需要全局知识图谱
# Remove-Item -Path "data\knowledge" -Force -ErrorAction SilentlyContinue
```

或者使用 Python 脚本：

```python
from pathlib import Path

# 要删除的废弃目录
obsolete_dirs = [
    "data/notes",
    "data/code",
    "data/summaries",
    "data/guides",
    # "data/knowledge",  # 可选
]

for dir_path in obsolete_dirs:
    path = Path(dir_path)
    if path.exists() and not any(path.iterdir()):
        path.rmdir()
        print(f"已删除空目录: {dir_path}")
```

## 配置文件说明

在 `config.yaml` 中：

```yaml
paper_reading:
  papers_dir: "papers"              # 输入目录（合法）
  paper_workspace_dir: "data/papers" # 输出目录（合法，新结构）
  
  # 以下为兼容旧结构的配置（已废弃）
  notes_dir: "data/notes"           # 已废弃
  code_dir: "data/code"             # 已废弃
  summaries_dir: "data/summaries"   # 已废弃
  guides_dir: "data/guides"         # 已废弃
  knowledge_dir: "data/knowledge"   # 可能废弃（取决于是否需要全局知识图谱）
```

## 总结

- ✅ **`papers/`** - 合法，存储原始PDF（输入）
- ✅ **`data/papers/`** - 合法，存储分析结果（输出）
- ❌ **`data/notes/`, `data/code/`, `data/summaries/`, `data/guides/`** - 废弃，可删除
- ⚠️ **`data/knowledge/`** - 可能废弃，根据需求决定是否删除
