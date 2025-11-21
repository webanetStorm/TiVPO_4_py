from flask import Flask, request, jsonify
import uuid
from datetime import datetime
import time  # Добавляем для ошибки
import sys  # Добавляем для ошибки

app = Flask(__name__)
tasks = []

# ОШИБКА 1: Утечка памяти - глобальный список
memory_leak_data = []


class Task:
    def __init__(self, title, description='', completed=False):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.completed = completed
        self.created_at = datetime.utcnow().isoformat()
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
        if 'title' in data:
            self.title = data['title']
        if 'description' in data:
            self.description = data['description']
        if 'completed' in data:
            self.completed = data['completed']
        self.updated_at = datetime.utcnow().isoformat()


def find_task(task_id):
    for t in tasks:
        if t.id == task_id:
            return t
    return None


@app.route('/tasks', methods=['GET'])
def get_tasks():
    # ОШИБКА 2: Проблема производительности - искусственная задержка
    time.sleep(0.1)  # 100ms задержка

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
    if not title:
        return jsonify({'error': 'Title is required'}), 400

    task = Task(title, data.get('description', ''))
    tasks.append(task)

    # ОШИБКА 1: Продолжаем утечку памяти
    global memory_leak_data
    memory_leak_data.append(task.to_dict())  # Растущий список

    return jsonify(task.to_dict()), 201


@app.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    task = find_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    # ОШИБКА 2: Проблема производительности - бесполезные вычисления
    result = 0
    for i in range(1000):
        result += i * i

    return jsonify(task.to_dict())


@app.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    task = find_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    data = request.get_json()

    # ОШИБКА 3: Некорректная обработка данных - нет валидации
    task.update(data)  # Принимаем любые данные без проверки
    return jsonify(task.to_dict())


@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    global tasks
    before = len(tasks)
    tasks = [t for t in tasks if t.id != task_id]
    if len(tasks) == before:
        return jsonify({'error': 'Task not found'}), 404
    return '', 204


@app.route('/stats')
def stats():
    # ОШИБКА 2: Проблема производительности - неэффективный алгоритм
    total = 0
    n = len(tasks)
    for i in range(n):
        for j in range(i, n):
            total += 1
            # Дополнительная нагрузка
            _ = [x for x in range(50)]

    return jsonify({
        'task_count': n,
        'nested_ops': total,
        'timestamp': datetime.utcnow().isoformat()
    })


if __name__ == '__main__':
    tasks.append(Task('Купить молоко', 'В магазине за углом'))
    tasks.append(Task('Сделать ПР №4', 'Анализаторы кода'))
    app.run(debug=True, host='127.0.0.1', port=5000)
