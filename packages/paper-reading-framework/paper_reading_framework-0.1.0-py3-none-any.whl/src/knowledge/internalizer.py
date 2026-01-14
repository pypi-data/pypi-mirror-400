"""\
知识内化模块
将论文知识转化为个人知识体系
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class KnowledgeInternalizer:
    """知识内化器"""

    def __init__(self, notes_dir: Optional[str] = None, config_path: str = "config.yaml"):
        """初始化内化器。

        Args:
            notes_dir: 笔记存储目录（如果为 None，则从配置文件读取）
            config_path: 配置文件路径（支持 `config.yaml` / `config/config.yaml` / `config`）
        """
        self.config = self._load_config(config_path)
        paper_reading = self.config.get("paper_reading", {}) if isinstance(self.config, dict) else {}

        # 新结构：所有产物写入 data/papers/<paper_id>/...
        self.paper_workspace_dir = paper_reading.get("paper_workspace_dir") or paper_reading.get("output_root")
        self.paper_workspace_dir = Path(self.paper_workspace_dir) if self.paper_workspace_dir else None
        if self.paper_workspace_dir:
            self.paper_workspace_dir.mkdir(parents=True, exist_ok=True)

        # 旧结构（兼容）
        if notes_dir is None:
            notes_dir = paper_reading.get("notes_dir", "data/notes")

        self.notes_dir = Path(notes_dir)
        self.notes_dir.mkdir(parents=True, exist_ok=True)

        self.knowledge_dir = Path(paper_reading.get("knowledge_dir", "data/knowledge"))
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)

        self.summaries_dir = Path(paper_reading.get("summaries_dir", "data/summaries"))
        self.summaries_dir.mkdir(parents=True, exist_ok=True)


    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件（兼容历史路径）。"""
        candidates = [config_path, "config.yaml", "config/config.yaml", "config"]
        for p in candidates:
            if not p:
                continue
            config_file = Path(p)
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
        return {}

    def _safe_title_id(self, paper_info: Dict[str, Any]) -> str:
        title = (paper_info.get("title") or "unknown").strip()[:80]
        safe = "".join(c if (c.isalnum() or c in ("-", "_", ".")) else "_" for c in title)
        safe = safe.strip("_")
        return safe[:50] or "unknown"

    def _paper_root(self, paper_id: Optional[str], paper_info: Optional[Dict[str, Any]] = None) -> Optional[Path]:
        if not self.paper_workspace_dir:
            return None
        pid = paper_id
        if not pid and paper_info is not None:
            pid = self._safe_title_id(paper_info)
        if not pid:
            pid = "unknown"
        return self.paper_workspace_dir / pid

    def get_summaries_dir(self, paper_id: Optional[str] = None, paper_info: Optional[Dict[str, Any]] = None) -> Path:
        """获取摘要目录：优先写入 `data/papers/<paper_id>/summaries`。"""
        root = self._paper_root(paper_id, paper_info)
        if root:
            d = root / "summaries"
            d.mkdir(parents=True, exist_ok=True)
            return d

        # 旧结构（兼容）
        if paper_id:
            d = self.summaries_dir / paper_id
            d.mkdir(parents=True, exist_ok=True)
            return d
        self.summaries_dir.mkdir(parents=True, exist_ok=True)
        return self.summaries_dir


    def create_note(
        self,
        paper_info: Dict[str, Any],
        analysis: str,
        key_points: Dict[str, Any],
        paper_id: Optional[str] = None,
    ) -> Path:
        """创建论文笔记：默认写入 `data/papers/<paper_id>/notes/`。"""
        root = self._paper_root(paper_id, paper_info)
        if root:
            paper_dir = root / "notes"
        else:
            # 旧结构（兼容）
            if paper_id:
                paper_dir = self.notes_dir / paper_id
            else:
                paper_title = (paper_info.get("title") or "unknown").replace(" ", "_")[:50]
                paper_dir = self.notes_dir / paper_title

        paper_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_note.md"
        note_path = paper_dir / filename

        note_content = self._generate_markdown_note(paper_info, analysis, key_points)
        note_path.write_text(note_content, encoding="utf-8")
        return note_path


    @staticmethod
    def _to_text(value: Any) -> str:
        """将任意值转换为可写入 Markdown 的字符串。"""
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False, indent=2)
        return str(value)

    def _generate_markdown_note(self, paper_info: Dict[str, Any], analysis: str, key_points: Dict[str, Any]) -> str:
        """生成 Markdown 格式的笔记。"""
        keywords = []
        if isinstance(key_points, dict):
            keywords = [str(x) for x in key_points.get("keywords", [])]

        lines = [
            f"# {paper_info.get('title', 'Unknown Title')}",
            "",
            f"**创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 基本信息",
            "",
            f"- **作者**: {', '.join(paper_info.get('authors', []))}",
            f"- **关键词**: {', '.join(keywords)}",
            "",
            "## 核心贡献",
            "",
            self._to_text(key_points.get("main_contribution", "N/A")) if isinstance(key_points, dict) else "N/A",
            "",
            "## 方法摘要",
            "",
            self._to_text(key_points.get("method_summary", "N/A")) if isinstance(key_points, dict) else "N/A",
            "",
            "## 关键技术",
            "",
        ]

        if isinstance(key_points, dict):
            for technique in key_points.get("key_techniques", []):
                lines.append(f"- {self._to_text(technique)}")

        lines.extend(
            [
                "",
                "## 详细分析",
                "",
                analysis,
                "",
                "## 实验与结果",
                "",
                self._to_text(key_points.get("experiments", "N/A")) if isinstance(key_points, dict) else "N/A",
                "",
                "## 局限性",
                "",
                self._to_text(key_points.get("limitations", "N/A")) if isinstance(key_points, dict) else "N/A",
                "",
                "## 未来工作",
                "",
                self._to_text(key_points.get("future_work", "N/A")) if isinstance(key_points, dict) else "N/A",
                "",
                "## 个人思考",
                "",
                "### 可应用场景",
                "",
                "- [ ] 待补充",
                "",
                "### 实现思路",
                "",
                "- [ ] 待补充",
                "",
                "### 相关论文",
                "",
                "- [ ] 待补充",
                "",
            ]
        )

        return "\n".join(lines)


    def create_knowledge_graph_entry(self, paper_info: Dict[str, Any], key_points: Dict[str, Any]) -> Dict[str, Any]:
        """创建知识图谱条目。"""
        return {
            "id": f"paper_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": paper_info.get("title", ""),
            "authors": paper_info.get("authors", []),
            "keywords": key_points.get("keywords", []) if isinstance(key_points, dict) else [],
            "techniques": key_points.get("key_techniques", []) if isinstance(key_points, dict) else [],
            "contribution": key_points.get("main_contribution", "") if isinstance(key_points, dict) else "",
            "related_papers": [],
            "tags": [],
            "created_at": datetime.now().isoformat(),
        }

    def save_knowledge_graph(
        self,
        entries: List[Dict[str, Any]],
        filename: str = "knowledge_graph.json",
        paper_id: Optional[str] = None,
        paper_info: Optional[Dict[str, Any]] = None,
    ):
        """保存知识图谱：默认写入 `data/papers/<paper_id>/knowledge/knowledge_graph.json`。"""
        root = self._paper_root(paper_id, paper_info)
        if root:
            knowledge_dir = root / "knowledge"
            knowledge_dir.mkdir(parents=True, exist_ok=True)
            graph_path = knowledge_dir / filename
        else:
            # 旧结构（兼容）
            if paper_id:
                paper_dir = self.knowledge_dir / paper_id
                paper_dir.mkdir(parents=True, exist_ok=True)
                graph_path = paper_dir / filename
            else:
                graph_path = self.knowledge_dir / filename

        if graph_path.exists():
            with open(graph_path, "r", encoding="utf-8") as f:
                existing_entries = json.load(f)
            entries = existing_entries + entries

        with open(graph_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)


    def create_summary(self, paper_info: Dict[str, Any], analysis: str) -> str:
        """创建论文摘要（简化版）。"""
        return f"""
# {paper_info.get('title', 'Unknown')} - 摘要

## 核心要点
{analysis[:500]}...

---
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""".strip()
