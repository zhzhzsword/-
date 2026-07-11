"""
空间管理模块
实现动态调度 + 固定分配混合模式的空间管理策略
"""

from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime, timedelta
import random

from models.user import User, UserType


class SeatType(Enum):
    """座位类型枚举"""
    FIXED = "fixed"  # 固定座位（20%）
    PRIORITY = "priority"  # 优先座位（30%）
    DYNAMIC = "dynamic"  # 动态座位（50%）


class SeatStatus(Enum):
    """座位状态枚举"""
    AVAILABLE = "available"  # 可用
    OCCUPIED = "occupied"  # 已占用
    TEMPORARY_RELEASED = "temporary_released"  # 临时释放
    RESERVED = "reserved"  # 已预约


class Seat:
    """座位"""
    
    def __init__(
        self,
        seat_id: str,
        seat_type: SeatType,
        location: str,
        features: List[str],
        quiet_level: int,  # 安静度（1-5）
        privacy_level: int,  # 私密性（1-5）
        has_window: bool,  # 是否靠窗
        is_corner: bool,  # 是否角落
        has_socket: bool  # 是否有插座
    ):
        self.seat_id = seat_id
        self.seat_type = seat_type
        self.location = location
        self.features = features
        self.quiet_level = quiet_level
        self.privacy_level = privacy_level
        self.has_window = has_window
        self.is_corner = is_corner
        self.has_socket = has_socket
        
        # 座位状态
        self.status = SeatStatus.AVAILABLE
        self.current_user_id: Optional[str] = None
        self.usage_start_time: Optional[datetime] = None
        
        # 固定座位特有属性
        self.fixed_user_id: Optional[str] = None  # 固定分配用户ID
        self.fixed_user_type: Optional[UserType] = None  # 固定用户类型
        
        # 临时释放属性
        self.temporary_release_end_time: Optional[datetime] = None
        self.temporary_release_user_id: Optional[str] = None
        
        # 使用率统计
        self.weekly_usage_ratio: float = 0.0  # 每周使用率
    
    def is_available_for_user(self, user: User) -> bool:
        """检查座位是否对用户可用"""
        if self.status == SeatStatus.AVAILABLE:
            return True
        
        if self.status == SeatStatus.TEMPORARY_RELEASED:
            # 临时释放座位可以被其他用户临时使用
            return True
        
        if self.status == SeatStatus.OCCUPIED:
            # 如果是固定用户，检查是否是自己
            if self.seat_type == SeatType.FIXED and self.fixed_user_id == user.user_id:
                return True
        
        return False
    
    def match_user_preference(self, user: User) -> float:
        """计算座位与用户偏好的匹配度"""
        score = 0.0
        
        if user.user_type == UserType.ANXIOUS_STUDENT:
            # 焦虑学生偏好安静角落
            if self.is_corner:
                score += 0.3
            if self.quiet_level >= 4:
                score += 0.2
            if self.privacy_level >= 4:
                score += 0.2
        
        elif user.user_type == UserType.INTERNATIONAL_STUDENT:
            # 留学生偏好人流少区域
            if "外文阅览室附近" in self.location:
                score += 0.3
            if self.quiet_level >= 3:
                score += 0.2
        
        elif user.user_type == UserType.FRESHMAN:
            # 新生偏好视野开阔座位
            if "服务台附近" in self.location:
                score += 0.3
            if self.has_window:
                score += 0.2
        
        elif user.user_type == UserType.GRADUATE_STUDENT:
            # 考研学生偏好固定座位和插座
            if self.seat_type == SeatType.FIXED:
                score += 0.4
            if self.has_socket:
                score += 0.3
        
        elif user.user_type == UserType.TEACHER:
            # 教师偏好安静独立空间
            if self.seat_type == SeatType.FIXED:
                score += 0.3
            if self.privacy_level >= 4:
                score += 0.2
        
        else:
            # 普通用户偏好通用特征
            if self.has_socket:
                score += 0.2
            if self.quiet_level >= 3:
                score += 0.2
        
        return min(score, 1.0)


