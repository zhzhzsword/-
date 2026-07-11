"""
推荐算法模块
实现情境感知混合推荐策略，包含公平性和多样性保障机制
"""

from typing import List, Dict, Tuple
from enum import Enum
import random
import math

from models.user import User, UserType


class ResourceType(Enum):
    """资源类型枚举"""
    BOOK = "book"  # 书籍
    SEAT = "seat"  # 座位
    ACTIVITY = "activity"  # 活动
    RESOURCE_PLATFORM = "resource_platform"  # 资源平台


class Situation(Enum):
    """情境枚举"""
    NORMAL = "normal"  # 正常时期
    EXAM_WEEK = "exam_week"  # 考试周
    VACATION = "vacation"  # 假期
    BEGINNING_SEMESTER = "beginning_semester"  # 开学初


class RecommendationItem:
    """推荐项"""
    
    def __init__(
        self,
        item_id: str,
        item_type: ResourceType,
        title: str,
        description: str,
        relevance_score: float,
        popularity: float,  # 热门度（0-1）
        niche_score: float,  # 小众度（0-1）
        subjects: List[str],  # 学科领域
        language: str = "中文",  # 语言
        tags: List[str] = []
    ):
        self.item_id = item_id
        self.item_type = item_type
        self.title = title
        self.description = description
        self.relevance_score = relevance_score
        self.popularity = popularity
        self.niche_score = niche_score
        self.subjects = subjects
        self.language = language
        self.tags = tags


class CollaborativeFilter:
    """协同过滤推荐器"""
    
    def __init__(self):
        self.user_item_matrix: Dict[str, Dict[str, float]] = {}  # 用户-物品评分矩阵
    
    def recommend(self, user: User, all_items: List[RecommendationItem]) -> List[RecommendationItem]:
        """协同过滤推荐"""
        # 简化版协同过滤：基于用户标签匹配
        recommendations = []
        
        for item in all_items:
            # 计算标签匹配度
            tag_match_score = self._calculate_tag_match(user.tags, item.tags)
            
            # 计算相关性得分
            relevance_score = tag_match_score * 0.7 + item.popularity * 0.3
            
            if relevance_score > 0.3:  # 简单阈值
                recommendations.append(item)
        
        # 按相关性得分排序
        recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return recommendations[:10]  # 返回前10项
    
    def _calculate_tag_match(self, user_tags: List[str], item_tags: List[str]) -> float:
        """计算标签匹配度"""
        if not user_tags or not item_tags:
            return 0.0
        
        # 计算交集
        intersection = set(user_tags) & set(item_tags)
        
        # 计算匹配度
        match_score = len(intersection) / len(user_tags)
        
        return match_score


