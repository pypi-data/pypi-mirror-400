"""
导读生成模块
为业余读者生成详细的教学引导文档
"""

from typing import Dict, Any, Optional
from pathlib import Path
import yaml
from datetime import datetime


class GuideGenerator:
    """导读生成器"""
    
    def __init__(self, config_path: str = "config.yaml"):

        """
        初始化导读生成器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.reader_config = self.config.get("reader_profile", {})
        self.reader_type = self.reader_config.get("type", "amateur")
        self.reader_profile = self.reader_config.get(self.reader_type, {})
        
        pr = self.config.get("paper_reading", {}) if isinstance(self.config, dict) else {}

        # 新结构：data/papers/<paper_id>/guides
        self.paper_workspace_dir = pr.get("paper_workspace_dir") or pr.get("output_root")
        self.paper_workspace_dir = Path(self.paper_workspace_dir) if self.paper_workspace_dir else None
        if self.paper_workspace_dir:
            self.paper_workspace_dir.mkdir(parents=True, exist_ok=True)

        # 旧结构（兼容）
        guides_dir = pr.get("guides_dir", "data/guides")
        self.guides_dir = Path(guides_dir)
        self.guides_dir.mkdir(parents=True, exist_ok=True)

    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def generate_reading_guide(
        self,
        paper_info: Dict[str, Any],
        analysis: str,
        key_points: Dict[str, Any],
        glossary: Dict[str, Dict[str, str]],
        moonshot_client,
        paper_id: Optional[str] = None
    ) -> Path:
        """
        生成阅读指南
        
        Args:
            paper_info: 论文信息
            analysis: 分析结果
            key_points: 关键点
            glossary: 术语表
            moonshot_client: Moonshot AI 客户端
        
        Returns:
            导读文件路径
        """
        if not self.reader_profile.get("needs_guidance", True):
            # 专业读者不需要详细导读
            return None
        
        # 使用AI生成详细导读
        guide_content = self._generate_ai_guide(
            paper_info, analysis, key_points, glossary, moonshot_client
        )
        
        # 保存导读
        if self.paper_workspace_dir:
            pid = paper_id or paper_info.get("title", "unknown").replace(" ", "_")[:50]
            paper_dir = self.paper_workspace_dir / pid / "guides"
            paper_dir.mkdir(parents=True, exist_ok=True)
            guide_path = paper_dir / "reading_guide.md"
        else:
            if paper_id:
                paper_dir = self.guides_dir / paper_id
                paper_dir.mkdir(parents=True, exist_ok=True)
                filename = "reading_guide.md"
                guide_path = paper_dir / filename
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                paper_title = paper_info.get("title", "unknown").replace(" ", "_")[:50]
                filename = f"{timestamp}_{paper_title}_reading_guide.md"
                guide_path = self.guides_dir / filename

        
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        return guide_path
    
    def _generate_ai_guide(
        self,
        paper_info: Dict[str, Any],
        analysis: str,
        key_points: Dict[str, Any],
        glossary: Dict[str, Dict[str, str]],
        moonshot_client
    ) -> str:
        """使用AI生成详细导读"""
        
        reader_bg = self.reader_profile.get("background", "软件工程背景、高等数学基础的本科学历开发者")
        needs_examples = self.reader_profile.get("needs_examples", True)
        depth = self.reader_profile.get("explanation_depth", "detailed")
        
        # 构建术语表摘要
        glossary_summary = "\n".join([
            f"- **{term}**: {info.get('definition', '')[:100]}"
            for term, info in list(glossary.items())[:20]
        ])
        
        prompt = f"""请为以下论文生成一份详细的阅读指南，读者背景是：{reader_bg}

论文信息：
- 标题：{paper_info.get('title', 'N/A')}
- 作者：{', '.join(paper_info.get('authors', []))}

核心贡献：
{key_points.get('main_contribution', 'N/A')}

主要方法：
{key_points.get('method_summary', 'N/A')}

关键技术：
{', '.join(key_points.get('key_techniques', []))}

重要术语（前20个）：
{glossary_summary}

请生成一份结构化的阅读指南，包括：

1. **阅读前准备**
   - 需要的前置知识
   - 建议阅读顺序
   - 重点关注的章节

2. **核心概念解释**
   - 用通俗易懂的方式解释论文的核心概念
   - 提供类比和例子（如果需要）
   - 解释为什么这些概念重要

3. **技术路线图**
   - 论文的技术路线，用步骤化的方式说明
   - 每一步的作用和意义
   - 关键决策点

4. **难点解析**
   - 识别论文中的难点
   - 提供详细的解释和示例
   - 给出理解建议

5. **实践建议**
   - 如何验证理解
   - 可以尝试的实验
   - 进一步学习的方向

6. **常见问题**
   - 读者可能遇到的问题
   - 解答和提示

请使用Markdown格式，语言要通俗易懂，适合{reader_bg}的读者。"""
        
        messages = [
            {
                "role": "system",
                "content": f"你是一位经验丰富的学术导师，擅长为不同背景的读者提供个性化的论文阅读指导。你能够用通俗易懂的方式解释复杂的概念，并根据读者的背景调整解释的深度。当前读者是：{reader_bg}"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        try:
            response = moonshot_client.chat_completion(messages)
            ai_guide = response["choices"][0]["message"]["content"]
            
            # 添加头部信息
            header = f"""# {paper_info.get('title', 'Unknown')} - 阅读指南

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**读者背景**: {reader_bg}
**阅读难度**: 适合{reader_bg}的详细导读

---

"""
            
            # 添加术语表
            glossary_section = self._format_glossary(glossary)
            
            return header + ai_guide + "\n\n---\n\n" + glossary_section
            
        except Exception as e:
            # 如果AI生成失败，返回基础版本
            return self._generate_basic_guide(paper_info, key_points, glossary)
    
    def _format_glossary(self, glossary: Dict[str, Dict[str, str]]) -> str:
        """格式化术语表"""
        if not glossary:
            return ""
        
        lines = ["## 📚 重要术语表\n"]
        
        for term, info in list(glossary.items())[:30]:  # 限制显示数量
            lines.append(f"### {term}\n")
            lines.append(f"**定义**: {info.get('definition', 'N/A')}\n")
            
            explanation = info.get('explanation', '')
            if explanation:
                lines.append(f"**详细解释**: {explanation}\n")
            
            examples = info.get('examples', [])
            if examples:
                lines.append("**例子**:\n")
                for example in examples[:3]:
                    lines.append(f"- {example}\n")
            
            related = info.get('related_terms', [])
            if related:
                lines.append(f"**相关术语**: {', '.join(related)}\n")
            
            lines.append("\n---\n\n")
        
        return '\n'.join(lines)
    
    def _generate_basic_guide(
        self,
        paper_info: Dict[str, Any],
        key_points: Dict[str, Any],
        glossary: Dict[str, Dict[str, str]]
    ) -> str:
        """生成基础导读（AI失败时的备用方案）"""
        return f"""# {paper_info.get('title', 'Unknown')} - 阅读指南

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 核心概念

{key_points.get('main_contribution', 'N/A')}

## 主要方法

{key_points.get('method_summary', 'N/A')}

## 重要术语

{self._format_glossary(glossary)}
"""
