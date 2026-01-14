"""
Moonshot AI API 客户端
用于与 Moonshot AI (Kimi) 进行交互
使用国内 API 端点: https://api.moonshot.cn/v1
"""

import os
import yaml
from typing import Optional, List, Dict, Any
from pathlib import Path
from openai import OpenAI

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # 如果没有安装 python-dotenv，手动加载 .env 文件
    try:
        env_file = Path(__file__).parent.parent.parent / ".env"
        if env_file.exists():
            import os
            with open(env_file, 'r', encoding='utf-8-sig') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
    except:
        pass


class MoonshotClient:
    """Moonshot AI API 客户端"""
    
    def __init__(self, config_path: str = "config.yaml"):

        """
        初始化客户端
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.api_key = os.getenv("MOONSHOT_API_KEY") or self.config.get("moonshot", {}).get("api_key", "")
        # 使用国内 API 端点
        self.base_url = self.config.get("moonshot", {}).get("base_url", "https://api.moonshot.cn/v1")
        self.model = self.config.get("moonshot", {}).get("model", "moonshot-v1-8k")
        self.temperature = self.config.get("moonshot", {}).get("temperature", 0.7)
        self.max_tokens = self.config.get("moonshot", {}).get("max_tokens", 4096)
        
        if not self.api_key:
            raise ValueError("请设置 MOONSHOT_API_KEY 环境变量或在 config.yaml 中配置 api_key")
        
        # 初始化 OpenAI 客户端（兼容 Moonshot API）
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
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

    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        发送聊天请求（使用 OpenAI SDK，兼容 Moonshot API）
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            model: 模型名称，默认使用配置中的模型
            temperature: 温度参数
            max_tokens: 最大token数
        
        Returns:
            API 响应结果
        """
        try:
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature if temperature is not None else self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            
            # 转换为字典格式以保持兼容性
            return {
                "choices": [{
                    "message": {
                        "role": response.choices[0].message.role,
                        "content": response.choices[0].message.content
                    }
                }],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            raise Exception(f"API 调用失败: {str(e)}")
    
    def analyze_paper(
        self,
        paper_content: str,
        analysis_type: str = "comprehensive",
        reader_profile: Optional[Dict[str, Any]] = None,
        paper_url: Optional[str] = None
    ) -> str:
        """
        分析论文内容
        
        Args:
            paper_content: 论文内容（文本）或 arXiv URL
            analysis_type: 分析类型
                - "comprehensive": 全面分析
                - "summary": 摘要
                - "methodology": 方法论
                - "innovation": 创新点
                - "implementation": 实现要点
            reader_profile: 读者配置，如果提供则使用教学引导模式
            paper_url: 论文 URL（如果提供，将优先使用 URL 进行分析）
        
        Returns:
            分析结果
        """
        # 根据读者类型调整提示词
        reader_context = ""
        if reader_profile:
            reader_type = reader_profile.get("type", "amateur")
            reader_bg = reader_profile.get(reader_type, {}).get("background", "")
            needs_guidance = reader_profile.get(reader_type, {}).get("needs_guidance", True)
            
            if needs_guidance and reader_type == "amateur":
                reader_context = f"\n\n注意：读者背景是{reader_bg}，请用通俗易懂的方式解释，提供更多教学引导，对专业术语进行解释，使用类比和例子帮助理解。"
        
        # 如果提供了 URL 或 paper_content 是 URL，使用 URL 分析
        if paper_url or (paper_content.startswith("http://") or paper_content.startswith("https://")):
            url = paper_url or paper_content
            content_text = f"论文链接：{url}\n\n请访问并分析这篇论文的内容。"
        else:
            content_text = f"论文内容：\n{paper_content}"
        
        prompts = {
            "comprehensive": f"""请对以下论文进行全面分析，包括：
1. 论文核心问题和研究目标
2. 主要方法和创新点
3. 实验结果和贡献
4. 技术细节和实现要点
5. 潜在应用场景
6. 可改进方向{reader_context}

{content_text}""",
            "summary": f"""请为以下论文生成简洁的摘要，包括：
- 研究问题
- 主要方法
- 核心贡献{reader_context}

{content_text}""",
            "methodology": f"""请详细分析以下论文的方法论，包括：
- 技术路线
- 算法流程
- 关键步骤
- 数学公式和原理{reader_context}

{content_text}""",
            "innovation": f"""请提取以下论文的创新点：
- 主要创新
- 与现有方法的区别
- 技术突破{reader_context}

{content_text}""",
            "implementation": f"""请分析以下论文的实现要点：
- 关键技术细节
- 代码实现思路
- 参数设置
- 实验配置{reader_context}

{content_text}"""
        }
        
        prompt = prompts.get(analysis_type, prompts["comprehensive"])
        
        # 根据读者类型调整系统提示
        system_prompt = "你是一位专业的学术论文分析专家，擅长深入理解计算机图形学、人工智能等领域的论文，并能提供精准的分析和实用的建议。"
        if reader_profile and reader_profile.get(reader_profile.get("type", "amateur"), {}).get("needs_guidance", False):
            system_prompt = "你是一位经验丰富的学术导师，擅长为不同背景的读者提供个性化的论文分析。你能够用通俗易懂的方式解释复杂的概念，提供教学引导，并使用类比和例子帮助理解。"
        
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = self.chat_completion(messages)
        return response["choices"][0]["message"]["content"]
    
    def extract_key_points(self, paper_content: str) -> Dict[str, Any]:
        """
        提取论文关键点
        
        Returns:
            包含关键信息的字典
        """
        prompt = """请从以下论文中提取关键信息，以JSON格式返回：
{{
    "title": "论文标题",
    "authors": ["作者列表"],
    "keywords": ["关键词列表"],
    "main_contribution": "主要贡献",
    "method_summary": "方法摘要",
    "key_techniques": ["关键技术列表"],
    "experiments": "实验设置和结果",
    "limitations": "局限性",
    "future_work": "未来工作"
}}

论文内容：
{content}"""
        
        messages = [
            {
                "role": "system",
                "content": "你是一位专业的学术论文分析专家，擅长提取论文的关键信息。请以JSON格式返回结果。"
            },
            {
                "role": "user",
                "content": prompt.format(content=paper_content[:50000])  # 限制长度
            }
        ]
        
        response = self.chat_completion(messages)
        content = response["choices"][0]["message"]["content"]
        
        # 尝试解析JSON（可能需要清理格式）
        import json
        import re
        
        # 提取JSON部分
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        
        return {"raw_response": content}
    
    def generate_implementation_guide(self, paper_content: str) -> str:
        """
        生成实现指南
        
        Returns:
            实现指南文本
        """
        prompt = """基于以下论文，生成详细的实现指南，包括：
1. 技术栈选择
2. 核心算法实现步骤
3. 关键代码结构
4. 参数配置建议
5. 测试和验证方法
6. 常见问题和解决方案

论文内容：
{content}"""
        
        messages = [
            {
                "role": "system",
                "content": "你是一位经验丰富的软件工程师和算法实现专家，擅长将学术论文转化为可执行的代码实现。"
            },
            {
                "role": "user",
                "content": prompt.format(content=paper_content[:50000])
            }
        ]
        
        response = self.chat_completion(messages)
        return response["choices"][0]["message"]["content"]
