"""\
论文解析模块
支持解析 PDF、文本等格式的论文
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

import PyPDF2


class PaperParser:
    """论文解析器"""

    def parse_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """解析 PDF 文件。"""
        pdf_path_p = Path(pdf_path)
        if not pdf_path_p.exists():
            raise FileNotFoundError(f"文件不存在: {pdf_path_p}")

        result: Dict[str, Any] = {
            "file_path": str(pdf_path_p),
            "title": "",
            "authors": [],
            "abstract": "",
            "sections": {},
            "full_text": "",
            "metadata": {},
        }

        try:
            with open(pdf_path_p, "rb") as f:
                reader = PyPDF2.PdfReader(f)

                if reader.metadata:
                    result["metadata"] = {
                        "title": reader.metadata.get("/Title", ""),
                        "author": reader.metadata.get("/Author", ""),
                        "subject": reader.metadata.get("/Subject", ""),
                        "creator": reader.metadata.get("/Creator", ""),
                    }

                full_text_parts: List[str] = []
                for page_num, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    full_text_parts.append(f"\n--- Page {page_num + 1} ---\n{text}")

                full_text = "".join(full_text_parts)
                result["full_text"] = full_text

                structured = self._extract_structure(full_text)
                result.update(structured)

        except Exception as e:
            result["error"] = str(e)

        return result

    def parse_text(self, text: str) -> Dict[str, Any]:
        """解析纯文本。"""
        return self._extract_structure(text)

    def _extract_structure(self, text: str) -> Dict[str, Any]:
        """从文本中提取结构化信息（启发式）。"""
        structure: Dict[str, Any] = {
            "title": "",
            "authors": [],
            "abstract": "",
            "sections": {},
        }

        lines = text.split("\n")

        # 标题：通常出现在前几十行；跳过分页标记等噪声
        for line in lines[:60]:
            s = line.strip()
            if not s:
                continue
            if s.startswith("--- Page"):
                continue
            if s.lower().startswith("arxiv"):
                continue
            if s.lower().startswith("abstract"):
                continue
            if 10 < len(s) < 200:
                structure["title"] = s
                break

        # 摘要
        abstract_start = False
        abstract_lines: List[str] = []
        for line in lines:
            lower = line.lower().strip()
            if not abstract_start and lower.startswith("abstract"):
                abstract_start = True
                continue
            if abstract_start:
                if any(k in lower for k in ["introduction", "1.", "keywords", "index terms"]):
                    break
                if line.strip():
                    abstract_lines.append(line.strip())
        structure["abstract"] = " ".join(abstract_lines)

        # 章节
        section_pattern = r"^\s*(\d+)\.?\s+([A-Z][A-Za-z\s\-]{2,})$"
        current_section = None
        section_content: List[str] = []

        for line in lines:
            m = re.match(section_pattern, line.strip())
            if m:
                if current_section:
                    structure["sections"][current_section] = "\n".join(section_content).strip()
                current_section = m.group(2).strip()
                section_content = []
            elif current_section:
                section_content.append(line)

        if current_section:
            structure["sections"][current_section] = "\n".join(section_content).strip()

        return structure

    def extract_references(self, text: str) -> List[Dict[str, str]]:
        """提取参考文献（简化版）。"""
        references: List[Dict[str, str]] = []

        ref_pattern = r"References?\s*\n(.*?)(?=\n[A-Z]|\Z)"
        match = re.search(ref_pattern, text, re.DOTALL | re.IGNORECASE)

        if match:
            ref_text = match.group(1)
            for line in ref_text.split("\n"):
                s = line.strip()
                if s and len(s) > 10:
                    references.append({"text": s, "authors": "", "year": "", "title": ""})

        return references
