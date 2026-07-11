"""
学习相关数据模型：学习路径、共读小组、学习记录、番茄钟
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from enum import Enum


class PathStatus(Enum):
    """学习路径状态"""
    NOT_STARTED = "未开始"
    IN_PROGRESS = "进行中"
    COMPLETED = "已完成"


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "待完成"
    IN_PROGRESS = "进行中"
    COMPLETED = "已完成"
    SKIPPED = "已跳过"


class ReadingGroupStatus(Enum):
    """共读小组状态"""
    RECRUITING = "招募中"
    IN_PROGRESS = "进行中"
    COMPLETED = "已完成"


class PomodoroStatus(Enum):
    """番茄钟状态"""
    IDLE = "空闲"
    WORKING = "专注中"
    BREAK = "休息中"


class StudyRecord:
    """学习记录"""
    
    def __init__(self, user_id: str, date: str, duration_minutes: int, 
                 subject: str, content: str, book_title: str = ""):
        self.record_id = str(uuid.uuid4())[:8]
        self.user_id = user_id
        self.date = date
        self.duration_minutes = duration_minutes
        self.subject = subject
        self.content = content
        self.book_title = book_title
        self.created_at = datetime.now()


class LearningPathTask:
    """学习路径任务"""
    
    def __init__(self, title: str, description: str, duration_days: int, 
                 resources: List[str] = None, day: int = 1):
        self.task_id = str(uuid.uuid4())[:8]
        self.title = title
        self.description = description
        self.duration_days = duration_days
        self.resources = resources or []
        self.status = TaskStatus.PENDING
        self.day = day
        self.progress = 0.0


class LearningPath:
    """学习路径"""
    
    def __init__(self, user_id: str, path_type: str, title: str, 
                 description: str, total_days: int):
        self.path_id = str(uuid.uuid4())[:8]
        self.user_id = user_id
        self.path_type = path_type
        self.title = title
        self.description = description
        self.total_days = total_days
        self.tasks: List[LearningPathTask] = []
        self.status = PathStatus.NOT_STARTED
        self.current_day = 0
        self.progress = 0.0
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
    
    def add_task(self, task: LearningPathTask):
        """添加任务"""
        self.tasks.append(task)
    
    def start(self):
        """开始学习路径"""
        self.status = PathStatus.IN_PROGRESS
        self.current_day = 1
        self.started_at = datetime.now()
        if self.tasks:
            self.tasks[0].status = TaskStatus.IN_PROGRESS
    
    def complete_task(self, task_id: str) -> bool:
        """完成任务"""
        for task in self.tasks:
            if task.task_id == task_id:
                task.status = TaskStatus.COMPLETED
                task.progress = 100.0
                self._update_progress()
                
                completed_count = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
                if completed_count == len(self.tasks):
                    self.status = PathStatus.COMPLETED
                    self.completed_at = datetime.now()
                return True
        return False
    
    def _update_progress(self):
        """更新进度"""
        if not self.tasks:
            self.progress = 0.0
            return
        completed = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        self.progress = (completed / len(self.tasks)) * 100
    
    def get_today_tasks(self) -> List[LearningPathTask]:
        """获取今日任务"""
        return [t for t in self.tasks if t.day == self.current_day and t.status != TaskStatus.COMPLETED]


class ReadingGroupMember:
    """共读小组成员"""
    
    def __init__(self, user_id: str, user_name: str, role: str = "member"):
        self.user_id = user_id
        self.user_name = user_name
        self.role = role
        self.joined_at = datetime.now()
        self.reading_progress = 0.0
        self.notes_count = 0


class ReadingNote:
    """读书笔记"""
    
    def __init__(self, group_id: str, user_id: str, user_name: str, 
                 content: str, chapter: str = ""):
        self.note_id = str(uuid.uuid4())[:8]
        self.group_id = group_id
        self.user_id = user_id
        self.user_name = user_name
        self.content = content
        self.chapter = chapter
        self.likes = 0
        self.comments: List[str] = []
        self.created_at = datetime.now()


class ReadingGroup:
    """共读小组"""
    
    def __init__(self, creator_id: str, creator_name: str, book_title: str, 
                 description: str, max_members: int = 20, duration_days: int = 30):
        self.group_id = str(uuid.uuid4())[:8]
        self.creator_id = creator_id
        self.creator_name = creator_name
        self.book_title = book_title
        self.description = description
        self.max_members = max_members
        self.duration_days = duration_days
        self.status = ReadingGroupStatus.RECRUITING
        self.members: List[ReadingGroupMember] = []
        self.notes: List[ReadingNote] = []
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        
        self.add_member(creator_id, creator_name, "creator")
    
    def add_member(self, user_id: str, user_name: str, role: str = "member") -> bool:
        """添加成员"""
        if len(self.members) >= self.max_members:
            return False
        if any(m.user_id == user_id for m in self.members):
            return False
        
        member = ReadingGroupMember(user_id, user_name, role)
        self.members.append(member)
        return True
    
    def add_note(self, user_id: str, user_name: str, content: str, chapter: str = "") -> ReadingNote:
        """添加笔记"""
        note = ReadingNote(self.group_id, user_id, user_name, content, chapter)
        self.notes.append(note)
        
        for member in self.members:
            if member.user_id == user_id:
                member.notes_count += 1
                break
        
        return note
    
    def like_note(self, note_id: str) -> bool:
        """点赞笔记"""
        for note in self.notes:
            if note.note_id == note_id:
                note.likes += 1
                return True
        return False
    
    def start_reading(self):
        """开始共读"""
        self.status = ReadingGroupStatus.IN_PROGRESS
        self.started_at = datetime.now()


class PomodoroSession:
    """番茄钟会话"""
    
    def __init__(self, user_id: str, work_minutes: int = 25, break_minutes: int = 5):
        self.session_id = str(uuid.uuid4())[:8]
        self.user_id = user_id
        self.work_minutes = work_minutes
        self.break_minutes = break_minutes
        self.status = PomodoroStatus.IDLE
        self.current_cycle = 0
        self.total_work_minutes = 0
        self.completed_cycles = 0
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.created_at = datetime.now()
    
    def start_work(self):
        """开始专注"""
        self.status = PomodoroStatus.WORKING
        self.start_time = datetime.now()
        self.current_cycle += 1
    
    def start_break(self):
        """开始休息"""
        self.status = PomodoroStatus.BREAK
        self.total_work_minutes += self.work_minutes
        self.completed_cycles += 1
    
    def stop(self):
        """停止"""
        self.status = PomodoroStatus.IDLE
        self.end_time = datetime.now()
    
    def reset(self):
        """重置"""
        self.status = PomodoroStatus.IDLE
        self.current_cycle = 0
        self.total_work_minutes = 0
        self.completed_cycles = 0
        self.start_time = None
        self.end_time = None


class LearningStats:
    """学习统计"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.total_study_days = 0
        self.total_study_minutes = 0
        self.total_books_read = 0
        self.total_notes = 0
        self.total_pomodoros = 0
        self.streak_days = 0
        self.weekly_minutes: Dict[str, int] = {}
        self.subject_distribution: Dict[str, int] = {}
        self.records: List[StudyRecord] = []
    
    def add_record(self, record: StudyRecord):
        """添加学习记录"""
        self.records.append(record)
        self.total_study_minutes += record.duration_minutes
        
        if record.subject in self.subject_distribution:
            self.subject_distribution[record.subject] += record.duration_minutes
        else:
            self.subject_distribution[record.subject] = record.duration_minutes
        
        unique_dates = set(r.date for r in self.records)
        self.total_study_days = len(unique_dates)
    
    def get_weekly_data(self) -> Dict[str, int]:
        """获取近7天数据"""
        result = {}
        today = datetime.now()
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            date_str = date.strftime("%m-%d")
            day_minutes = sum(
                r.duration_minutes for r in self.records 
                if r.date == date.strftime("%Y-%m-%d")
            )
            result[date_str] = day_minutes
        return result


