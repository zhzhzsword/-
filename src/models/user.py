"""
用户模型模块
定义不同用户群体及其特征
"""

from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime


class UserType(Enum):
    """用户类型枚举"""
    GRADUATE_STUDENT = "graduate_student"  # 考研学生
    INTERNATIONAL_STUDENT = "international_student"  # 留学生
    TEACHER = "teacher"  # 教师
    FRESHMAN = "freshman"  # 新生
    ANXIOUS_STUDENT = "anxious_student"  # 焦虑学生
    NORMAL_USER = "normal_user"  # 普通用户


class EmotionState(Enum):
    """情绪状态枚举"""
    CALM = "calm"  # 平静
    STRESSED = "stressed"  # 压力大
    ANXIOUS = "anxious"  # 焦虑
    EXCITED = "excited"  # 兴奋


class LanguageLevel(Enum):
    """中文水平枚举"""
    HSK1 = "HSK1"
    HSK2 = "HSK2"
    HSK3 = "HSK3"
    HSK4 = "HSK4"
    HSK5 = "HSK5"
    HSK6 = "HSK6"
    NATIVE = "native"  # 中文母语


class User:
    """用户基类"""
    
    def __init__(
        self,
        user_id: str,
        name: str,
        user_type: UserType,
        email: str,
        department: str,
        grade: int,
        register_date: datetime
    ):
        self.user_id = user_id
        self.name = name
        self.user_type = user_type
        self.email = email
        self.department = department
        self.grade = grade
        self.register_date = register_date
        
        # 用户行为数据
        self.borrow_history: List[str] = []  # 借阅历史
        self.seat_usage_history: List[Dict] = []  # 座位使用历史
        self.search_history: List[str] = []  # 搜索历史
        self.resource_usage_history: List[str] = []  # 资源使用历史
        
        # 用户偏好
        self.preferences: Dict = {}
        
        # 用户标签
        self.tags: List[str] = []
    
    def add_borrow_record(self, book_id: str):
        """添加借阅记录"""
        self.borrow_history.append(book_id)
    
    def add_seat_usage(self, seat_id: str, start_time: datetime, end_time: datetime):
        """添加座位使用记录"""
        self.seat_usage_history.append({
            "seat_id": seat_id,
            "start_time": start_time,
            "end_time": end_time,
            "duration": (end_time - start_time).total_seconds() / 3600  # 小时
        })
    
    def add_search_record(self, query: str):
        """添加搜索记录"""
        self.search_history.append(query)
    
    def update_preferences(self, key: str, value: any):
        """更新用户偏好"""
        self.preferences[key] = value
    
    def add_tag(self, tag: str):
        """添加用户标签"""
        if tag not in self.tags:
            self.tags.append(tag)


class GraduateStudent(User):
    """考研学生"""
    
    def __init__(
        self,
        user_id: str,
        name: str,
        email: str,
        department: str,
        grade: int,
        register_date: datetime,
        exam_subjects: List[str],
        exam_date: datetime,
        preparation_duration: int  # 备考时长（月）
    ):
        super().__init__(
            user_id, name, UserType.GRADUATE_STUDENT,
            email, department, grade, register_date
        )
        
        self.exam_subjects = exam_subjects  # 考试科目
        self.exam_date = exam_date  # 考试日期
        self.preparation_duration = preparation_duration  # 备考时长
        
        # 考研特定标签
        self.add_tag("考研")
        for subject in exam_subjects:
            self.add_tag(subject)
        
        # 考研学生特定偏好
        self.update_preferences("study_duration_target", 10)  # 目标学习时长（小时/天）
        self.update_preferences("fixed_seat_needed", True)  # 是否需要固定座位


class InternationalStudent(User):
    """留学生"""
    
    def __init__(
        self,
        user_id: str,
        name: str,
        email: str,
        department: str,
        grade: int,
        register_date: datetime,
        nationality: str,
        chinese_level: LanguageLevel,
        major_subjects: List[str]
    ):
        super().__init__(
            user_id, name, UserType.INTERNATIONAL_STUDENT,
            email, department, grade, register_date
        )
        
        self.nationality = nationality  # 国籍
        self.chinese_level = chinese_level  # 中文水平
        self.major_subjects = major_subjects  # 专业科目
        
        # 留学生特定标签
        self.add_tag("留学生")
        self.add_tag(nationality)
        self.add_tag(chinese_level.value)
        
        # 留学生特定偏好
        self.update_preferences("english_resources_ratio", 0.6)  # 英文资源偏好比例
        self.update_preferences("cross_cultural_support_needed", True)  # 跨文化支持需求


class Teacher(User):
    """教师"""
    
    def __init__(
        self,
        user_id: str,
        name: str,
        email: str,
        department: str,
        grade: int,  # 教师年级为工作年限
        register_date: datetime,
        research_areas: List[str],
        courses: List[str]
    ):
        super().__init__(
            user_id, name, UserType.TEACHER,
            email, department, grade, register_date
        )
        
        self.research_areas = research_areas  # 研究方向
        self.courses = courses  # 教授课程
        
        # 教师特定标签
        self.add_tag("教师")
        for area in research_areas:
            self.add_tag(area)
        
        # 教师特定偏好
        self.update_preferences("new_book_tracking", True)  # 新书追踪需求
        self.update_preferences("teaching_resources_needed", True)  # 教学资源需求


