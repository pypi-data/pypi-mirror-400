# 项目重构指南

## 新的目录结构

```
Architechture/
├── src/                    # 源代码（API）- 保持不变
│   ├── api/
│   ├── paper/
│   ├── knowledge/
│   └── implementation/
├── scripts/                 # 工具脚本（新建）
│   ├── main.py             # 主程序（从 src/main.py 移动）
│   ├── download_and_analyze.py
│   ├── quick_start.py
│   └── test_api.py
├── config/                  # 配置文件（新建）
│   └── config.yaml         # 配置文件（从根目录移动）
├── data/                    # 产出数据（新建，已部分完成）
│   ├── papers/             # 论文文件（已移动）
│   ├── notes/              # 笔记（已移动）
│   ├── summaries/          # 摘要（已移动）
│   ├── code/               # 生成的代码（已移动）
│   └── knowledge/          # 知识图谱（新建）
├── docs/                   # 文档（新建）
│   ├── api_setup.md
│   ├── usage_examples.md
│   ├── project_summary.md
│   ├── assistant_reading_feature.md
│   ├── refactor_guide.md
│   └── refactor_paths.md
├── requirements.txt
└── .env
```

## 已完成的更新

1. ✅ 更新了 `src/api/moonshot_client.py` - 配置文件路径改为 `config/config.yaml`
2. ✅ 更新了 `src/paper/fetcher.py` - 配置文件路径改为 `config/config.yaml`
3. ✅ 更新了 `src/knowledge/internalizer.py` - 从配置文件读取路径
4. ✅ 更新了 `src/implementation/code_generator.py` - 从配置文件读取路径
5. ✅ 创建了 `config/config.yaml` - 新的配置文件（路径已更新）

## 需要手动完成的步骤

### 1. 创建目录结构

```bash
# 如果 config, scripts, docs 是文件，先删除
rm -f config scripts docs

# 创建目录
mkdir -p config scripts docs data/knowledge
```

### 2. 移动文件

```bash
# 移动配置文件
mv config.yaml config/config.yaml  # 如果存在

# 移动脚本文件
mv src/main.py scripts/main.py
mv download_and_analyze.py scripts/  # 如果存在
mv quick_start.py scripts/
mv test_api.py scripts/

# 移动文档文件（已统一重命名为小写）
# 注意：README.md 和 START_HERE.md 保留在根目录
mv API_SETUP.md docs/api_setup.md
mv USAGE_EXAMPLES.md docs/usage_examples.md
mv PROJECT_SUMMARY.md docs/project_summary.md
mv ASSISTANT_READING_FEATURE.md docs/assistant_reading_feature.md
mv REFACTOR_GUIDE.md docs/refactor_guide.md
mv REFACTOR_PATHS.md docs/refactor_paths.md
```

### 3. 更新脚本中的路径引用

所有脚本需要更新：
- 导入路径：`sys.path.insert(0, str(Path(__file__).parent.parent))`
- 配置文件路径：`config/config.yaml`

### 4. 更新 .gitignore

确保以下目录被忽略：
```
data/
config/config.yaml  # 如果包含敏感信息
.env
```

## 使用新结构

### 运行主程序

```bash
# 从项目根目录运行
python scripts/main.py fetch
python scripts/main.py analyze data/papers/paper.pdf
python scripts/main.py full data/papers/paper.pdf
```

### 配置文件位置

所有配置现在在 `config/config.yaml`，路径都是相对于项目根目录的。

## 优势

1. **清晰的分离**：源码（src/）、脚本（scripts/）、配置（config/）、数据（data/）、文档（docs/）
2. **易于维护**：所有产出内容集中在 data/ 目录
3. **版本控制友好**：可以轻松忽略 data/ 目录
4. **配置集中**：所有配置在 config/ 目录