class LearningManager:
    """学习管理器"""
    
    def __init__(self):
        self.learning_paths: Dict[str, LearningPath] = {}
        self.reading_groups: Dict[str, ReadingGroup] = {}
        self.pomodoro_sessions: Dict[str, PomodoroSession] = {}
        self.user_stats: Dict[str, LearningStats] = {}
        self.user_paths: Dict[str, List[str]] = {}
        self.user_groups: Dict[str, List[str]] = {}
    
    def create_learning_path(self, user_id: str, path_type: str, 
                            title: str, description: str, 
                            tasks_data: List[Dict]) -> LearningPath:
        """创建学习路径"""
        total_days = max(t.get("day", 1) for t in tasks_data)
        path = LearningPath(user_id, path_type, title, description, total_days)
        
        for task_data in tasks_data:
            task = LearningPathTask(
                title=task_data["title"],
                description=task_data.get("description", ""),
                duration_days=task_data.get("duration_days", 1),
                resources=task_data.get("resources", []),
                day=task_data.get("day", 1)
            )
            path.add_task(task)
        
        self.learning_paths[path.path_id] = path
        
        if user_id not in self.user_paths:
            self.user_paths[user_id] = []
        self.user_paths[user_id].append(path.path_id)
        
        self._ensure_stats(user_id)
        return path
    
    def get_user_paths(self, user_id: str) -> List[LearningPath]:
        """获取用户的学习路径"""
        if user_id not in self.user_paths:
            return []
        return [self.learning_paths[pid] for pid in self.user_paths[user_id] 
                if pid in self.learning_paths]
    
    def create_reading_group(self, creator_id: str, creator_name: str,
                            book_title: str, description: str,
                            max_members: int = 20) -> ReadingGroup:
        """创建共读小组"""
        group = ReadingGroup(creator_id, creator_name, book_title, description, max_members)
        self.reading_groups[group.group_id] = group
        
        if creator_id not in self.user_groups:
            self.user_groups[creator_id] = []
        self.user_groups[creator_id].append(group.group_id)
        
        return group
    
    def join_reading_group(self, group_id: str, user_id: str, user_name: str) -> bool:
        """加入共读小组"""
        if group_id not in self.reading_groups:
            return False
        group = self.reading_groups[group_id]
        success = group.add_member(user_id, user_name)
        
        if success:
            if user_id not in self.user_groups:
                self.user_groups[user_id] = []
            if group_id not in self.user_groups[user_id]:
                self.user_groups[user_id].append(group_id)
        
        return success
    
    def get_all_groups(self) -> List[ReadingGroup]:
        """获取所有共读小组"""
        return list(self.reading_groups.values())
    
    def get_user_groups(self, user_id: str) -> List[ReadingGroup]:
        """获取用户加入的小组"""
        if user_id not in self.user_groups:
            return []
        return [self.reading_groups[gid] for gid in self.user_groups[user_id] 
                if gid in self.reading_groups]
    
    def start_pomodoro(self, user_id: str, work_minutes: int = 25, 
                       break_minutes: int = 5) -> PomodoroSession:
        """开始番茄钟"""
        session = PomodoroSession(user_id, work_minutes, break_minutes)
        self.pomodoro_sessions[session.session_id] = session
        return session
    
    def _ensure_stats(self, user_id: str):
        """确保用户统计存在"""
        if user_id not in self.user_stats:
            self.user_stats[user_id] = LearningStats(user_id)
    
    def get_stats(self, user_id: str) -> LearningStats:
        """获取用户统计"""
        self._ensure_stats(user_id)
        return self.user_stats[user_id]
    
    def add_study_record(self, user_id: str, date: str, duration_minutes: int,
                        subject: str, content: str, book_title: str = "") -> StudyRecord:
        """添加学习记录"""
        self._ensure_stats(user_id)
        record = StudyRecord(user_id, date, duration_minutes, subject, content, book_title)
        self.user_stats[user_id].add_record(record)
        return record