class ContentMatcher:
    """内容匹配推荐器"""
    
    def __init__(self):
        self.item_features: Dict[str, Dict] = {}  # 物品特征字典
    
    def recommend(self, user: User, all_items: List[RecommendationItem]) -> List[RecommendationItem]:
        """内容匹配推荐"""
        recommendations = []
        
        for item in all_items:
            # 计算内容匹配度
            content_match_score = self._calculate_content_match(user, item)
            
            if content_match_score > 0.2:  # 简单阈值
                # 创建推荐项副本并更新得分
                item_copy = RecommendationItem(
                    item_id=item.item_id,
                    item_type=item.item_type,
                    title=item.title,
                    description=item.description,
                    relevance_score=content_match_score,
                    popularity=item.popularity,
                    niche_score=item.niche_score,
                    subjects=item.subjects,
                    language=item.language,
                    tags=item.tags
                )
                recommendations.append(item_copy)
        
        # 按相关性得分排序
        recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return recommendations[:10]  # 返回前10项
    
    def _calculate_content_match(self, user: User, item: RecommendationItem) -> float:
        """计算内容匹配度"""
        score = 0.0
        
        # 学科匹配
        if hasattr(user, 'department'):
            if any(subject in user.department for subject in item.subjects):
                score += 0.3
        
        # 用户类型匹配
        if user.user_type == UserType.GRADUATE_STUDENT:
            # 考研学生偏好备考资料
            if hasattr(user, 'exam_subjects'):
                for subject in user.exam_subjects:
                    if subject in item.subjects:
                        score += 0.2
        
        elif user.user_type == UserType.INTERNATIONAL_STUDENT:
            # 留学生偏好英文文献
            if item.language == "英文" or item.language == "双语":
                score += 0.3
            # 专业匹配
            if hasattr(user, 'major_subjects'):
                for subject in user.major_subjects:
                    if subject in item.subjects:
                        score += 0.2
        
        elif user.user_type == UserType.TEACHER:
            # 教师偏好学术文献和新书
            if hasattr(user, 'research_areas'):
                for area in user.research_areas:
                    if area in item.subjects:
                        score += 0.3
        
        elif user.user_type == UserType.FRESHMAN:
            # 新生偏好基础入门资源
            if "基础" in item.tags or "入门" in item.tags:
                score += 0.3
        
        elif user.user_type == UserType.ANXIOUS_STUDENT:
            # 焦虑学生偏好心理支持和轻松资料
            if "心理支持" in item.tags or "轻松" in item.tags:
                score += 0.3
        
        return min(score, 1.0)  # 限制最大值为1.0


class ContextSensor:
    """情境感知推荐器"""
    
    def __init__(self):
        self.situation_weights = {
            UserType.GRADUATE_STUDENT: {
                Situation.NORMAL: {"content": 0.5, "collaborative": 0.3, "context": 0.2},
                Situation.EXAM_WEEK: {"content": 0.6, "collaborative": 0.2, "context": 0.2},
                Situation.VACATION: {"content": 0.4, "collaborative": 0.4, "context": 0.2}
            },
            UserType.INTERNATIONAL_STUDENT: {
                Situation.NORMAL: {"content": 0.6, "language_filter": 0.2, "context": 0.2},
                Situation.EXAM_WEEK: {"content": 0.7, "language_filter": 0.1, "context": 0.2},
                Situation.VACATION: {"content": 0.5, "language_filter": 0.3, "context": 0.2}
            },
            UserType.TEACHER: {
                Situation.NORMAL: {"content": 0.4, "new_book_tracking": 0.4, "collaborative": 0.2},
                Situation.EXAM_WEEK: {"content": 0.5, "new_book_tracking": 0.3, "collaborative": 0.2}
            },
            UserType.FRESHMAN: {
                Situation.BEGINNING_SEMESTER: {"content": 0.7, "popular": 0.2, "context": 0.1},
                Situation.NORMAL: {"content": 0.6, "collaborative": 0.3, "context": 0.1}
            },
            UserType.ANXIOUS_STUDENT: {
                Situation.NORMAL: {"context": 0.5, "content": 0.3, "collaborative": 0.2},
                Situation.EXAM_WEEK: {"context": 0.6, "content": 0.2, "collaborative": 0.2}
            }
        }
    
    def analyze_situation(self, context_data: Dict) -> Situation:
        """分析当前情境"""
        # 简化版情境分析
        if context_data.get("exam_week"):
            return Situation.EXAM_WEEK
        elif context_data.get("vacation"):
            return Situation.VACATION
        elif context_data.get("beginning_semester"):
            return Situation.BEGINNING_SEMESTER
        else:
            return Situation.NORMAL
    
    def recommend(
        self, 
        user: User, 
        situation: Situation, 
        all_items: List[RecommendationItem]
    ) -> List[RecommendationItem]:
        """情境感知推荐"""
        recommendations = []
        
        # 根据用户类型和情境调整推荐策略
        if user.user_type == UserType.ANXIOUS_STUDENT and situation == Situation.EXAM_WEEK:
            # 焦虑学生考试周：优先心理支持
            for item in all_items:
                if "心理支持" in item.tags:
                    item_copy = RecommendationItem(
                        item_id=item.item_id,
                        item_type=item.item_type,
                        title=item.title,
                        description=item.description,
                        relevance_score=0.9,  # 高相关性
                        popularity=item.popularity,
                        niche_score=item.niche_score,
                        subjects=item.subjects,
                        language=item.language,
                        tags=item.tags
                    )
                    recommendations.append(item_copy)
        
        elif user.user_type == UserType.TEACHER and situation == Situation.NORMAL:
            # 教师正常时期：新书追踪
            for item in all_items:
                if "新书" in item.tags:
                    item_copy = RecommendationItem(
                        item_id=item.item_id,
                        item_type=item.item_type,
                        title=item.title,
                        description=item.description,
                        relevance_score=0.8,
                        popularity=item.popularity,
                        niche_score=item.niche_score,
                        subjects=item.subjects,
                        language=item.language,
                        tags=item.tags
                    )
                    recommendations.append(item_copy)
        
        return recommendations[:5]  # 返回前5项


