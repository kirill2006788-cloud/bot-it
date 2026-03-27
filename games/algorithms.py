from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, GameScore, GameSession
import random
import json
from datetime import datetime

algorithms_bp = Blueprint('algorithms', __name__)

# Алгоритмы для визуализации
ALGORITHMS = {
    'sorting': {
        'bubble_sort': {
            'name': 'Пузырьковая сортировка',
            'description': 'Простой алгоритм сортировки, который многократно проходит по списку',
            'complexity': 'O(n²)',
            'steps': []
        },
        'selection_sort': {
            'name': 'Сортировка выбором',
            'description': 'Находит минимальный элемент и помещает его в начало',
            'complexity': 'O(n²)',
            'steps': []
        },
        'insertion_sort': {
            'name': 'Сортировка вставками',
            'description': 'Строит отсортированную последовательность по одному элементу',
            'complexity': 'O(n²)',
            'steps': []
        },
        'merge_sort': {
            'name': 'Сортировка слиянием',
            'description': 'Разделяет массив пополам и рекурсивно сортирует',
            'complexity': 'O(n log n)',
            'steps': []
        },
        'quick_sort': {
            'name': 'Быстрая сортировка',
            'description': 'Выбирает опорный элемент и разделяет массив',
            'complexity': 'O(n log n)',
            'steps': []
        }
    },
    'searching': {
        'linear_search': {
            'name': 'Линейный поиск',
            'description': 'Последовательно проверяет каждый элемент',
            'complexity': 'O(n)',
            'steps': []
        },
        'binary_search': {
            'name': 'Бинарный поиск',
            'description': 'Ищет в отсортированном массиве, исключая половину элементов',
            'complexity': 'O(log n)',
            'steps': []
        }
    },
    'graph': {
        'dfs': {
            'name': 'Поиск в глубину',
            'description': 'Обходит граф, углубляясь насколько возможно',
            'complexity': 'O(V + E)',
            'steps': []
        },
        'bfs': {
            'name': 'Поиск в ширину',
            'description': 'Обходит граф по уровням',
            'complexity': 'O(V + E)',
            'steps': []
        }
    }
}

@algorithms_bp.route('/api/games/algorithms/visualize', methods=['POST'])
@login_required
def visualize_algorithm():
    """Визуализация алгоритма"""
    try:
        data = request.get_json()
        algorithm_type = data.get('algorithm_type', 'sorting')  # sorting, searching, graph
        algorithm_name = data.get('algorithm_name', 'bubble_sort')
        input_data = data.get('input_data', [])
        
        if not input_data:
            # Генерация случайных данных
            if algorithm_type == 'sorting':
                input_data = generate_random_array(10)
            elif algorithm_type == 'searching':
                input_data = generate_sorted_array(10)
            elif algorithm_type == 'graph':
                input_data = generate_graph_data()
        
        # Получение алгоритма
        algorithm_info = ALGORITHMS.get(algorithm_type, {}).get(algorithm_name)
        if not algorithm_info:
            return jsonify({'error': 'Алгоритм не найден'}), 404
        
        # Выполнение алгоритма с визуализацией
        visualization = execute_algorithm(algorithm_name, input_data)
        
        # Создание игровой сессии
        session_id = f"algorithms_{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        game_session = GameSession(
            user_id=current_user.id,
            session_id=session_id,
            game_type='algorithms',
            game_data=json.dumps({
                'algorithm_type': algorithm_type,
                'algorithm_name': algorithm_name,
                'input_data': input_data,
                'visualization': visualization,
                'start_time': datetime.utcnow().isoformat(),
                'current_step': 0,
                'total_steps': len(visualization['steps']),
                'game_state': 'playing'
            })
        )
        
        db.session.add(game_session)
        db.session.commit()
        
        return jsonify({
            'session_id': session_id,
            'algorithm_info': algorithm_info,
            'input_data': input_data,
            'visualization': visualization,
            'created_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при визуализации алгоритма'}), 500

