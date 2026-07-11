"""
图书馆智能服务系统 - Web应用后端
基于Flask框架，提供聊天API和静态页面服务
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from flask import Flask, render_template, request, jsonify, session
from core.chat_agent import ChatAgent
from models.learning import (LearningManager, generate_kaoyan_math_path, 
                           generate_ielts_prep_path, create_sample_groups,
                           PathStatus, TaskStatus, ReadingGroupStatus, PomodoroStatus)
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'library-smart-system-secret-key-2024'

agents = {}
learning_manager = LearningManager()


def get_agent(session_id):
    """获取或创建会话对应的智能助手"""
    if session_id not in agents:
        agents[session_id] = ChatAgent()
    return agents[session_id]


def get_current_user():
    """获取当前用户"""
    session_id = session.get('session_id', 'guest')
    user_id = session.get('user_id', 'U0000')
    user_name = session.get('user_name', '李明')
    return user_id, user_name, session_id


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard_page():
    """学习仪表盘页面"""
    return render_template('dashboard.html')


@app.route('/learning-path')
def learning_path_page():
    """学习路径页面"""
    return render_template('learning_path.html')


@app.route('/reading-group')
def reading_group_page():
    """共读小组页面"""
    return render_template('reading_group.html')


@app.route('/pomodoro')
def pomodoro_page():
    """番茄钟页面"""
    return render_template('pomodoro.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """聊天API接口"""
    data = request.get_json()
    user_input = data.get('message', '').strip()
    
    if not user_input:
        return jsonify({'error': '消息不能为空'}), 400
    
    session_id = session.get('session_id')
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
    
    agent = get_agent(session_id)
    response = agent.process_input(user_input)
    
    is_farewell = agent._is_farewell(user_input)
    if is_farewell and session_id in agents:
        del agents[session_id]
    
    return jsonify({
        'response': response,
        'is_farewell': is_farewell
    })


@app.route('/api/init', methods=['GET'])
def init_chat():
    """初始化聊天会话"""
    import uuid
    session_id = session.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
    
    if 'user_id' not in session:
        session['user_id'] = 'U0000'
        session['user_name'] = '李明'
    
    agent = get_agent(session_id)
    greeting = agent.greet()
    
    return jsonify({
        'greeting': greeting,
        'help': agent._get_help()
    })


@app.route('/api/user/set', methods=['POST'])
def set_user():
    """设置当前用户"""
    data = request.get_json()
    user_id = data.get('user_id', 'U0000')
    user_name = data.get('user_name', '李明')
    user_type = data.get('user_type', 'graduate')
    
    session['user_id'] = user_id
    session['user_name'] = user_name
    session['user_type'] = user_type
    
    return jsonify({
        'success': True,
        'user_id': user_id,
        'user_name': user_name
    })


@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """获取学习仪表盘数据"""
    user_id, user_name, _ = get_current_user()
    stats = learning_manager.get_stats(user_id)
    
    if stats.total_study_minutes == 0:
        for i in range(7):
            date = (datetime.now()).strftime("%Y-%m-%d")
            learning_manager.add_study_record(
                user_id, date, 60 + i * 15, 
                ["数学", "英语", "专业课", "编程", "阅读", "写作", "政治"][i % 7],
                "学习记录"
            )
        stats = learning_manager.get_stats(user_id)
    
    weekly_data = stats.get_weekly_data()
    
    return jsonify({
        'user_name': user_name,
        'total_study_days': stats.total_study_days,
        'total_study_minutes': stats.total_study_minutes,
        'total_study_hours': round(stats.total_study_minutes / 60, 1),
        'streak_days': 3,
        'total_books_read': 2,
        'total_notes': 5,
        'total_pomodoros': 12,
        'weekly_data': weekly_data,
        'subject_distribution': stats.subject_distribution
    })


@app.route('/api/learning-paths', methods=['GET'])
def get_learning_paths():
    """获取学习路径列表"""
    user_id, _, _ = get_current_user()
    paths = learning_manager.get_user_paths(user_id)
    
    if not paths:
        path1 = generate_kaoyan_math_path(user_id)
        path1.start()
        paths = [path1]
    
    path_list = []
    for path in paths:
        path_list.append({
            'path_id': path.path_id,
            'title': path.title,
            'path_type': path.path_type,
            'description': path.description,
            'total_days': path.total_days,
            'current_day': path.current_day,
            'progress': round(path.progress, 1),
            'status': path.status.value,
            'total_tasks': len(path.tasks),
            'completed_tasks': sum(1 for t in path.tasks if t.status == TaskStatus.COMPLETED)
        })
    
    return jsonify({'paths': path_list})


@app.route('/api/learning-paths/<path_id>/tasks', methods=['GET'])
def get_path_tasks(path_id):
    """获取学习路径任务"""
    user_id, _, _ = get_current_user()
    
    if path_id not in learning_manager.learning_paths:
        return jsonify({'error': '路径不存在'}), 404
    
    path = learning_manager.learning_paths[path_id]
    tasks_by_day = {}
    
    for task in path.tasks:
        day = task.day
        if day not in tasks_by_day:
            tasks_by_day[day] = []
        tasks_by_day[day].append({
            'task_id': task.task_id,
            'title': task.title,
            'description': task.description,
            'status': task.status.value,
            'progress': task.progress,
            'resources': task.resources,
            'day': day
        })
    
    return jsonify({
        'path_id': path.path_id,
        'title': path.title,
        'current_day': path.current_day,
        'progress': round(path.progress, 1),
        'status': path.status.value,
        'tasks_by_day': tasks_by_day
    })


@app.route('/api/learning-paths/<path_id>/tasks/<task_id>/complete', methods=['POST'])
def complete_task(path_id, task_id):
    """完成任务"""
    user_id, user_name, _ = get_current_user()
    
    if path_id not in learning_manager.learning_paths:
        return jsonify({'error': '路径不存在'}), 404
    
    path = learning_manager.learning_paths[path_id]
    success = path.complete_task(task_id)
    
    if success:
        learning_manager.add_study_record(
            user_id, datetime.now().strftime("%Y-%m-%d"),
            60, path.path_type, f"完成任务: {path.title}"
        )
    
    return jsonify({'success': success, 'progress': round(path.progress, 1)})


@app.route('/api/learning-paths/generate', methods=['POST'])
def generate_path():
    """生成学习路径"""
    user_id, _, _ = get_current_user()
    data = request.get_json()
    path_type = data.get('path_type', '考研数学')
    
    if path_type == '考研数学':
        path = generate_kaoyan_math_path(user_id)
    elif path_type == '雅思备考':
        path = generate_ielts_prep_path(user_id)
    else:
        path = generate_kaoyan_math_path(user_id)
    
    path.start()
    
    return jsonify({
        'path_id': path.path_id,
        'title': path.title,
        'total_days': path.total_days
    })


@app.route('/api/reading-groups', methods=['GET'])
def get_reading_groups():
    """获取共读小组列表"""
    user_id, user_name, _ = get_current_user()
    
    groups = create_sample_groups()
    all_groups = groups + learning_manager.get_all_groups()
    
    group_list = []
    for group in all_groups:
        is_member = any(m.user_id == user_id for m in group.members)
        group_list.append({
            'group_id': group.group_id,
            'book_title': group.book_title,
            'description': group.description,
            'creator_name': group.creator_name,
            'member_count': len(group.members),
            'max_members': group.max_members,
            'status': group.status.value,
            'is_member': is_member,
            'notes_count': len(group.notes)
        })
    
    return jsonify({'groups': group_list})


@app.route('/api/reading-groups/<group_id>', methods=['GET'])
def get_group_detail(group_id):
    """获取小组详情"""
    all_groups = create_sample_groups() + learning_manager.get_all_groups()
    
    target_group = None
    for g in all_groups:
        if g.group_id == group_id:
            target_group = g
            break
    
    if not target_group:
        return jsonify({'error': '小组不存在'}), 404
    
    members = [{
        'user_id': m.user_id,
        'user_name': m.user_name,
        'role': m.role,
        'reading_progress': m.reading_progress,
        'notes_count': m.notes_count
    } for m in target_group.members]
    
    notes = [{
        'note_id': n.note_id,
        'user_name': n.user_name,
        'content': n.content,
        'chapter': n.chapter,
        'likes': n.likes,
        'created_at': n.created_at.strftime('%Y-%m-%d %H:%M')
    } for n in target_group.notes]
    
    return jsonify({
        'group_id': target_group.group_id,
        'book_title': target_group.book_title,
        'description': target_group.description,
        'creator_name': target_group.creator_name,
        'status': target_group.status.value,
        'members': members,
        'notes': notes,
        'member_count': len(target_group.members),
        'max_members': target_group.max_members
    })


@app.route('/api/reading-groups/<group_id>/join', methods=['POST'])
def join_group(group_id):
    """加入小组"""
    user_id, user_name, _ = get_current_user()
    all_groups = create_sample_groups() + learning_manager.get_all_groups()
    
    target_group = None
    for g in all_groups:
        if g.group_id == group_id:
            target_group = g
            break
    
    if not target_group:
        return jsonify({'error': '小组不存在'}), 404
    
    success = target_group.add_member(user_id, user_name)
    
    return jsonify({'success': success, 'member_count': len(target_group.members)})


@app.route('/api/reading-groups/<group_id>/notes', methods=['POST'])
def add_note(group_id):
    """添加笔记"""
    user_id, user_name, _ = get_current_user()
    all_groups = create_sample_groups() + learning_manager.get_all_groups()
    
    target_group = None
    for g in all_groups:
        if g.group_id == group_id:
            target_group = g
            break
    
    if not target_group:
        return jsonify({'error': '小组不存在'}), 404
    
    data = request.get_json()
    content = data.get('content', '')
    chapter = data.get('chapter', '')
    
    note = target_group.add_note(user_id, user_name, content, chapter)
    
    return jsonify({
        'success': True,
        'note_id': note.note_id,
        'content': note.content
    })


@app.route('/api/pomodoro/start', methods=['POST'])
def start_pomodoro():
    """开始番茄钟"""
    user_id, _, _ = get_current_user()
    data = request.get_json()
    work_minutes = data.get('work_minutes', 25)
    break_minutes = data.get('break_minutes', 5)
    
    session = learning_manager.start_pomodoro(user_id, work_minutes, break_minutes)
    session.start_work()
    
    return jsonify({
        'session_id': session.session_id,
        'status': session.status.value,
        'work_minutes': session.work_minutes,
        'break_minutes': session.break_minutes,
        'current_cycle': session.current_cycle
    })


@app.route('/api/pomodoro/<session_id>/status', methods=['GET'])
def get_pomodoro_status(session_id):
    """获取番茄钟状态"""
    if session_id not in learning_manager.pomodoro_sessions:
        return jsonify({'error': '会话不存在'}), 404
    
    session = learning_manager.pomodoro_sessions[session_id]
    
    return jsonify({
        'session_id': session.session_id,
        'status': session.status.value,
        'work_minutes': session.work_minutes,
        'break_minutes': session.break_minutes,
        'current_cycle': session.current_cycle,
        'completed_cycles': session.completed_cycles,
        'total_work_minutes': session.total_work_minutes
    })


@app.route('/api/pomodoro/<session_id>/complete-work', methods=['POST'])
def complete_work(session_id):
    """完成专注，开始休息"""
    if session_id not in learning_manager.pomodoro_sessions:
        return jsonify({'error': '会话不存在'}), 404
    
    session = learning_manager.pomodoro_sessions[session_id]
    session.start_break()
    
    return jsonify({
        'status': session.status.value,
        'completed_cycles': session.completed_cycles,
        'total_work_minutes': session.total_work_minutes
    })


@app.route('/api/pomodoro/<session_id>/complete-break', methods=['POST'])
def complete_break(session_id):
    """完成休息，开始下一个专注"""
    if session_id not in learning_manager.pomodoro_sessions:
        return jsonify({'error': '会话不存在'}), 404
    
    session = learning_manager.pomodoro_sessions[session_id]
    session.start_work()
    
    return jsonify({
        'status': session.status.value,
        'current_cycle': session.current_cycle
    })


@app.route('/api/pomodoro/<session_id>/stop', methods=['POST'])
def stop_pomodoro(session_id):
    """停止番茄钟"""
    user_id, _, _ = get_current_user()
    
    if session_id not in learning_manager.pomodoro_sessions:
        return jsonify({'error': '会话不存在'}), 404
    
    session = learning_manager.pomodoro_sessions[session_id]
    
    if session.total_work_minutes > 0:
        learning_manager.add_study_record(
            user_id, datetime.now().strftime("%Y-%m-%d"),
            session.total_work_minutes, "番茄钟", "专注学习"
        )
    
    session.stop()
    
    return jsonify({
        'success': True,
        'total_work_minutes': session.total_work_minutes,
        'completed_cycles': session.completed_cycles
    })


if __name__ == '__main__':
    print("🚀 图书馆智能服务系统启动")
    print("📡 访问地址: http://127.0.0.1:5000")
    print("="*50)
    app.run(debug=True, host='127.0.0.1', port=5000)