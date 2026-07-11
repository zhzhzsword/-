"""
图书馆智能服务系统 - 交互式演示入口
展示用户管理、推荐系统、空间管理三大核心模块
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.user import UserType, LanguageLevel, EmotionState, create_sample_users, UserManager
from algorithms.recommendation import HybridRecommender, create_sample_items
from core.space_management import SpaceManager, SeatType, create_sample_space_manager
from core.chat_agent import chat_interface


def print_separator(title):
    """打印分隔符"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_menu():
    """打印主菜单"""
    print("\n" + "="*60)
    print(" 🚀 图书馆智能服务系统 - 主菜单")
    print("="*60)
    print("  1. 用户管理系统")
    print("  2. 情境感知推荐系统")
    print("  3. 三层空间管理系统")
    print("  4. 伦理保障机制")
    print("  5. 全部模块演示")
    print("  6. 🤖 对话式智能助手")
    print("  0. 退出系统")
    print("="*60)


def sub_menu_user():
    """用户管理子菜单"""
    print("\n" + "-"*40)
    print(" 用户管理系统")
    print("-"*40)
    print("  1. 查看所有用户")
    print("  2. 按类型筛选用户")
    print("  3. 返回主菜单")
    print("-"*40)


def sub_menu_recommend():
    """推荐系统子菜单"""
    print("\n" + "-"*40)
    print(" 情境感知推荐系统")
    print("-"*40)
    print("  1. 考研学生推荐（考试周）")
    print("  2. 留学生推荐（正常时期）")
    print("  3. 焦虑学生推荐（考试周）")
    print("  4. 教师推荐")
    print("  5. 新生推荐")
    print("  6. 返回主菜单")
    print("-"*40)


def sub_menu_space():
    """空间管理子菜单"""
    print("\n" + "-"*40)
    print(" 三层空间管理系统")
    print("-"*40)
    print("  1. 查看座位分布")
    print("  2. 考研学生分配座位")
    print("  3. 留学生分配座位")
    print("  4. 焦虑学生分配座位")
    print("  5. 新生分配座位")
    print("  6. 返回主菜单")
    print("-"*40)


def demo_user_management(user_manager):
    """演示用户管理模块"""
    while True:
        sub_menu_user()
        choice = input("请选择操作（1-3）：")
        
        if choice == "1":
            print_separator("查看所有用户")
            user_types_display = {
                UserType.GRADUATE_STUDENT: "考研学生",
                UserType.INTERNATIONAL_STUDENT: "留学生",
                UserType.TEACHER: "教师",
                UserType.FRESHMAN: "新生",
                UserType.ANXIOUS_STUDENT: "焦虑学生"
            }
            
            print(f"\n系统已创建 {len(user_manager.users)} 名示例用户：")
            for user_id, user in user_manager.users.items():
                type_name = user_types_display.get(user.user_type, "普通用户")
                print(f"\n  🧑‍🎓 {user.name} ({user_id})")
                print(f"     ├─ 用户类型：{type_name}")
                print(f"     ├─ 所属院系：{user.department}")
                print(f"     ├─ 用户标签：{', '.join(user.tags)}")
                print(f"     └─ 用户偏好：{user.preferences}")
        
        elif choice == "2":
            print("\n用户类型列表：")
            print("  1 - 考研学生")
            print("  2 - 留学生")
            print("  3 - 教师")
            print("  4 - 新生")
            print("  5 - 焦虑学生")
            
            type_choice = input("请选择用户类型（1-5）：")
            type_map = {
                "1": UserType.GRADUATE_STUDENT,
                "2": UserType.INTERNATIONAL_STUDENT,
                "3": UserType.TEACHER,
                "4": UserType.FRESHMAN,
                "5": UserType.ANXIOUS_STUDENT
            }
            
            if type_choice in type_map:
                users = user_manager.get_users_by_type(type_map[type_choice])
                print(f"\n找到 {len(users)} 名用户：")
                for user in users:
                    print(f"\n  🧑‍🎓 {user.name} ({user.user_id})")
                    print(f"     ├─ 所属院系：{user.department}")
                    print(f"     └─ 用户标签：{', '.join(user.tags)}")
            else:
                print("❌ 无效选项")
        
        elif choice == "3":
            break
        
        else:
            print("❌ 无效选项，请重新输入")