def generate_kaoyan_math_path(user_id: str) -> LearningPath:
    """生成考研数学学习路径"""
    tasks = [
        {"day": 1, "title": "高等数学基础-函数与极限", "description": "复习函数概念、极限定义与性质", 
         "resources": ["高等数学上册 第一章", "考研数学基础班视频"]},
        {"day": 2, "title": "导数与微分", "description": "导数定义、求导法则、微分中值定理", 
         "resources": ["高等数学上册 第二章", "考研数学真题集"]},
        {"day": 3, "title": "不定积分与定积分", "description": "积分公式、换元法、分部积分法", 
         "resources": ["高等数学上册 第四章", "积分练习200题"]},
        {"day": 4, "title": "微分方程", "description": "一阶微分方程、二阶常系数微分方程", 
         "resources": ["高等数学下册 第七章", "微分方程专项训练"]},
        {"day": 5, "title": "向量代数与空间几何", "description": "向量运算、平面方程、空间直线", 
         "resources": ["高等数学下册 第八章"]},
        {"day": 6, "title": "多元函数微分学", "description": "偏导数、全微分、多元函数极值", 
         "resources": ["高等数学下册 第九章"]},
        {"day": 7, "title": "重积分", "description": "二重积分、三重积分的计算与应用", 
         "resources": ["高等数学下册 第十章", "重积分专项练习"]},
        {"day": 8, "title": "线代基础-行列式与矩阵", "description": "行列式计算、矩阵运算、逆矩阵", 
         "resources": ["线性代数 第一、二章"]},
        {"day": 9, "title": "向量组与线性方程组", "description": "线性相关、秩、方程组解的结构", 
         "resources": ["线性代数 第三、四章"]},
        {"day": 10, "title": "特征值与二次型", "description": "特征值特征向量、相似对角化、二次型", 
         "resources": ["线性代数 第五、六章"]},
        {"day": 11, "title": "概率论基础", "description": "随机事件、概率公式、随机变量", 
         "resources": ["概率论与数理统计 第一、二章"]},
        {"day": 12, "title": "数字特征与大数定律", "description": "期望、方差、协方差、中心极限定理", 
         "resources": ["概率论与数理统计 第四、五章"]},
        {"day": 13, "title": "真题模拟一", "description": "完整做一套真题，查漏补缺", 
         "resources": ["近十年真题集"]},
        {"day": 14, "title": "真题模拟二", "description": "第二套真题，重点突破薄弱环节", 
         "resources": ["近十年真题集", "错题本"]},
    ]
    
    manager = LearningManager()
    return manager.create_learning_path(
        user_id=user_id,
        path_type="考研数学",
        title="考研数学14天冲刺计划",
        description="系统复习高等数学、线性代数、概率论，配合真题训练",
        tasks_data=tasks
    )


