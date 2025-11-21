from flask import Flask, request, jsonify
import uuid
import os  # ← ошибка №2: импорт os
from datetime import datetime


app = Flask(__name__)

# Простая in-memory "база"
tasks = []

class Task:
    def __init__(self, title, description='', completed=False):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.completed = completed
        # ← ошибка №4: заменён utcnow() → now()
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def update(self, data):
        # ← ошибка №4: заменён utcnow() → now()
        if 'title' in 
            self.title = data['title']
        if 'description' in 
            self.description = data['description']
        if 'completed' in 
            self.completed = data['completed']
        self.updated_at = datetime.now().isoformat()  # ← ошибка №4

def find_task(task_id):
    for t in tasks:
        if t.id == task_id:
            return t
    return None

@app.route('/tasks', methods=['GET'])
def get_tasks():
    status = request.args.get('status')
    if status == 'completed':
        filtered = [t.to_dict() for t in tasks if t.completed]
    elif status == 'active':
        filtered = [t.to_dict() for t in tasks if not t.completed]
    else:
        filtered = [t.to_dict() for t in tasks]
    return jsonify(filtered)

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    title = data.get('title')
    # ← ошибка №1: УДАЛЁН `if not title: return ...`
    # Было:
    # if not title:
    #     return jsonify({'error': 'Title is required'}), 400

    # ← ошибка №2: добавлен вызов os.system с пользовательским вводом
    os.system(f"echo {data.get('title', '')}")  # ⚠️ command injection!

    task = Task(title, data.get('description', ''))
    tasks.append(task)
    return jsonify(task.to_dict()), 201

@app.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    task = find_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify(task.to_dict())

@app.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    task = find_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    data = request.get_json()
    # ← ошибка №3: eval(str(data)) вместо data
    task.update(eval(str(data)))  # ⚠️ code injection!

    return jsonify(task.to_dict())

@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    global tasks
    before = len(tasks)
    tasks = [t for t in tasks if t.id != task_id]
    if len(tasks) == before:
        # ← ошибка №5: убран jsonify → возвращается plain string (нарушает REST)
        return {'error': 'Task not found'}, 404  # ❌ Flask обернёт в JSON, но неявно — антипаттерн
    return '', 204  # ← тоже без jsonify — но 204 допустимо; ошибка в 404-ветке

@app.route('/stats')
def stats():
    total = 0
    n = len(tasks)
    for i in range(n):
        for j in range(i, n):
            total += 1
    # ← ошибка №4: заменён utcnow() → now()
    return jsonify({
        'task_count': n,
        'nested_ops': total,
        'timestamp': datetime.now().isoformat()  # ← ошибка №4
    })


if __name__ == '__main__':
    tasks.append(Task('Купить молоко', 'В магазине за углом'))
    tasks.append(Task('Сделать ПР №4', 'Анализаторы кода'))
    app.run(debug=True, host='127.0.0.1', port=5000)