class FixedAllocator:
    """固定座位分配器"""
    
    def __init__(self):
        self.fixed_seats: Dict[str, Seat] = {}  # 固定座位字典
        self.user_fixed_seats: Dict[str, str] = {}  # 用户固定座位映射
    
    def allocate(self, user: User) -> Optional[Seat]:
        """为用户分配固定座位"""
        # 检查用户是否已有固定座位
        if user.user_id in self.user_fixed_seats:
            seat_id = self.user_fixed_seats[user.user_id]
            return self.fixed_seats.get(seat_id)
        
        # 检查是否有可用固定座位
        available_seats = [
            seat for seat in self.fixed_seats.values()
            if seat.status == SeatStatus.AVAILABLE
        ]
        
        if not available_seats:
            return None
        
        # 计算座位匹配度
        best_seat = None
        best_score = 0.0
        
        for seat in available_seats:
            score = seat.match_user_preference(user)
            if score > best_score:
                best_score = score
                best_seat = seat
        
        if best_seat:
            # 分配座位
            best_seat.fixed_user_id = user.user_id
            best_seat.fixed_user_type = user.user_type
            best_seat.status = SeatStatus.RESERVED
            self.user_fixed_seats[user.user_id] = best_seat.seat_id
            
            return best_seat
        
        return None
    
    def temporary_release(self, user_id: str, seat_id: str, duration: int) -> bool:
        """座位临时释放"""
        # 检查释放时长
        if duration > 30:
            return False
        
        seat = self.fixed_seats.get(seat_id)
        if not seat or seat.fixed_user_id != user_id:
            return False
        
        # 标记座位为临时释放状态
        seat.status = SeatStatus.TEMPORARY_RELEASED
        seat.temporary_release_user_id = user_id
        seat.temporary_release_end_time = datetime.now() + timedelta(minutes=duration)
        
        return True
    
    def auto_reclaim(self, seat_id: str, user_id: str) -> bool:
        """自动收回座位"""
        seat = self.fixed_seats.get(seat_id)
        if not seat or seat.temporary_release_user_id != user_id:
            return False
        
        # 恢复座位状态
        seat.status = SeatStatus.RESERVED
        seat.temporary_release_user_id = None
        seat.temporary_release_end_time = None
        
        return True
    
    def revoke_fixed_seat(self, user_id: str, seat_id: str) -> bool:
        """收回固定座位"""
        seat = self.fixed_seats.get(seat_id)
        if not seat or seat.fixed_user_id != user_id:
            return False
        
        # 收回座位
        seat.fixed_user_id = None
        seat.fixed_user_type = None
        seat.status = SeatStatus.AVAILABLE
        if user_id in self.user_fixed_seats:
            del self.user_fixed_seats[user_id]
        
        return True


class PriorityAllocator:
    """优先座位分配器"""
    
    def __init__(self):
        self.priority_seats: Dict[str, Seat] = {}  # 优先座位字典
    
    def allocate(self, user: User, user_type: UserType) -> Optional[Seat]:
        """为用户分配优先座位"""
        # 检查是否有可用优先座位
        available_seats = [
            seat for seat in self.priority_seats.values()
            if seat.status == SeatStatus.AVAILABLE
        ]
        
        if not available_seats:
            return None
        
        # 根据用户类型筛选优先座位
        if user_type == UserType.ANXIOUS_STUDENT:
            # 焦虑学生：安静角落
            priority_seats = [
                seat for seat in available_seats
                if seat.is_corner and seat.quiet_level >= 4
            ]
        elif user_type == UserType.INTERNATIONAL_STUDENT:
            # 留学生：外文阅览室附近
            priority_seats = [
                seat for seat in available_seats
                if "外文阅览室附近" in seat.location
            ]
        elif user_type == UserType.FRESHMAN:
            # 新生：服务台附近
            priority_seats = [
                seat for seat in available_seats
                if "服务台附近" in seat.location
            ]
        else:
            priority_seats = available_seats
        
        if not priority_seats:
            # 无优先座位，返回普通座位
            priority_seats = available_seats
        
        # 计算座位匹配度
        best_seat = None
        best_score = 0.0
        
        for seat in priority_seats:
            score = seat.match_user_preference(user)
            if score > best_score:
                best_score = score
                best_seat = seat
        
        return best_seat


