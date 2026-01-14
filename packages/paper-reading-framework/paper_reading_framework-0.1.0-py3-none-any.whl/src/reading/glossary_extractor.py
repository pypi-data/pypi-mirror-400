"""
术语提取和解释模块
识别论文中的专有名词并提供解释
"""

from typing import List, Dict, Any, Optional
import re
import yaml
from pathlib import Path


class GlossaryExtractor:
    """术语提取器"""
    
    def __init__(self, config_path: str = "config.yaml"):

        """
        初始化术语提取器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.reader_config = self.config.get("reader_profile", {})
        self.reader_type = self.reader_config.get("type", "amateur")
        self.needs_glossary = self.reader_config.get(self.reader_type, {}).get("needs_glossary", True)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def extract_terms(self, paper_content: str) -> List[Dict[str, str]]:
        """
        提取论文中的专有名词
        
        Args:
            paper_content: 论文内容
        
        Returns:
            术语列表，每个术语包含：term, context, frequency
        """
        # 常见的学术术语模式
        patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Algorithm|Method|Model|Framework|System|Approach|Technique|Methodology)\b',
            r'\b[A-Z]{2,}(?:\s+[A-Z]{2,})*\b',  # 缩写词
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b',  # 专有名词短语
        ]
        
        terms = {}
        
        for pattern in patterns:
            matches = re.finditer(pattern, paper_content)
            for match in matches:
                term = match.group().strip()
                if len(term) > 3 and term not in ['The', 'This', 'That', 'These', 'Those']:
                    if term not in terms:
                        terms[term] = {
                            "term": term,
                            "frequency": 0,
                            "contexts": []
                        }
                    terms[term]["frequency"] += 1
                    
                    # 提取上下文
                    start = max(0, match.start() - 100)
                    end = min(len(paper_content), match.end() + 100)
                    context = paper_content[start:end].strip()
                    if context not in terms[term]["contexts"]:
                        terms[term]["contexts"].append(context)
        
        # 按频率排序，返回前50个
        sorted_terms = sorted(terms.values(), key=lambda x: x["frequency"], reverse=True)
        return sorted_terms[:50]
    
    def should_explain_term(self, term: str) -> bool:
        """
        判断是否需要解释某个术语
        
        Args:
            term: 术语
        
        Returns:
            是否需要解释
        """
        return self.needs_glossary


class GlossaryExplainer:
    """术语解释器（使用AI）"""
    
    def __init__(self, moonshot_client):
        """
        初始化解释器
        
        Args:
            moonshot_client: Moonshot AI 客户端
        """
        self.client = moonshot_client
    
    def explain_term(
        self,
        term: str,
        context: str,
        reader_background: str = "软件工程背景、高等数学基础的本科学历开发者"
    ) -> Dict[str, str]:
        """
        解释术语
        
        Args:
            term: 术语
            context: 上下文
            reader_background: 读者背景
        
        Returns:
            解释字典，包含：definition, explanation, examples, related_terms
        """
        prompt = f"""请为以下术语提供详细解释，读者背景是：{reader_background}

术语：{term}
上下文：{context}

请提供：
1. 简洁定义（1-2句话）
2. 详细解释（适合读者背景的理解）
3. 实际例子或类比（如果适用）
4. 相关术语（如果有）

请以JSON格式返回：
{{
    "definition": "简洁定义",
    "explanation": "详细解释",
    "examples": ["例子1", "例子2"],
    "related_terms": ["相关术语1", "相关术语2"]
}}"""
        
        messages = [
            {
                "role": "system",
                "content": "你是一位专业的学术术语解释专家，擅长用通俗易懂的方式解释复杂的学术概念，能够根据读者的背景调整解释的深度和方式。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        try:
            response = self.client.chat_completion(messages)
            content = response["choices"][0]["message"]["content"]
            
            # 尝试解析JSON
            import json
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            
            # 如果解析失败，返回原始内容
            return {
                "definition": content[:200],
                "explanation": content,
                "examples": [],
                "related_terms": []
            }
        except Exception as e:
            return {
                "definition": f"术语：{term}",
                "explanation": f"解释生成失败：{str(e)}",
                "examples": [],
                "related_terms": []
            }
    
    def explain_terms_batch(
        self,
        terms: List[Dict[str, Any]],
        reader_background: str
    ) -> Dict[str, Dict[str, str]]:
        """
        批量解释术语
        
        Args:
            terms: 术语列表
            reader_background: 读者背景
        
        Returns:
            术语解释字典
        """
        glossary = {}
        
        for term_info in terms[:20]:  # 限制数量，避免过多API调用
            term = term_info["term"]
            context = term_info["contexts"][0] if term_info["contexts"] else ""
            
            explanation = self.explain_term(term, context, reader_background)
            glossary[term] = explanation
        
        return glossary