class HybridRecommender:
    """混合推荐系统"""
    
    def __init__(self):
        self.collaborative_filter = CollaborativeFilter()
        self.content_matcher = ContentMatcher()
        self.context_sensor = ContextSensor()
        self._all_items_cache = []
    
    def recommend(
        self, 
        user: User, 
        context: Dict, 
        all_items: List[RecommendationItem]
    ) -> List[RecommendationItem]:
        """混合推荐"""
        self._all_items_cache = all_items
        
        # 情境分析
        situation = self.context_sensor.analyze_situation(context)
        
        # 多策略并行计算
        cf_results = self.collaborative_filter.recommend(user, all_items)
        content_results = self.content_matcher.recommend(user, all_items)
        context_results = self.context_sensor.recommend(user, situation, all_items)
        
        # 结果融合
        hybrid_results = self._merge_results(
            cf_results, content_results, context_results, user, situation
        )
        
        # 公平性修正
        fair_results = self._ensure_fairness(hybrid_results, user)
        
        # 多样性保证
        diverse_results = self._ensure_diversity(fair_results)
        
        return diverse_results
    
    def _merge_results(
        self,
        cf_results: List[RecommendationItem],
        content_results: List[RecommendationItem],
        context_results: List[RecommendationItem],
        user: User,
        situation: Situation
    ) -> List[RecommendationItem]:
        """结果融合"""
        # 合并所有推荐项
        all_recommended = {}
        
        # 协同过滤结果（权重较低）
        for item in cf_results:
            if item.item_id not in all_recommended:
                all_recommended[item.item_id] = item
                item.relevance_score *= 0.3
        
        # 内容匹配结果（权重较高）
        for item in content_results:
            if item.item_id in all_recommended:
                all_recommended[item.item_id].relevance_score += item.relevance_score * 0.5
            else:
                item.relevance_score *= 0.5
                all_recommended[item.item_id] = item
        
        # 情境感知结果（权重最高）
        for item in context_results:
            if item.item_id in all_recommended:
                all_recommended[item.item_id].relevance_score += item.relevance_score * 0.2
            else:
                item.relevance_score *= 0.2
                all_recommended[item.item_id] = item
        
        # 按融合后的相关性得分排序
        recommendations = list(all_recommended.values())
        recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return recommendations[:20]  # 返回前20项
    
    def _ensure_fairness(
        self, 
        recommendations: List[RecommendationItem], 
        user: User
    ) -> List[RecommendationItem]:
        """公平性修正"""
        if not recommendations:
            return recommendations
        
        result = list(recommendations)
        seen_ids = {item.item_id for item in result}
        
        # 统计热门资源比例
        popular_items = [item for item in result if item.popularity > 0.7]
        popular_ratio = len(popular_items) / len(result)
        
        # 如果热门资源超过30%，替换为冷门资源
        if popular_ratio > 0.3:
            niche_items = [item for item in result if item.niche_score > 0.6]
            replace_count = int(len(result) * 0.1)
            for i in range(min(replace_count, len(niche_items), len(popular_items))):
                popular_idx = result.index(popular_items[i])
                niche_idx = result.index(niche_items[i])
                result[popular_idx], result[niche_idx] = result[niche_idx], result[popular_idx]
        
        # 用户类型特定公平性修正
        if user.user_type == UserType.INTERNATIONAL_STUDENT:
            english_items = [item for item in result if item.language == "英文"]
            english_ratio = len(english_items) / len(result)
            target_count = int(len(result) * 0.4)
            
            if len(english_items) < target_count:
                all_english = [
                    item for item in self._all_items_cache 
                    if item.language == "英文" and item.item_id not in seen_ids
                ]
                needed = target_count - len(english_items)
                for item in all_english[:needed]:
                    result.append(item)
                    seen_ids.add(item.item_id)
        
        elif user.user_type == UserType.ANXIOUS_STUDENT:
            mental_items = [item for item in result if "心理支持" in item.tags]
            target_count = max(1, int(len(result) * 0.2))
            
            if len(mental_items) < target_count:
                all_mental = [
                    item for item in self._all_items_cache 
                    if "心理支持" in item.tags and item.item_id not in seen_ids
                ]
                needed = target_count - len(mental_items)
                for item in all_mental[:needed]:
                    result.append(item)
                    seen_ids.add(item.item_id)
        
        # 确保冷门资源至少20%
        niche_items = [item for item in result if item.niche_score > 0.6]
        target_count = max(1, int(len(result) * 0.2))
        
        if len(niche_items) < target_count:
            all_niche = [
                item for item in self._all_items_cache 
                if item.niche_score > 0.6 and item.item_id not in seen_ids
            ]
            needed = target_count - len(niche_items)
            for item in all_niche[:needed]:
                result.append(item)
                seen_ids.add(item.item_id)
        
        return result
    
    def _ensure_diversity(self, recommendations: List[RecommendationItem]) -> List[RecommendationItem]:
        """多样性保证"""
        if not recommendations:
            return recommendations
        
        result = list(recommendations)
        seen_ids = {item.item_id for item in result}
        
        # 资源类型多样性
        type_counts = {}
        for item in result:
            type_counts[item.item_type] = type_counts.get(item.item_type, 0) + 1
        
        for resource_type in ResourceType:
            current_count = type_counts.get(resource_type, 0)
            target_count = max(1, int(len(result) * 0.1))
            
            if current_count < target_count:
                type_items = [
                    item for item in self._all_items_cache 
                    if item.item_type == resource_type and item.item_id not in seen_ids
                ]
                needed = target_count - current_count
                for item in type_items[:needed]:
                    result.append(item)
                    seen_ids.add(item.item_id)
                    type_counts[resource_type] = type_counts.get(resource_type, 0) + 1
        
        # 学科领域多样性
        unique_subjects = set()
        for item in result:
            unique_subjects.update(item.subjects)
        
        if len(unique_subjects) < 3:
            cross_subject_items = []
            for item in self._all_items_cache:
                if item.item_id in seen_ids:
                    continue
                has_new_subject = any(s not in unique_subjects for s in item.subjects)
                if has_new_subject:
                    cross_subject_items.append(item)
                    for s in item.subjects:
                        unique_subjects.add(s)
                    if len(unique_subjects) >= 3:
                        break
            
            for item in cross_subject_items[:2]:
                if item.item_id not in seen_ids:
                    result.append(item)
                    seen_ids.add(item.item_id)
        
        return result