def generate_ielts_prep_path(user_id: str) -> LearningPath:
    """生成雅思备考学习路径"""
    tasks = [
        {"day": 1, "title": "雅思听力基础", "description": "听力题型介绍、场景词汇积累", 
         "resources": ["雅思听力真题 剑15", "听力高频词汇"]},
        {"day": 2, "title": "雅思阅读-填空题技巧", "description": "填空题定位技巧、同义词替换", 
         "resources": ["雅思阅读真题", "阅读核心词汇"]},
        {"day": 3, "title": "雅思写作-Task1图表", "description": "柱状图、折线图、表格写作方法", 
         "resources": ["雅思写作范文", "写作高分句型"]},
        {"day": 4, "title": "雅思口语-Part1", "description": "Part1常见话题与答题思路", 
         "resources": ["口语题库", "口语素材积累"]},
        {"day": 5, "title": "雅思听力-选择题技巧", "description": "选择题干扰项排除、预读技巧", 
         "resources": ["雅思听力真题 剑16"]},
        {"day": 6, "title": "雅思阅读-判断题", "description": "True/False/Not Given判断方法", 
         "resources": ["雅思阅读真题"]},
        {"day": 7, "title": "雅思写作-Task2大作文", "description": "议论文结构、论点展开", 
         "resources": ["雅思写作范文", "话题词汇"]},
        {"day": 8, "title": "雅思口语-Part2", "description": "话题卡描述、一分钟笔记法", 
         "resources": ["口语题库", "万能素材"]},
        {"day": 9, "title": "完整模考一", "description": "听说读写完整模考", 
         "resources": ["剑桥雅思真题 剑17"]},
        {"day": 10, "title": "错题回顾与总结", "description": "分析错题，查漏补缺", 
         "resources": ["错题本"]},
    ]
    
    manager = LearningManager()
    return manager.create_learning_path(
        user_id=user_id,
        path_type="雅思备考",
        title="雅思10天冲刺计划",
        description="系统提升听说读写四项能力，冲刺目标分数",
        tasks_data=tasks
    )


def create_sample_groups() -> List[ReadingGroup]:
    """创建示例共读小组"""
    manager = LearningManager()
    
    groups_data = [
        {
            "book_title": "《百年孤独》",
            "description": "一起读马尔克斯的魔幻现实主义经典，探讨孤独与命运",
            "creator_id": "U0001",
            "creator_name": "Ahmed",
            "members": [("U0000", "李明"), ("U0003", "张小华")]
        },
        {
            "book_title": "《数据结构与算法分析》",
            "description": "计算机专业必读书目，每周一章，互相督促学习",
            "creator_id": "U0000",
            "creator_name": "李明",
            "members": [("U0001", "Ahmed")]
        },
        {
            "book_title": "《被讨厌的勇气》",
            "description": "心理学入门读物，一起探索阿德勒心理学",
            "creator_id": "U0004",
            "creator_name": "匿名",
            "members": [("U0003", "张小华")]
        },
    ]
    
    groups = []
    for gdata in groups_data:
        group = manager.create_reading_group(
            gdata["creator_id"],
            gdata["creator_name"],
            gdata["book_title"],
            gdata["description"]
        )
        for uid, uname in gdata["members"]:
            manager.join_reading_group(group.group_id, uid, uname)
        groups.append(group)
    
    return groups