def demo_recommendation_system(user_manager, all_items, recommender):
    """演示推荐系统模块"""
    user_types_display = {
        UserType.GRADUATE_STUDENT: "考研学生",
        UserType.INTERNATIONAL_STUDENT: "留学生",
        UserType.TEACHER: "教师",
        UserType.FRESHMAN: "新生",
        UserType.ANXIOUS_STUDENT: "焦虑学生"
    }
    
    scenarios = {
        UserType.GRADUATE_STUDENT: {"exam_week": True, "情境": "考试周"},
        UserType.INTERNATIONAL_STUDENT: {"normal": True, "情境": "正常时期"},
        UserType.TEACHER: {"normal": True, "情境": "正常时期"},
        UserType.FRESHMAN: {"beginning_semester": True, "情境": "开学初"},
        UserType.ANXIOUS_STUDENT: {"exam_week": True, "情境": "考试周"}
    }
    
    while True:
        sub_menu_recommend()
        choice = input("请选择操作（1-6）：")
        
        choice_map = {
            "1": UserType.GRADUATE_STUDENT,
            "2": UserType.INTERNATIONAL_STUDENT,
            "3": UserType.ANXIOUS_STUDENT,
            "4": UserType.TEACHER,
            "5": UserType.FRESHMAN
        }
        
        if choice in choice_map:
            user_type = choice_map[choice]
            users = user_manager.get_users_by_type(user_type)
            
            if users:
                user = users[0]
                context = dict(scenarios[user_type])
                situation = context.pop("情境")
                
                recommendations = recommender.recommend(user, context, all_items)
                
                print_separator(f"{user_types_display[user_type]}「{user.name}」推荐结果")
                print(f"\n📚 当前情境：{situation}")
                
                if recommendations:
                    for i, item in enumerate(recommendations[:5], 1):
                        print(f"\n     {i}. {item.title}")
                        print(f"        ├─ 类型：{item.item_type.value}")
                        print(f"        ├─ 相关性：{item.relevance_score:.2f}")
                        print(f"        ├─ 热门度：{item.popularity:.2f}")
                        print(f"        ├─ 小众度：{item.niche_score:.2f}")
                        print(f"        ├─ 语言：{item.language}")
                        print(f"        └─ 标签：{', '.join(item.tags)}")
                else:
                    print("     暂无推荐结果")
        
        elif choice == "6":
            break
        
        else:
            print("❌ 无效选项，请重新输入")


def demo_space_management(user_manager, space_manager):
    """演示空间管理模块"""
    user_types_display = {
        UserType.GRADUATE_STUDENT: "考研学生",
        UserType.INTERNATIONAL_STUDENT: "留学生",
        UserType.ANXIOUS_STUDENT: "焦虑学生",
        UserType.FRESHMAN: "新生"
    }
    
    seat_types_display = {
        SeatType.FIXED: "固定座位",
        SeatType.PRIORITY: "优先座位",
        SeatType.DYNAMIC: "动态座位"
    }
    
    while True:
        sub_menu_space()
        choice = input("请选择操作（1-6）：")
        
        if choice == "1":
            print_separator("座位分布统计")
            print(f"\n总座位数：{len(space_manager.all_seats)}")
            print(f"  ├─ 固定座位：{len(space_manager.fixed_allocator.fixed_seats)} (20%)")
            print(f"  ├─ 优先座位：{len(space_manager.priority_allocator.priority_seats)} (30%)")
            print(f"  └─ 动态座位：{len(space_manager.dynamic_scheduler.dynamic_seats)} (50%)")
            
            occupied_count = sum(1 for s in space_manager.all_seats.values() if s.status.name == "OCCUPIED")
            available_count = sum(1 for s in space_manager.all_seats.values() if s.status.name == "AVAILABLE")
            print(f"\n当前状态：")
            print(f"  ├─ 已占用：{occupied_count}")
            print(f"  └─ 可用：{available_count}")
        
        elif choice == "2":
            users = user_manager.get_users_by_type(UserType.GRADUATE_STUDENT)
            if users:
                user = users[0]
                seat = space_manager.allocate_seat(user, {"situation": "normal"})
                print_separator(f"{user_types_display[user.user_type]}「{user.name}」座位分配")
                if seat:
                    print_seat_info(seat, seat_types_display)
        
        elif choice == "3":
            users = user_manager.get_users_by_type(UserType.INTERNATIONAL_STUDENT)
            if users:
                user = users[0]
                seat = space_manager.allocate_seat(user, {"situation": "normal"})
                print_separator(f"{user_types_display[user.user_type]}「{user.name}」座位分配")
                if seat:
                    print_seat_info(seat, seat_types_display)
        
        elif choice == "4":
            users = user_manager.get_users_by_type(UserType.ANXIOUS_STUDENT)
            if users:
                user = users[0]
                seat = space_manager.allocate_seat(user, {"situation": "normal"})
                print_separator(f"{user_types_display[user.user_type]}「{user.name}」座位分配")
                if seat:
                    print_seat_info(seat, seat_types_display)
        
        elif choice == "5":
            users = user_manager.get_users_by_type(UserType.FRESHMAN)
            if users:
                user = users[0]
                seat = space_manager.allocate_seat(user, {"situation": "normal"})
                print_separator(f"{user_types_display[user.user_type]}「{user.name}」座位分配")
                if seat:
                    print_seat_info(seat, seat_types_display)
        
        elif choice == "6":
            break
        
        else:
            print("❌ 无效选项，请重新输入")