# 创建示例资源数据
def create_sample_items() -> List[RecommendationItem]:
    """创建示例资源数据"""
    items = []
    
    items.append(RecommendationItem(
        item_id="B001",
        item_type=ResourceType.BOOK,
        title="考研数学真题解析",
        description="历年考研数学真题详细解析",
        relevance_score=0.9,
        popularity=0.85,
        niche_score=0.15,
        subjects=["数学"],
        tags=["考研", "数学", "真题"]
    ))
    
    items.append(RecommendationItem(
        item_id="B002",
        item_type=ResourceType.BOOK,
        title="Introduction to Algorithms",
        description="算法导论英文版",
        relevance_score=0.7,
        popularity=0.6,
        niche_score=0.4,
        subjects=["计算机科学", "人工智能"],
        language="英文",
        tags=["算法", "英文文献", "计算机"]
    ))
    
    items.append(RecommendationItem(
        item_id="B003",
        item_type=ResourceType.BOOK,
        title="考试焦虑应对指南",
        description="帮助学生应对考试焦虑的心理支持书籍",
        relevance_score=0.8,
        popularity=0.3,
        niche_score=0.7,
        subjects=["心理学"],
        tags=["心理支持", "考试焦虑", "心理健康"]
    ))
    
    items.append(RecommendationItem(
        item_id="B004",
        item_type=ResourceType.BOOK,
        title="学习科学新进展",
        description="学习科学领域最新研究成果",
        relevance_score=0.8,
        popularity=0.4,
        niche_score=0.6,
        subjects=["学习科学", "教育学"],
        tags=["新书", "学习科学", "教育"]
    ))
    
    items.append(RecommendationItem(
        item_id="B005",
        item_type=ResourceType.BOOK,
        title="计算机专业课考研指南",
        description="计算机专业考研专业课备考指南",
        relevance_score=0.6,
        popularity=0.2,
        niche_score=0.8,
        subjects=["计算机科学", "人工智能"],
        tags=["考研", "专业课", "小众"]
    ))
    
    items.append(RecommendationItem(
        item_id="B006",
        item_type=ResourceType.BOOK,
        title="Artificial Intelligence: A Modern Approach",
        description="人工智能经典教材英文版",
        relevance_score=0.85,
        popularity=0.7,
        niche_score=0.3,
        subjects=["人工智能", "计算机科学"],
        language="英文",
        tags=["人工智能", "英文文献", "经典教材"]
    ))
    
    items.append(RecommendationItem(
        item_id="B007",
        item_type=ResourceType.BOOK,
        title="Data Science for Beginners",
        description="数据科学入门英文版",
        relevance_score=0.75,
        popularity=0.5,
        niche_score=0.5,
        subjects=["数据科学", "人工智能"],
        language="英文",
        tags=["数据科学", "英文文献", "入门"]
    ))
    
    items.append(RecommendationItem(
        item_id="B008",
        item_type=ResourceType.BOOK,
        title="大学生心理健康读本",
        description="面向大学生的心理健康指导书籍",
        relevance_score=0.7,
        popularity=0.4,
        niche_score=0.6,
        subjects=["心理学"],
        tags=["心理支持", "心理健康", "大学生"]
    ))
    
    items.append(RecommendationItem(
        item_id="B009",
        item_type=ResourceType.BOOK,
        title="新闻学入门",
        description="新闻传播学专业基础入门教材",
        relevance_score=0.8,
        popularity=0.5,
        niche_score=0.5,
        subjects=["新闻传播学"],
        tags=["基础", "入门", "新闻学"]
    ))
    
    items.append(RecommendationItem(
        item_id="B010",
        item_type=ResourceType.BOOK,
        title="教育心理学研究前沿",
        description="教育心理学领域最新研究论文集",
        relevance_score=0.9,
        popularity=0.35,
        niche_score=0.65,
        subjects=["教育学", "心理学"],
        tags=["新书", "教育心理学", "学术"]
    ))
    
    items.append(RecommendationItem(
        item_id="B011",
        item_type=ResourceType.BOOK,
        title="考研英语词汇速记",
        description="考研英语核心词汇记忆法",
        relevance_score=0.85,
        popularity=0.75,
        niche_score=0.25,
        subjects=["英语"],
        tags=["考研", "英语", "词汇"]
    ))
    
    items.append(RecommendationItem(
        item_id="B012",
        item_type=ResourceType.BOOK,
        title="媒介素养导论",
        description="新媒体时代媒介素养入门",
        relevance_score=0.7,
        popularity=0.3,
        niche_score=0.7,
        subjects=["新闻传播学"],
        tags=["基础", "入门", "小众"]
    ))
    
    items.append(RecommendationItem(
        item_id="S001",
        item_type=ResourceType.SEAT,
        title="靠窗角落座位A15",
        description="安静靠窗角落座位，适合深度学习",
        relevance_score=0.8,
        popularity=0.7,
        niche_score=0.3,
        subjects=["座位"],
        tags=["靠窗", "角落", "安静"]
    ))
    
    items.append(RecommendationItem(
        item_id="A001",
        item_type=ResourceType.ACTIVITY,
        title="考研经验分享会",
        description="往届考研成功学长学姐经验分享",
        relevance_score=0.8,
        popularity=0.8,
        niche_score=0.2,
        subjects=["考研"],
        tags=["考研", "活动", "经验分享"]
    ))
    
    items.append(RecommendationItem(
        item_id="A002",
        item_type=ResourceType.ACTIVITY,
        title="留学生文化交流沙龙",
        description="中外学生文化交流活动",
        relevance_score=0.7,
        popularity=0.5,
        niche_score=0.5,
        subjects=["跨文化交流"],
        tags=["留学生", "活动", "文化交流"]
    ))
    
    items.append(RecommendationItem(
        item_id="R001",
        item_type=ResourceType.RESOURCE_PLATFORM,
        title="英文文献数据库导航",
        description="常用英文学术数据库使用指南",
        relevance_score=0.75,
        popularity=0.6,
        niche_score=0.4,
        subjects=["计算机科学", "人工智能"],
        language="英文",
        tags=["数据库", "英文文献", "资源平台"]
    ))
    
    return items


