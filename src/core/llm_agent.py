"""
图书馆智能服务系统 - 大模型集成代理
支持通义千问API，提供通用解题能力
"""

import os
import json
import re
from typing import Optional


class LLMClient:
    """大模型客户端"""
    
    def __init__(self, api_key: str = None, model: str = "qwen-turbo"):
        self.api_key = api_key or os.environ.get("DASHSCOPE_API_KEY")
        self.model = model
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """初始化大模型客户端"""
        if self.api_key:
            try:
                from dashscope import Generation
                self.client = Generation
            except ImportError:
                pass
    
    def is_available(self) -> bool:
        """检查大模型是否可用"""
        return self.client is not None and self.api_key is not None
    
    def generate(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> str:
        """调用大模型生成响应"""
        if not self.is_available():
            return self._fallback_response(prompt)
        
        try:
            response = self.client.call(
                self.model,
                prompt=prompt,
                api_key=self.api_key,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            if response.status_code == 200:
                return response.output.text
            else:
                return f"大模型调用失败: {response.message}"
        except Exception as e:
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """本地回退响应"""
        return f"""
抱歉，当前未配置大模型API密钥，无法调用AI能力。

你可以通过以下方式启用大模型：
1. 安装依赖：pip install dashscope
2. 设置环境变量：export DASHSCOPE_API_KEY=你的密钥
3. 重新启动服务

如需帮助，请访问：https://help.aliyun.com/document_detail/611472.html
        """.strip()


class LLMAgent:
    """大模型智能代理"""
    
    def __init__(self, api_key: str = None):
        self.llm = LLMClient(api_key)
        self.system_prompt = """
你是一个全能的智能助手，同时具备以下两种能力：

【图书馆智能服务能力】
- 用户管理：支持登录不同类型用户（考研学生、留学生、教师、新生、焦虑学生）
- 资源推荐：根据用户身份和情境推荐书籍、活动、学习资源
- 座位管理：查询座位分布、预约座位、管理座位分配
- 图书搜索：搜索书籍、文献、活动等资源

【通用解题能力】
- 数学问题解答
- 编程问题解答
- 知识问答
- 学习辅导
- 作文写作
- 翻译服务
- 逻辑推理

请根据用户问题的类型，选择合适的能力进行回答：
- 如果是图书馆相关问题（书籍、座位、用户管理等），使用图书馆服务能力
- 如果是学习问题（解题、写作、编程等），使用通用解题能力
- 如果不确定，可以询问用户

请用友好、专业的语言回答问题。
        """.strip()
    
    def chat(self, user_input: str, context: str = "") -> str:
        """处理用户对话"""
        prompt = f"""
{self.system_prompt}

上下文：{context}

用户问题：{user_input}

请给出详细、专业的回答：
        """.strip()
        
        return self.llm.generate(prompt)
    
    def solve_math(self, problem: str) -> str:
        """解决数学问题"""
        prompt = f"""
你是一位数学专家，请详细解答以下数学问题：

问题：{problem}

请按照以下格式回答：
1. 题目分析
2. 解题思路
3. 详细步骤
4. 最终答案

请确保步骤清晰，易于理解。
        """.strip()
        
        return self.llm.generate(prompt)
    
    def solve_coding(self, problem: str) -> str:
        """解决编程问题"""
        prompt = f"""
你是一位编程专家，请详细解答以下编程问题：

问题：{problem}

请按照以下格式回答：
1. 问题分析
2. 解题思路
3. 代码实现（包含注释）
4. 代码解释

请确保代码可运行，注释清晰。
        """.strip()
        
        return self.llm.generate(prompt)
    
    def write_essay(self, topic: str, requirements: str = "") -> str:
        """写作服务"""
        prompt = f"""
你是一位写作专家，请根据以下主题写一篇文章：

主题：{topic}
要求：{requirements}

请写出一篇结构清晰、内容丰富、语言优美的文章。
        """.strip()
        
        return self.llm.generate(prompt)
    
    def translate(self, text: str, target_language: str = "中文") -> str:
        """翻译服务"""
        prompt = f"""
请将以下文本翻译成{target_language}：

原文：{text}

请确保翻译准确、流畅、符合目标语言习惯。
        """.strip()
        
        return self.llm.generate(prompt)
    
    def is_library_related(self, text: str) -> bool:
        """判断是否为图书馆相关问题"""
        library_keywords = [
            "图书馆", "书籍", "图书", "座位", "座位", "预约", "推荐",
            "考研", "留学生", "教师", "新生", "焦虑", "资源", "文献",
            "书架", "借阅", "查询", "搜索", "自习", "学习", "资料"
        ]
        
        for keyword in library_keywords:
            if keyword in text:
                return True
        return False
    
    def is_problem_solving(self, text: str) -> bool:
        """判断是否为解题问题"""
        solving_keywords = [
            "解", "计算", "证明", "推导", "求", "等于", "答案", "怎么做",
            "编程", "代码", "python", "java", "算法", "实现",
            "写", "作文", "文章", "翻译", "英语", "日语", "韩语",
            "为什么", "什么是", "解释", "说明", "原理", "分析",
            "数学", "物理", "化学", "题", "试卷", "作业", "考试"
        ]
        
        for keyword in solving_keywords:
            if keyword in text.lower():
                return True
        return False