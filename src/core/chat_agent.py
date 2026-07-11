"""
图书馆智能服务系统 - 对话式智能助手
支持自然语言交互，融合图书馆服务和大模型通用解题能力
"""

import re
import os
from typing import Optional
from models.user import User, UserType, UserManager, create_sample_users
from algorithms.recommendation import HybridRecommender, create_sample_items, ResourceType
from core.space_management import SpaceManager, SeatType, create_sample_space_manager


class ChatAgent:
    """对话式智能助手"""
    
    def __init__(self):
        self.user_manager = create_sample_users()
        self.all_items = create_sample_items()
        self.recommender = HybridRecommender()
        self.space_manager = create_sample_space_manager()
        self.current_user: Optional[User] = None
        
        self.llm_agent = None
        self._init_llm_agent()
        
        self.greetings = [
            "你好！我是图书馆智能助手，有什么可以帮你的？",
            "你好！欢迎使用图书馆智能服务系统。",
            "嗨！我可以帮你查找书籍、预约座位或获取学习资源推荐。"
        ]
        
        self.farewells = [
            "再见！祝你学习愉快！",
            "感谢使用图书馆智能服务系统，下次见！",
            "拜拜！有需要随时来找我。"
        ]
    
    def _init_llm_agent(self):
        """初始化大模型代理"""
        try:
            from core.llm_agent import LLMAgent
            api_key = os.environ.get("DASHSCOPE_API_KEY")
            self.llm_agent = LLMAgent(api_key)
        except ImportError:
            pass
    
    def greet(self) -> str:
        """问候语"""
        return self.greetings[0]
    
    def farewell(self) -> str:
        """告别语"""
        return self.farewells[0]
    
    def process_input(self, user_input: str) -> str:
        """处理用户输入"""
        user_input = user_input.strip()
        
        if self._is_farewell(user_input):
            return self.farewell()
        
        if self._is_help_request(user_input):
            return self._get_help()
        
        if self._is_login_request(user_input):
            return self._handle_login(user_input)
        
        if self._is_logout_request(user_input):
            return self._handle_logout()
        
        if self._is_recommend_request(user_input):
            return self._handle_recommend(user_input)
        
        if self._is_seat_request(user_input):
            return self._handle_seat(user_input)
        
        if self._is_search_request(user_input):
            return self._handle_search(user_input)
        
        if self._is_user_info_request(user_input):
            return self._handle_user_info(user_input)
        
        if self._is_problem_solving_request(user_input):
            return self._handle_problem_solving(user_input)
        
        if self._is_greeting(user_input):
            return self.greet()
        
        return self._handle_unknown(user_input)
    
    def _is_greeting(self, text: str) -> bool:
        """判断是否为问候"""
        patterns = ["你好", "hello", "hi", "嗨", "您好"]
        return any(pattern in text.lower() for pattern in patterns)
    
    def _is_farewell(self, text: str) -> bool:
        """判断是否为告别"""
        patterns = ["再见", "bye", "拜拜", "退出", "结束"]
        return any(pattern in text.lower() for pattern in patterns)
    
    def _is_help_request(self, text: str) -> bool:
        """判断是否为帮助请求"""
        patterns = ["帮助", "help", "功能", "能做什么", "能干什么"]
        return any(pattern in text.lower() for pattern in patterns)
    
    def _is_login_request(self, text: str) -> bool:
        """判断是否为登录请求"""
        patterns = ["登录", "登录", "sign in", "用户", "我是"]
        return any(pattern in text.lower() for pattern in patterns)
    
    def _is_logout_request(self, text: str) -> bool:
        """判断是否为登出请求"""
        patterns = ["登出", "logout", "退出登录"]
        return any(pattern in text.lower() for pattern in patterns)
    
    def _is_recommend_request(self, text: str) -> bool:
        """判断是否为推荐请求"""
        patterns = ["推荐", "推荐书", "找书", "好书", "文献", "资料"]
        return any(pattern in text.lower() for pattern in patterns)
    
    def _is_seat_request(self, text: str) -> bool:
        """判断是否为座位请求"""
        patterns = ["座位", "座位", "座位预约", "找座位", "占座", "空座"]
        return any(pattern in text.lower() for pattern in patterns)
    
    def _is_search_request(self, text: str) -> bool:
        """判断是否为搜索请求"""
        patterns = ["搜索", "查找", "search", "查询"]
        return any(pattern in text.lower() for pattern in patterns)
    
    def _is_user_info_request(self, text: str) -> bool:
        """判断是否为用户信息请求"""
        patterns = ["用户", "我的", "信息", "资料", "标签"]
        return any(pattern in text.lower() for pattern in patterns)
    
    def _is_problem_solving_request(self, text: str) -> bool:
        """判断是否为解题请求（优先于问候语判断）"""
        solving_keywords = [
            "解", "计算", "证明", "推导", "求", "等于", "答案", "怎么做",
            "编程", "代码", "python", "java", "算法", "实现",
            "写", "作文", "文章", "翻译", "英语", "日语", "韩语",
            "为什么", "什么是", "解释", "说明", "原理", "分析",
            "数学", "物理", "化学", "题", "试卷", "作业", "考试",
            "hello", "hi"
        ]
        
        for keyword in solving_keywords:
            if keyword in text.lower():
                return True
        return False
    
    def _handle_problem_solving(self, text: str) -> str:
        """处理解题请求 - 调用大模型"""
        if self.llm_agent and self.llm_agent.llm.is_available():
            user_context = ""
            if self.current_user:
                user_context = f"当前用户：{self.current_user.name}，{self.current_user.user_type.value}"
            
            return self.llm_agent.chat(text, user_context)
        else:
            return f"""
抱歉，当前未配置大模型，无法解答学习问题。

配置方法：
1. 在 .env 文件中设置 DASHSCOPE_API_KEY
2. 安装依赖：pip install dashscope
3. 重新启动服务

你可以尝试：登录图书馆账号，获取座位预约和资源推荐服务。
            """.strip()
    
    def _get_help(self) -> str:
        """获取帮助信息"""
        llm_available = self.llm_agent and self.llm_agent.llm.is_available()
        
        help_text = """
我可以帮你做以下事情：

📚 图书馆服务
- 用户管理：登录不同类型用户（考研学生/留学生/教师/新生/焦虑学生）
- 资源推荐：根据身份和情境推荐书籍、活动、学习资源
- 座位管理：查询座位分布、预约座位
- 图书搜索：搜索书籍、文献、活动

"""
        
        if llm_available:
            help_text += """
🧠 AI学习助手（已启用）
- 数学解题：求解方程、证明题、计算题
- 编程解答：代码实现、算法题、调试帮助
- 知识问答：百科知识、专业概念、学习辅导
- 作文写作：写文章、论文提纲、演讲稿
- 翻译服务：中英文互译、多语言翻译
- 逻辑推理：分析问题、决策建议

"""
        else:
            help_text += """
🧠 AI学习助手（需要配置大模型API密钥）
- 数学解题：求解方程、证明题、计算题
- 编程解答：代码实现、算法题、调试帮助
- 知识问答：百科知识、专业概念、学习辅导
- 作文写作：写文章、论文提纲、演讲稿
- 翻译服务：中英文互译、多语言翻译

配置方法：设置环境变量 DASHSCOPE_API_KEY

"""
        
        help_text += """
示例指令：
- 图书馆："我是考研学生"、"推荐一些资料"、"帮我找个座位"
- 学习："求x² + 2x + 1 = 0的解"、"用Python实现快速排序"、"翻译这段英文"
- 帮助："帮助"、"再见"
        """
        
        return help_text.strip()
    
    def _handle_login(self, text: str) -> str:
        """处理登录请求"""
        user_types = {
            "考研": UserType.GRADUATE_STUDENT,
            "留学生": UserType.INTERNATIONAL_STUDENT,
            "老师": UserType.TEACHER,
            "教师": UserType.TEACHER,
            "新生": UserType.FRESHMAN,
            "大一": UserType.FRESHMAN,
            "焦虑": UserType.ANXIOUS_STUDENT
        }
        
        detected_type = None
        for keyword, user_type in user_types.items():
            if keyword in text:
                detected_type = user_type
                break
        
        if detected_type:
            users = self.user_manager.get_users_by_type(detected_type)
            if users:
                self.current_user = users[0]
                type_names = {
                    UserType.GRADUATE_STUDENT: "考研学生",
                    UserType.INTERNATIONAL_STUDENT: "留学生",
                    UserType.TEACHER: "教师",
                    UserType.FRESHMAN: "新生",
                    UserType.ANXIOUS_STUDENT: "焦虑学生"
                }
                return f"登录成功！你现在是{type_names[detected_type]}「{self.current_user.name}」。有什么需要帮助的吗？"
        
        return "请告诉我你是哪种用户？（考研学生/留学生/教师/新生/焦虑学生）"
    
    def _handle_logout(self) -> str:
        """处理登出请求"""
        self.current_user = None
        return "已退出登录。欢迎再次使用！"
    
    def _handle_recommend(self, text: str) -> str:
        """处理推荐请求"""
        if not self.current_user:
            return "请先登录（告诉我你的身份：考研学生/留学生/教师/新生/焦虑学生）"
        
        user_type_names = {
            UserType.GRADUATE_STUDENT: "考研学生",
            UserType.INTERNATIONAL_STUDENT: "留学生",
            UserType.TEACHER: "教师",
            UserType.FRESHMAN: "新生",
            UserType.ANXIOUS_STUDENT: "焦虑学生"
        }
        
        context = {}
        if "考试周" in text or "备考" in text or "考研" in text:
            context["exam_week"] = True
        elif "开学" in text:
            context["beginning_semester"] = True
        else:
            context["normal"] = True
        
        recommendations = self.recommender.recommend(self.current_user, context, self.all_items)
        
        if recommendations:
            result = f"\n为{user_type_names[self.current_user.user_type]}「{self.current_user.name}」推荐以下资源：\n"
            for i, item in enumerate(recommendations[:5], 1):
                result += f"\n{i}. {item.title}"
                result += f"\n   - 类型：{item.item_type.value}"
                result += f"\n   - 相关性：{item.relevance_score:.2f}"
                result += f"\n   - 语言：{item.language}"
                result += f"\n   - 标签：{', '.join(item.tags)}"
            return result
        
        return "抱歉，暂时没有找到合适的推荐资源。"
    
    def _handle_seat(self, text: str) -> str:
        """处理座位请求"""
        if not self.current_user:
            return "请先登录（告诉我你的身份：考研学生/留学生/教师/新生/焦虑学生）"
        
        seat_types_display = {
            SeatType.FIXED: "固定座位",
            SeatType.PRIORITY: "优先座位",
            SeatType.DYNAMIC: "动态座位"
        }
        
        if "分布" in text or "统计" in text:
            total = len(self.space_manager.all_seats)
            fixed = len(self.space_manager.fixed_allocator.fixed_seats)
            priority = len(self.space_manager.priority_allocator.priority_seats)
            dynamic = len(self.space_manager.dynamic_scheduler.dynamic_seats)
            
            occupied = sum(1 for s in self.space_manager.all_seats.values() if s.status.name == "OCCUPIED")
            available = sum(1 for s in self.space_manager.all_seats.values() if s.status.name == "AVAILABLE")
            
            return f"""
当前座位分布：
- 总座位数：{total}个
  ├─ 固定座位：{fixed}个（20%）- 优先分配给考研学生
  ├─ 优先座位：{priority}个（30%）- 优先分配给焦虑学生/留学生/新生
  └─ 动态座位：{dynamic}个（50%）- 所有用户共享

当前状态：
- 已占用：{occupied}个
- 可用：{available}个
            """.strip()
        
        seat = self.space_manager.allocate_seat(self.current_user, {"situation": "normal"})
        
        if seat:
            return f"""
座位预约成功！
- 座位ID：{seat.seat_id}
- 座位类型：{seat_types_display[seat.seat_type]}
- 位置：{seat.location}
- 安静度：{'⭐' * seat.quiet_level}
- 私密性：{'🔒' * seat.privacy_level}
- 是否靠窗：{'✅' if seat.has_window else '❌'}
- 是否角落：{'✅' if seat.is_corner else '❌'}
- 是否有插座：{'✅' if seat.has_socket else '❌'}
            """.strip()
        
        return "抱歉，暂时没有可用的座位。"
    
    def _handle_search(self, text: str) -> str:
        """处理搜索请求"""
        keywords = re.findall(r'搜索(.+)', text) or re.findall(r'查找(.+)', text)
        
        if not keywords:
            return "请告诉我你想搜索什么？例如：搜索算法书籍"
        
        keyword = keywords[0].strip()
        
        results = []
        for item in self.all_items:
            if keyword in item.title or keyword in item.description or keyword in item.tags:
                results.append(item)
        
        if results:
            result = f"\n找到 {len(results)} 个相关资源：\n"
            for i, item in enumerate(results[:5], 1):
                result += f"\n{i}. {item.title}"
                result += f"\n   - 类型：{item.item_type.value}"
                result += f"\n   - 描述：{item.description[:30]}..."
                result += f"\n   - 标签：{', '.join(item.tags)}"
            return result
        
        return f"抱歉，没有找到与「{keyword}」相关的资源。"
    
    def _handle_user_info(self, text: str) -> str:
        """处理用户信息请求"""
        if not self.current_user:
            return "请先登录（告诉我你的身份：考研学生/留学生/教师/新生/焦虑学生）"
        
        type_names = {
            UserType.GRADUATE_STUDENT: "考研学生",
            UserType.INTERNATIONAL_STUDENT: "留学生",
            UserType.TEACHER: "教师",
            UserType.FRESHMAN: "新生",
            UserType.ANXIOUS_STUDENT: "焦虑学生"
        }
        
        return f"""
当前用户信息：
- 用户ID：{self.current_user.user_id}
- 姓名：{self.current_user.name}
- 用户类型：{type_names[self.current_user.user_type]}
- 所属院系：{self.current_user.department}
- 用户标签：{', '.join(self.current_user.tags)}
- 用户偏好：{self.current_user.preferences}
        """.strip()
    
    def _handle_unknown(self, text: str) -> str:
        """处理未知请求 - 调用大模型进行通用解题"""
        if self.llm_agent and self.llm_agent.llm.is_available():
            user_context = ""
            if self.current_user:
                user_context = f"当前用户：{self.current_user.name}，{self.current_user.user_type.value}"
            
            return self.llm_agent.chat(text, user_context)
        else:
            return f"""
抱歉，我不太理解你的意思。

你可以尝试以下操作：
- 登录："我是考研学生"
- 获取推荐："推荐一些资料"
- 预约座位："帮我找个座位"
- 搜索书籍："搜索算法书籍"
- 查看帮助："帮助"

📖 学习帮助（需要配置大模型）：
- 数学题："求x² + 2x + 1 = 0的解"
- 编程题："用Python实现快速排序"
- 翻译："翻译这段英文"
- 写作："写一篇关于人工智能的作文"

请告诉我你需要什么帮助？
        """.strip()


def chat_interface():
    """对话界面"""
    agent = ChatAgent()
    
    print("\n" + "="*60)
    print(" 🤖 图书馆智能助手")
    print("="*60)
    print(agent.greet())
    print("="*60)
    
    while True:
        user_input = input("\n你：")
        
        if not user_input.strip():
            continue
        
        response = agent.process_input(user_input)
        print(f"\n助手：{response}")
        
        if agent._is_farewell(user_input):
            break


if __name__ == "__main__":
    chat_interface()