if __name__ == "__main__":
    # 测试推荐系统
    from models.user import create_sample_users, UserType
    
    # 创建示例用户和资源
    user_manager = create_sample_users()
    all_items = create_sample_items()
    
    # 创建推荐系统
    recommender = HybridRecommender()
    
    # 测试考研学生推荐
    grad_users = user_manager.get_users_by_type(UserType.GRADUATE_STUDENT)
    if grad_users:
        grad_user = grad_users[0]
        recommendations = recommender.recommend(
            grad_user, 
            {"exam_week": True}, 
            all_items
        )
        
        print(f"考研学生推荐结果：")
        for item in recommendations[:5]:
            print(f"  - {item.title} (相关性: {item.relevance_score:.2f}, 热门度: {item.popularity:.2f})")
    
    # 测试留学生推荐
    intl_users = user_manager.get_users_by_type(UserType.INTERNATIONAL_STUDENT)
    if intl_users:
        intl_user = intl_users[0]
        recommendations = recommender.recommend(
            intl_user, 
            {"normal": True}, 
            all_items
        )
        
        print(f"留学生推荐结果：")
        for item in recommendations[:5]:
            print(f"  - {item.title} (相关性: {item.relevance_score:.2f}, 语言: {item.language})")
    
    # 测试焦虑学生推荐
    anxious_users = user_manager.get_users_by_type(UserType.ANXIOUS_STUDENT)
    if anxious_users:
        anxious_user = anxious_users[0]
        recommendations = recommender.recommend(
            anxious_user, 
            {"exam_week": True}, 
            all_items
        )
        
        print(f"焦虑学生推荐结果：")
        for item in recommendations[:5]:
            print(f"  - {item.title} (相关性: {item.relevance_score:.2f}, 标签: {item.tags})")