class Freshman(User):
    """新生"""
    
    def __init__(
        self,
        user_id: str,
        name: str,
        email: str,
        department: str,
        grade: int,
        register_date: datetime,
        career_goal: Optional[str] = None
    ):
        super().__init__(
            user_id, name, UserType.FRESHMAN,
            email, department, grade, register_date
        )
        
        self.career_goal = career_goal  # 职业目标
        
        # 新生特定标签
        self.add_tag("新生")
        if career_goal:
            self.add_tag(career_goal)
        
        # 新生特定偏好
        self.update_preferences("tutorial_needed", True)  # 新手引导需求
        self.update_preferences("social_integration_needed", True)  # 社交融入需求


class AnxiousStudent(User):
    """焦虑学生"""
    
    def __init__(
        self,
        user_id: str,
        name: str,
        email: str,
        department: str,
        grade: int,
        register_date: datetime,
        emotion_state: EmotionState,
        stress_level: int  # 压力水平（1-5）
    ):
        super().__init__(
            user_id, name, UserType.ANXIOUS_STUDENT,
            email, department, grade, register_date
        )
        
        self.emotion_state = emotion_state  # 当前情绪状态
        self.stress_level = stress_level  # 压力水平
        
        # 焦虑学生特定标签
        self.add_tag("焦虑学生")
        self.add_tag(emotion_state.value)
        self.add_tag(f"压力等级{stress_level}")
        
        # 焦虑学生特定偏好
        self.update_preferences("quiet_corner_needed", True)  # 安静角落需求
        self.update_preferences("mental_support_needed", True)  # 心理支持需求


class UserManager:
    """用户管理器"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}  # 用户字典
        self.user_counter = 0  # 用户计数器
    
    def create_user(self, user_type: UserType, **kwargs) -> User:
        """创建用户"""
        user_id = f"U{self.user_counter:04d}"
        self.user_counter += 1
        
        # 根据用户类型创建对应实例
        if user_type == UserType.GRADUATE_STUDENT:
            user = GraduateStudent(
                user_id=user_id, **kwargs
            )
        elif user_type == UserType.INTERNATIONAL_STUDENT:
            user = InternationalStudent(
                user_id=user_id, **kwargs
            )
        elif user_type == UserType.TEACHER:
            user = Teacher(
                user_id=user_id, **kwargs
            )
        elif user_type == UserType.FRESHMAN:
            user = Freshman(
                user_id=user_id, **kwargs
            )
        elif user_type == UserType.ANXIOUS_STUDENT:
            user = AnxiousStudent(
                user_id=user_id, **kwargs
            )
        else:
            user = User(
                user_id=user_id, user_type=user_type, **kwargs
            )
        
        self.users[user_id] = user
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """获取用户"""
        return self.users.get(user_id)
    
    def get_users_by_type(self, user_type: UserType) -> List[User]:
        """根据用户类型获取用户列表"""
        return [
            user for user in self.users.values()
            if user.user_type == user_type
        ]
    
    def update_user_behavior(self, user_id: str, behavior_type: str, data: any):
        """更新用户行为数据"""
        user = self.get_user(user_id)
        if not user:
            return
        
        if behavior_type == "borrow":
            user.add_borrow_record(data)
        elif behavior_type == "seat_usage":
            user.add_seat_usage(**data)
        elif behavior_type == "search":
            user.add_search_record(data)


# 示例数据
def create_sample_users() -> UserManager:
    """创建示例用户"""
    manager = UserManager()
    
    # 考研学生示例
    from datetime import datetime, timedelta
    grad_student = manager.create_user(
        UserType.GRADUATE_STUDENT,
        name="李明",
        email="liming@example.com",
        department="计算机学院",
        grade=4,
        register_date=datetime(2025, 9, 1),
        exam_subjects=["数学", "英语", "专业课"],
        exam_date=datetime(2026, 12, 25),
        preparation_duration=8
    )
    
    # 留学生示例
    intl_student = manager.create_user(
        UserType.INTERNATIONAL_STUDENT,
        name="Ahmed",
        email="ahmed@example.com",
        department="计算机学院",
        grade=1,
        register_date=datetime(2025, 9, 1),
        nationality="Pakistan",
        chinese_level=LanguageLevel.HSK4,
        major_subjects=["人工智能", "数据科学"]
    )
    
    # 教师示例
    teacher = manager.create_user(
        UserType.TEACHER,
        name="王老师",
        email="wanglaoshi@example.com",
        department="教育学院",
        grade=15,  # 工作年限
        register_date=datetime(2010, 9, 1),
        research_areas=["学习科学", "教育心理学"],
        courses=["教育心理学", "学习方法论"]
    )
    
    # 新生示例
    freshman = manager.create_user(
        UserType.FRESHMAN,
        name="张小华",
        email="zhangxiaohua@example.com",
        department="新闻传播学院",
        grade=1,
        register_date=datetime(2025, 9, 1),
        career_goal="记者"
    )
    
    # 焦虑学生示例
    anxious_student = manager.create_user(
        UserType.ANXIOUS_STUDENT,
        name="匿名",
        email="anonymous@example.com",
        department="法学院",
        grade=3,
        register_date=datetime(2023, 9, 1),
        emotion_state=EmotionState.STRESSED,
        stress_level=4
    )
    
    return manager


if __name__ == "__main__":
    # 测试用户管理
    manager = create_sample_users()
    print(f"创建用户数：{len(manager.users)}")
    
    # 测试考研学生
    grad_users = manager.get_users_by_type(UserType.GRADUATE_STUDENT)
    print(f"考研学生数：{len(grad_users)}")
    if grad_users:
        grad_user = grad_users[0]
        print(f"考研学生标签：{grad_user.tags}")
        print(f"考研科目：{grad_user.exam_subjects}")