def print_seat_info(seat, seat_types_display):
    """打印座位信息"""
    print(f"\n🪑 座位ID：{seat.seat_id}")
    print(f"     ├─ 座位类型：{seat_types_display[seat.seat_type]}")
    print(f"     ├─ 位置：{seat.location}")
    print(f"     ├─ 安静度：{'⭐' * seat.quiet_level}")
    print(f"     ├─ 私密性：{'🔒' * seat.privacy_level}")
    print(f"     ├─ 是否靠窗：{'✅' if seat.has_window else '❌'}")
    print(f"     ├─ 是否角落：{'✅' if seat.is_corner else '❌'}")
    print(f"     └─ 是否有插座：{'✅' if seat.has_socket else '❌'}")


def demo_ethical_features():
    """演示伦理保障机制"""
    print_separator("模块四：伦理保障机制验证")
    
    print("\n📊 公平性保障：")
    print("  ├─ 热门资源比例限制 ≤ 30%")
    print("  ├─ 冷门资源比例保证 ≥ 20%")
    print("  └─ 留学生英文文献推荐 ≥ 40%")
    
    print("\n🎯 多样性保障：")
    print("  ├─ 资源类型多样性（书籍/座位/活动/资源平台）")
    print("  ├─ 学科领域多样性（至少3个学科）")
    print("  └─ 跨学科推荐机制")
    
    print("\n❤️ 人文关怀：")
    print("  ├─ 考研学生固定座位分配")
    print("  ├─ 焦虑学生安静角落优先")
    print("  ├─ 留学生外文阅览室附近")
    print("  └─ 新生服务台附近引导")


def demo_all(user_manager, all_items, recommender, space_manager):
    """演示全部模块"""
    print_separator("模块一：用户管理系统")
    user_types_display = {
        UserType.GRADUATE_STUDENT: "考研学生",
        UserType.INTERNATIONAL_STUDENT: "留学生",
        UserType.TEACHER: "教师",
        UserType.FRESHMAN: "新生",
        UserType.ANXIOUS_STUDENT: "焦虑学生"
    }
    for user_id, user in user_manager.users.items():
        type_name = user_types_display.get(user.user_type, "普通用户")
        print(f"\n  🧑‍🎓 {user.name} ({user_id}) - {type_name}")
    
    print_separator("模块二：情境感知混合推荐系统")
    scenarios = {
        UserType.GRADUATE_STUDENT: {"exam_week": True},
        UserType.INTERNATIONAL_STUDENT: {"normal": True},
        UserType.ANXIOUS_STUDENT: {"exam_week": True}
    }
    for user_type, label in user_types_display.items():
        if user_type in scenarios:
            users = user_manager.get_users_by_type(user_type)
            if users:
                recommendations = recommender.recommend(users[0], scenarios[user_type], all_items)
                print(f"\n📚 {label}「{users[0].name}」推荐：")
                for item in recommendations[:3]:
                    print(f"     - {item.title}")
    
    print_separator("模块三：三层空间管理系统")
    print(f"座位分布：{len(space_manager.all_seats)}个（固定:{len(space_manager.fixed_allocator.fixed_seats)} 优先:{len(space_manager.priority_allocator.priority_seats)} 动态:{len(space_manager.dynamic_scheduler.dynamic_seats)}）")
    
    demo_ethical_features()
    print_separator("全部演示完成")


def main():
    """主函数"""
    print("🚀 图书馆智能服务系统启动")
    
    user_manager = create_sample_users()
    all_items = create_sample_items()
    recommender = HybridRecommender()
    space_manager = create_sample_space_manager()
    
    while True:
        print_menu()
        choice = input("\n请选择模块（0-6）：")
        
        if choice == "1":
            demo_user_management(user_manager)
        elif choice == "2":
            demo_recommendation_system(user_manager, all_items, recommender)
        elif choice == "3":
            demo_space_management(user_manager, space_manager)
        elif choice == "4":
            demo_ethical_features()
        elif choice == "5":
            demo_all(user_manager, all_items, recommender, space_manager)
        elif choice == "6":
            chat_interface()
        elif choice == "0":
            print("\n👋 感谢使用图书馆智能服务系统")
            break
        else:
            print("❌ 无效选项，请输入0-6")


if __name__ == "__main__":
    main()