class DynamicScheduler:
    """动态座位调度器"""
    
    def __init__(self):
        self.dynamic_seats: Dict[str, Seat] = {}  # 动态座位字典
    
    def schedule(self, user: User, context: Dict) -> Optional[Seat]:
        """动态座位调度"""
        # 检查是否有可用动态座位
        available_seats = [
            seat for seat in self.dynamic_seats.values()
            if seat.status == SeatStatus.AVAILABLE or seat.status == SeatStatus.TEMPORARY_RELEASED
        ]
        
        if not available_seats:
            return None
        
        # 情境感知调度
        situation = context.get("situation", "normal")
        
        if situation == "exam_week":
            # 考试周：优先推荐安静座位
            priority_seats = [
                seat for seat in available_seats
                if seat.quiet_level >= 4
            ]
        else:
            # 正常时期：根据用户历史偏好
            priority_seats = available_seats
        
        if not priority_seats:
            priority_seats = available_seats
        
        # 计算座位匹配度
        best_seat = None
        best_score = 0.0
        
        for seat in priority_seats:
            score = seat.match_user_preference(user)
            if score > best_score:
                best_score = score
                best_seat = seat
        
        return best_seat


class SpaceManager:
    """空间管理器"""
    
    def __init__(self):
        self.fixed_allocator = FixedAllocator()
        self.priority_allocator = PriorityAllocator()
        self.dynamic_scheduler = DynamicScheduler()
        
        self.all_seats: Dict[str, Seat] = {}  # 所有座位字典
        self.seat_counter = 0  # 座位计数器
    
    def initialize_seats(self, total_seats: int = 200):
        """初始化座位"""
        # 固定座位区域（20%）
        fixed_count = int(total_seats * 0.2)
        for i in range(fixed_count):
            seat = self._create_seat(
                SeatType.FIXED,
                f"固定区域A{i+1:02d}",
                features=["固定座位", "长期使用"],
                quiet_level=random.randint(3, 5),
                privacy_level=random.randint(3, 5)
            )
            self.fixed_allocator.fixed_seats[seat.seat_id] = seat
            self.all_seats[seat.seat_id] = seat
        
        # 优先座位区域（30%）
        priority_count = int(total_seats * 0.3)
        for i in range(priority_count):
            seat = self._create_seat(
                SeatType.PRIORITY,
                f"优先区域B{i+1:02d}",
                features=["优先座位", "靠窗角落"],
                quiet_level=random.randint(4, 5),
                privacy_level=random.randint(4, 5),
                has_window=random.choice([True, False]),
                is_corner=random.choice([True, False])
            )
            self.priority_allocator.priority_seats[seat.seat_id] = seat
            self.all_seats[seat.seat_id] = seat
        
        # 动态座位区域（50%）
        dynamic_count = int(total_seats * 0.5)
        for i in range(dynamic_count):
            seat = self._create_seat(
                SeatType.DYNAMIC,
                f"动态区域C{i+1:02d}",
                features=["动态座位", "实时调度"],
                quiet_level=random.randint(2, 4),
                privacy_level=random.randint(2, 4)
            )
            self.dynamic_scheduler.dynamic_seats[seat.seat_id] = seat
            self.all_seats[seat.seat_id] = seat
    
    def _create_seat(
        self,
        seat_type: SeatType,
        location: str,
        features: List[str],
        quiet_level: int,
        privacy_level: int,
        has_window: bool = False,
        is_corner: bool = False
    ) -> Seat:
        """创建座位"""
        seat_id = f"S{self.seat_counter:04d}"
        self.seat_counter += 1
        
        seat = Seat(
            seat_id=seat_id,
            seat_type=seat_type,
            location=location,
            features=features,
            quiet_level=quiet_level,
            privacy_level=privacy_level,
            has_window=has_window,
            is_corner=is_corner,
            has_socket=random.choice([True, False])
        )
        
        return seat
    
    def allocate_seat(self, user: User, context: Dict) -> Optional[Seat]:
        """为用户分配座位"""
        # 根据用户类型选择分配策略
        if user.user_type == UserType.GRADUATE_STUDENT:
            # 考研学生：固定座位分配
            result = self.fixed_allocator.allocate(user)
        
        elif user.user_type in [UserType.ANXIOUS_STUDENT, UserType.INTERNATIONAL_STUDENT, UserType.FRESHMAN]:
            # 特殊需求用户：优先座位分配
            result = self.priority_allocator.allocate(user, user.user_type)
        
        else:
            # 普通用户：动态座位调度
            result = self.dynamic_scheduler.schedule(user, context)
        
        if result:
            # 更新座位状态
            result.status = SeatStatus.OCCUPIED
            result.current_user_id = user.user_id
            result.usage_start_time = datetime.now()
        
        return result
    
    def release_seat(self, user_id: str) -> bool:
        """用户释放座位"""
        # 查找用户当前使用的座位
        seat = None
        for s in self.all_seats.values():
            if s.current_user_id == user_id:
                seat = s
                break
        
        if not seat:
            return False
        
        # 检查是否是固定座位
        if seat.seat_type == SeatType.FIXED and seat.fixed_user_id == user_id:
            # 固定座位不释放，仅标记为预留
            seat.status = SeatStatus.RESERVED
        else:
            # 其他座位直接释放
            seat.status = SeatStatus.AVAILABLE
        
        seat.current_user_id = None
        seat.usage_start_time = None
        
        return True
    
    def get_available_seats(self, user: User) -> List[Seat]:
        """获取用户可用的座位列表"""
        available = []
        
        for seat in self.all_seats.values():
            if seat.is_available_for_user(user):
                available.append(seat)
        
        return available
    
    def get_seat_recommendations(self, user: User, context: Dict) -> List[Seat]:
        """获取座位推荐"""
        available = self.get_available_seats(user)
        
        # 计算匹配度并排序
        recommendations = []
        for seat in available:
            score = seat.match_user_preference(user)
            recommendations.append((seat, score))
        
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return [seat for seat, score in recommendations[:10]]


