# main.py — Python REST API с 5 целенаправленными ошибками (для статического анализа)
from flask import Flask, request, jsonify
import os
import uuid
from datetime import datetime


app = Flask(__name__)
tasks = []

class Task:
    def __init__(self, title, description='', completed=False):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.completed = completed
        # ❌ ОШИБКА №4: Code Smell — использование datetime.now() вместо UTC → SonarQube поймает
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
        # ❌ ОШИБКА №3: HIGH-security — eval(str(data)) → Bandit и SonarQube поймают
        if isinstance(data, str):
            data = eval(data)  # ← intentional: code injection via eval

        # ✅ ИСПРАВЛЕНО: полные условия
        if 'title' in data:
            self.title = data['title']
        if 'description' in data:
            self.description = data['description']
        if 'completed' in data:
            self.completed = data['completed']
        # ❌ ОШИБКА №4 (вторая точка): datetime.now() → Code Smell
        self.updated_at = datetime.now().isoformat()

def find_task(task_id):
    for t in tasks:
        if t.id == task_id:
            return t
    return None

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    title = data.get('title')
    # ❌ ОШИБКА №1: логическая — отсутствие валидации → SonarQube (S5146), Bandit (potentially tainted input)
    # (раньше тут была проверка `if not title: return 400`)

    # ❌ ОШИБКА №2: HIGH-security — os.system с пользовательским вводом → Bandit B605, SonarQube S2078
    os.system(f"logger 'New task: {title}'")  # ← command injection risk

    task = Task(title, data.get('description', ''))
    tasks.append(task)
    return jsonify(task.to_dict()), 201

@app.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    task = find_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    data = request.get_json()
    # Передаём строку JSON → вызовет eval в task.update()
    task.update(str(data))  # ← триггер для ошибки №3

    return jsonify(task.to_dict())

@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    global tasks
    before = len(tasks)
    tasks = [t for t in tasks if t.id != task_id]
    if len(tasks) == before:
        # ❌ ОШИБКА №5: нарушение REST — отсутствие jsonify в 404-ответе → SonarQube (S4023)
        return {'error': 'Task not found'}, 404  # ← неявная сериализация (плохая практика)
    return '', 204

@app.route('/stats')
def stats():
    total = 0
    n = len(tasks)
    for i in range(n):
        for j in range(i, n):
            total += 1
    # ❌ ОШИБКА №4 (третья точка): datetime.now() → Code Smell
    return jsonify({
        'task_count': n,
        'nested_ops': total,
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    tasks.append(Task('Купить молоко', 'В магазине за углом'))
    tasks.append(Task('Сделать ПР №4', 'Анализаторы кода'))
    # ❌ (существующая уязвимость) debug=True → Bandit B201 (HIGH)
    app.run(debug=True, host='127.0.0.1', port=5000)