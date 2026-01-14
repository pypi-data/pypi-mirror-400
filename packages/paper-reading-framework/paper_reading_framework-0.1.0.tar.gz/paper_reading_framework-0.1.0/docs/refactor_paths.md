# 项目重构计划

## 新的目录结构

```
Architechture/
├── src/                    # 源代码（API）
│   ├── api/
│   ├── paper/
│   ├── knowledge/
│   └── implementation/
├── scripts/                 # 工具脚本
│   ├── main.py
│   ├── download_and_analyze.py
│   ├── quick_start.py
│   └── test_api.py
├── config/                  # 配置文件
│   └── config.yaml
├── data/                    # 产出数据（所有生成的内容）
│   ├── papers/             # 论文文件
│   ├── notes/              # 笔记
│   ├── summaries/          # 摘要
│   ├── code/               # 生成的代码
│   └── knowledge/          # 知识图谱
├── docs/                   # 文档
│   ├── README.md
│   ├── API_SETUP.md
│   └── ...
├── requirements.txt
└── .env
```

## 需要更新的路径

1. `src/api/moonshot_client.py`: config_path 默认值改为 "config/config.yaml"
2. `src/paper/fetcher.py`: config_path 默认值改为 "config/config.yaml"
3. `src/knowledge/internalizer.py`: notes_dir 默认值从配置读取
4. `src/implementation/code_generator.py`: code_dir 默认值从配置读取
5. 所有脚本: 更新导入路径和配置文件路径