@algorithms_bp.route('/api/games/algorithms/step', methods=['POST'])
@login_required
def next_algorithm_step():
    """Переход к следующему шагу алгоритма"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'ID сессии не указан'}), 400
        
        # Получение игровой сессии
        game_session = GameSession.query.filter_by(
            session_id=session_id,
            user_id=current_user.id
        ).first()
        
        if not game_session:
            return jsonify({'error': 'Игровая сессия не найдена'}), 404
        
        game_data = game_session.get_game_data()
        
        # Проверка состояния игры
        if game_data['game_state'] != 'playing':
            return jsonify({'error': 'Визуализация уже завершена'}), 400
        
        # Переход к следующему шагу
        game_data['current_step'] += 1
        
        # Проверка завершения
        if game_data['current_step'] >= game_data['total_steps']:
            game_data['game_state'] = 'completed'
            
            # Сохранение результата
            time_spent = calculate_game_time(game_data['start_time'])
            score = calculate_algorithm_score(game_data, time_spent)
            
            game_score = GameScore(
                user_id=current_user.id,
                game_type='algorithms',
                score=score,
                level=1,
                time_spent=time_spent
            )
            
            db.session.add(game_score)
            db.session.commit()
            
            # Проверка достижений
            from achievements import check_game_achievements
            check_game_achievements(current_user.id, 'algorithms', score, time_spent)
            
            return jsonify({
                'step': game_data['visualization']['steps'][game_data['current_step'] - 1],
                'current_step': game_data['current_step'],
                'total_steps': game_data['total_steps'],
                'game_state': 'completed',
                'score': score,
                'time_spent': time_spent,
                'message': 'Визуализация завершена!'
            })
        
        # Получение текущего шага
        current_step = game_data['visualization']['steps'][game_data['current_step'] - 1]
        
        # Сохранение прогресса
        game_session.set_game_data(game_data)
        db.session.commit()
        
        return jsonify({
            'step': current_step,
            'current_step': game_data['current_step'],
            'total_steps': game_data['total_steps'],
            'game_state': 'playing'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при переходе к следующему шагу'}), 500

@algorithms_bp.route('/api/games/algorithms/algorithms', methods=['GET'])
def get_available_algorithms():
    """Получение доступных алгоритмов"""
    try:
        return jsonify({'algorithms': ALGORITHMS})
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении алгоритмов'}), 500

def generate_random_array(size):
    """Генерация случайного массива"""
    return [random.randint(1, 100) for _ in range(size)]

def generate_sorted_array(size):
    """Генерация отсортированного массива"""
    return list(range(1, size + 1))

def generate_graph_data():
    """Генерация данных графа"""
    return {
        'nodes': ['A', 'B', 'C', 'D', 'E'],
        'edges': [
            {'from': 'A', 'to': 'B', 'weight': 1},
            {'from': 'A', 'to': 'C', 'weight': 2},
            {'from': 'B', 'to': 'D', 'weight': 3},
            {'from': 'C', 'to': 'D', 'weight': 1},
            {'from': 'D', 'to': 'E', 'weight': 2}
        ]
    }

def execute_algorithm(algorithm_name, input_data):
    """Выполнение алгоритма с визуализацией"""
    if algorithm_name == 'bubble_sort':
        return bubble_sort_visualization(input_data)
    elif algorithm_name == 'selection_sort':
        return selection_sort_visualization(input_data)
    elif algorithm_name == 'insertion_sort':
        return insertion_sort_visualization(input_data)
    elif algorithm_name == 'merge_sort':
        return merge_sort_visualization(input_data)
    elif algorithm_name == 'quick_sort':
        return quick_sort_visualization(input_data)
    elif algorithm_name == 'linear_search':
        return linear_search_visualization(input_data)
    elif algorithm_name == 'binary_search':
        return binary_search_visualization(input_data)
    elif algorithm_name == 'dfs':
        return dfs_visualization(input_data)
    elif algorithm_name == 'bfs':
        return bfs_visualization(input_data)
    else:
        return {'steps': [], 'result': input_data}

def bubble_sort_visualization(arr):
    """Визуализация пузырьковой сортировки"""
    steps = []
    n = len(arr)
    arr_copy = arr.copy()
    
    for i in range(n):
        for j in range(0, n - i - 1):
            steps.append({
                'type': 'compare',
                'indices': [j, j + 1],
                'array': arr_copy.copy(),
                'description': f'Сравниваем {arr_copy[j]} и {arr_copy[j + 1]}'
            })
            
            if arr_copy[j] > arr_copy[j + 1]:
                arr_copy[j], arr_copy[j + 1] = arr_copy[j + 1], arr_copy[j]
                steps.append({
                    'type': 'swap',
                    'indices': [j, j + 1],
                    'array': arr_copy.copy(),
                    'description': f'Меняем местами {arr_copy[j + 1]} и {arr_copy[j]}'
                })
    
    return {
        'steps': steps,
        'result': arr_copy,
        'comparisons': len([s for s in steps if s['type'] == 'compare']),
        'swaps': len([s for s in steps if s['type'] == 'swap'])
    }

def selection_sort_visualization(arr):
    """Визуализация сортировки выбором"""
    steps = []
    arr_copy = arr.copy()
    n = len(arr_copy)
    
    for i in range(n):
        min_idx = i
        steps.append({
            'type': 'select',
            'indices': [i],
            'array': arr_copy.copy(),
            'description': f'Ищем минимальный элемент начиная с позиции {i}'
        })
        
        for j in range(i + 1, n):
            steps.append({
                'type': 'compare',
                'indices': [min_idx, j],
                'array': arr_copy.copy(),
                'description': f'Сравниваем {arr_copy[min_idx]} и {arr_copy[j]}'
            })
            
            if arr_copy[j] < arr_copy[min_idx]:
                min_idx = j
                steps.append({
                    'type': 'update_min',
                    'indices': [j],
                    'array': arr_copy.copy(),
                    'description': f'Новый минимальный элемент: {arr_copy[j]}'
                })
        
        if min_idx != i:
            arr_copy[i], arr_copy[min_idx] = arr_copy[min_idx], arr_copy[i]
            steps.append({
                'type': 'swap',
                'indices': [i, min_idx],
                'array': arr_copy.copy(),
                'description': f'Меняем местами {arr_copy[min_idx]} и {arr_copy[i]}'
            })
    
    return {
        'steps': steps,
        'result': arr_copy,
        'comparisons': len([s for s in steps if s['type'] == 'compare']),
        'swaps': len([s for s in steps if s['type'] == 'swap'])
    }

def insertion_sort_visualization(arr):
    """Визуализация сортировки вставками"""
    steps = []
    arr_copy = arr.copy()
    
    for i in range(1, len(arr_copy)):
        key = arr_copy[i]
        j = i - 1
        
        steps.append({
            'type': 'insert',
            'indices': [i],
            'array': arr_copy.copy(),
            'description': f'Вставляем элемент {key} в отсортированную часть'
        })
        
        while j >= 0 and arr_copy[j] > key:
            steps.append({
                'type': 'compare',
                'indices': [j, j + 1],
                'array': arr_copy.copy(),
                'description': f'Сравниваем {arr_copy[j]} и {key}'
            })
            
            arr_copy[j + 1] = arr_copy[j]
            j -= 1
            
            steps.append({
                'type': 'shift',
                'indices': [j + 1],
                'array': arr_copy.copy(),
                'description': f'Сдвигаем элемент {arr_copy[j + 1]}'
            })
        
        arr_copy[j + 1] = key
        steps.append({
            'type': 'place',
            'indices': [j + 1],
            'array': arr_copy.copy(),
            'description': f'Помещаем {key} на позицию {j + 1}'
        })
    
    return {
        'steps': steps,
        'result': arr_copy,
        'comparisons': len([s for s in steps if s['type'] == 'compare']),
        'shifts': len([s for s in steps if s['type'] == 'shift'])
    }

def merge_sort_visualization(arr):
    """Визуализация сортировки слиянием"""
    steps = []
    arr_copy = arr.copy()
    
    def merge_sort_recursive(arr, left, right):
        if left < right:
            mid = (left + right) // 2
            
            steps.append({
                'type': 'divide',
                'indices': [left, mid, right],
                'array': arr.copy(),
                'description': f'Разделяем массив на части [{left}:{mid}] и [{mid+1}:{right}]'
            })
            
            merge_sort_recursive(arr, left, mid)
            merge_sort_recursive(arr, mid + 1, right)
            
            steps.append({
                'type': 'merge',
                'indices': [left, mid, right],
                'array': arr.copy(),
                'description': f'Сливаем отсортированные части [{left}:{mid}] и [{mid+1}:{right}]'
            })
            
            merge(arr, left, mid, right)
    
    def merge(arr, left, mid, right):
        left_arr = arr[left:mid + 1]
        right_arr = arr[mid + 1:right + 1]
        
        i = j = 0
        k = left
        
        while i < len(left_arr) and j < len(right_arr):
            steps.append({
                'type': 'compare',
                'indices': [k],
                'array': arr.copy(),
                'description': f'Сравниваем {left_arr[i]} и {right_arr[j]}'
            })
            
            if left_arr[i] <= right_arr[j]:
                arr[k] = left_arr[i]
                i += 1
            else:
                arr[k] = right_arr[j]
                j += 1
            k += 1
        
        while i < len(left_arr):
            arr[k] = left_arr[i]
            i += 1
            k += 1
        
        while j < len(right_arr):
            arr[k] = right_arr[j]
            j += 1
            k += 1
    
    merge_sort_recursive(arr_copy, 0, len(arr_copy) - 1)
    
    return {
        'steps': steps,
        'result': arr_copy,
        'comparisons': len([s for s in steps if s['type'] == 'compare']),
        'merges': len([s for s in steps if s['type'] == 'merge'])
    }

def quick_sort_visualization(arr):
    """Визуализация быстрой сортировки"""
    steps = []
    arr_copy = arr.copy()
    
    def quick_sort_recursive(arr, low, high):
        if low < high:
            steps.append({
                'type': 'partition',
                'indices': [low, high],
                'array': arr.copy(),
                'description': f'Разделяем массив [{low}:{high}]'
            })
            
            pi = partition(arr, low, high)
            
            steps.append({
                'type': 'pivot',
                'indices': [pi],
                'array': arr.copy(),
                'description': f'Опорный элемент {arr[pi]} на позиции {pi}'
            })
            
            quick_sort_recursive(arr, low, pi - 1)
            quick_sort_recursive(arr, pi + 1, high)
    
    def partition(arr, low, high):
        pivot = arr[high]
        i = low - 1
        
        for j in range(low, high):
            steps.append({
                'type': 'compare',
                'indices': [j, high],
                'array': arr.copy(),
                'description': f'Сравниваем {arr[j]} с опорным элементом {pivot}'
            })
            
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
                steps.append({
                    'type': 'swap',
                    'indices': [i, j],
                    'array': arr.copy(),
                    'description': f'Меняем местами {arr[j]} и {arr[i]}'
                })
        
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        steps.append({
            'type': 'swap',
            'indices': [i + 1, high],
            'array': arr.copy(),
            'description': f'Помещаем опорный элемент {pivot} на позицию {i + 1}'
        })
        
        return i + 1
    
    quick_sort_recursive(arr_copy, 0, len(arr_copy) - 1)
    
    return {
        'steps': steps,
        'result': arr_copy,
        'comparisons': len([s for s in steps if s['type'] == 'compare']),
        'swaps': len([s for s in steps if s['type'] == 'swap'])
    }

def linear_search_visualization(arr):
    """Визуализация линейного поиска"""
    steps = []
    target = random.choice(arr)  # Случайный элемент для поиска
    
    steps.append({
        'type': 'start',
        'indices': [],
        'array': arr.copy(),
        'description': f'Ищем элемент {target}'
    })
    
    for i, element in enumerate(arr):
        steps.append({
            'type': 'compare',
            'indices': [i],
            'array': arr.copy(),
            'description': f'Проверяем элемент {element} на позиции {i}'
        })
        
        if element == target:
            steps.append({
                'type': 'found',
                'indices': [i],
                'array': arr.copy(),
                'description': f'Элемент {target} найден на позиции {i}!'
            })
            break
    else:
        steps.append({
            'type': 'not_found',
            'indices': [],
            'array': arr.copy(),
            'description': f'Элемент {target} не найден'
        })
    
    return {
        'steps': steps,
        'result': target,
        'comparisons': len([s for s in steps if s['type'] == 'compare']),
        'target': target
    }

def binary_search_visualization(arr):
    """Визуализация бинарного поиска"""
    steps = []
    target = random.choice(arr)  # Случайный элемент для поиска
    left, right = 0, len(arr) - 1
    
    steps.append({
        'type': 'start',
        'indices': [left, right],
        'array': arr.copy(),
        'description': f'Ищем элемент {target} в отсортированном массиве'
    })
    
    while left <= right:
        mid = (left + right) // 2
        
        steps.append({
            'type': 'compare',
            'indices': [mid],
            'array': arr.copy(),
            'description': f'Сравниваем элемент {arr[mid]} на позиции {mid} с {target}'
        })
        
        if arr[mid] == target:
            steps.append({
                'type': 'found',
                'indices': [mid],
                'array': arr.copy(),
                'description': f'Элемент {target} найден на позиции {mid}!'
            })
            break
        elif arr[mid] < target:
            left = mid + 1
            steps.append({
                'type': 'narrow',
                'indices': [left, right],
                'array': arr.copy(),
                'description': f'Ищем в правой половине [{left}:{right}]'
            })
        else:
            right = mid - 1
            steps.append({
                'type': 'narrow',
                'indices': [left, right],
                'array': arr.copy(),
                'description': f'Ищем в левой половине [{left}:{right}]'
            })
    else:
        steps.append({
            'type': 'not_found',
            'indices': [],
            'array': arr.copy(),
            'description': f'Элемент {target} не найден'
        })
    
    return {
        'steps': steps,
        'result': target,
        'comparisons': len([s for s in steps if s['type'] == 'compare']),
        'target': target
    }

def dfs_visualization(graph_data):
    """Визуализация поиска в глубину"""
    steps = []
    visited = set()
    start_node = graph_data['nodes'][0]
    
    def dfs_recursive(node):
        if node in visited:
            return
        
        visited.add(node)
        steps.append({
            'type': 'visit',
            'indices': [node],
            'array': graph_data.copy(),
            'description': f'Посещаем узел {node}'
        })
        
        for edge in graph_data['edges']:
            if edge['from'] == node and edge['to'] not in visited:
                steps.append({
                    'type': 'explore',
                    'indices': [node, edge['to']],
                    'array': graph_data.copy(),
                    'description': f'Исследуем ребро {node} -> {edge['to']}'
                })
                dfs_recursive(edge['to'])
    
    dfs_recursive(start_node)
    
    return {
        'steps': steps,
        'result': list(visited),
        'visited_nodes': len(visited),
        'start_node': start_node
    }

def bfs_visualization(graph_data):
    """Визуализация поиска в ширину"""
    steps = []
    visited = set()
    queue = [graph_data['nodes'][0]]
    
    steps.append({
        'type': 'start',
        'indices': [queue[0]],
        'array': graph_data.copy(),
        'description': f'Начинаем BFS с узла {queue[0]}'
    })
    
    while queue:
        node = queue.pop(0)
        
        if node not in visited:
            visited.add(node)
            steps.append({
                'type': 'visit',
                'indices': [node],
                'array': graph_data.copy(),
                'description': f'Посещаем узел {node}'
            })
            
            for edge in graph_data['edges']:
                if edge['from'] == node and edge['to'] not in visited:
                    queue.append(edge['to'])
                    steps.append({
                        'type': 'enqueue',
                        'indices': [edge['to']],
                        'array': graph_data.copy(),
                        'description': f'Добавляем узел {edge['to']} в очередь'
                    })
    
    return {
        'steps': steps,
        'result': list(visited),
        'visited_nodes': len(visited),
        'start_node': graph_data['nodes'][0]
    }

def calculate_game_time(start_time_str):
    """Расчет времени игры"""
    start_time = datetime.fromisoformat(start_time_str)
    end_time = datetime.utcnow()
    return int((end_time - start_time).total_seconds())

def calculate_algorithm_score(game_data, time_spent):
    """Расчет очков за визуализацию алгоритма"""
    base_score = 100
    
    # Бонус за сложность алгоритма
    complexity_bonus = {
        'bubble_sort': 0,
        'selection_sort': 10,
        'insertion_sort': 10,
        'merge_sort': 30,
        'quick_sort': 30,
        'linear_search': 0,
        'binary_search': 20,
        'dfs': 25,
        'bfs': 25
    }.get(game_data['algorithm_name'], 0)
    
    # Бонус за быструю визуализацию
    time_bonus = 0
    if time_spent < 60:  # Менее минуты
        time_bonus = 25
    elif time_spent < 120:  # Менее двух минут
        time_bonus = 15
    
    score = base_score + complexity_bonus + time_bonus
    
    return max(0, score)

def get_algorithm_statistics(user_id):
    """Получение статистики визуализаций алгоритмов"""
    try:
        games = GameScore.query.filter_by(
            user_id=user_id,
            game_type='algorithms'
        ).all()
        
        if not games:
            return {
                'visualizations_played': 0,
                'average_score': 0,
                'best_score': 0,
                'total_time': 0,
                'average_time': 0
            }
        
        total_score = sum(game.score for game in games)
        total_time = sum(game.time_spent for game in games)
        best_score = max(game.score for game in games)
        
        return {
            'visualizations_played': len(games),
            'average_score': round(total_score / len(games), 2),
            'best_score': best_score,
            'total_time': total_time,
            'average_time': round(total_time / len(games), 2)
        }
        
    except Exception as e:
        return {
            'visualizations_played': 0,
            'average_score': 0,
            'best_score': 0,
            'total_time': 0,
            'average_time': 0
        }

def get_algorithm_tips():
    """Получение советов по алгоритмам"""
    tips = [
        "Изучайте сложность алгоритмов - это поможет выбрать правильный алгоритм",
        "Практикуйтесь с разными типами данных для лучшего понимания",
        "Визуализация помогает понять, как работают алгоритмы",
        "Начинайте с простых алгоритмов и постепенно переходите к сложным",
        "Обращайте внимание на количество сравнений и обменов",
        "Изучайте рекурсивные алгоритмы - они элегантны и эффективны",
        "Помните, что лучший алгоритм зависит от размера данных",
        "Анализируйте производительность алгоритмов на разных входных данных"
    ]
    
    return random.choice(tips)