# 创建示例空间管理器
def create_sample_space_manager() -> SpaceManager:
    """创建示例空间管理器"""
    manager = SpaceManager()
    manager.initialize_seats(total_seats=200)
    
    print(f"初始化座位数：{len(manager.all_seats)}")
    print(f"固定座位数：{len(manager.fixed_allocator.fixed_seats)}")
    print(f"优先座位数：{len(manager.priority_allocator.priority_seats)}")
    print(f"动态座位数：{len(manager.dynamic_scheduler.dynamic_seats)}")
    
    return manager


if __name__ == "__main__":
    # 测试空间管理
    from models.user import create_sample_users, UserType
    
    # 创建示例用户和空间管理器
    user_manager = create_sample_users()
    space_manager = create_sample_space_manager()
    
    # 测试考研学生固定座位分配
    grad_users = user_manager.get_users_by_type(UserType.GRADUATE_STUDENT)
    if grad_users:
        grad_user = grad_users[0]
        seat = space_manager.allocate_seat(grad_user, {"situation": "normal"})
        
        if seat:
            print(f"考研学生分配座位：{seat.seat_id}, 类型：{seat.seat_type.value}, 位置：{seat.location}")
            print(f"座位特征：安静度={seat.quiet_level}, 私密性={seat.privacy_level}, 有插座={seat.has_socket}")
    
    # 测试焦虑学生优先座位分配
    anxious_users = user_manager.get_users_by_type(UserType.ANXIOUS_STUDENT)
    if anxious_users:
        anxious_user = anxious_users[0]
        seat = space_manager.allocate_seat(anxious_user, {"situation": "normal"})
        
        if seat:
            print(f"焦虑学生分配座位：{seat.seat_id}, 类型：{seat.seat_type.value}, 位置：{seat.location}")
            print(f"座位特征：安静度={seat.quiet_level}, 私密性={seat.privacy_level}, 是否角落={seat.is_corner}")
    
    # 测试留学生优先座位分配
    intl_users = user_manager.get_users_by_type(UserType.INTERNATIONAL_STUDENT)
    if intl_users:
        intl_user = intl_users[0]
        seat = space_manager.allocate_seat(intl_user, {"situation": "normal"})
        
        if seat:
            print(f"留学生分配座位：{seat.seat_id}, 类型：{seat.seat_type.value}, 位置：{seat.location}")