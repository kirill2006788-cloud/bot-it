from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, GameScore, GameSession
import random
import json
from datetime import datetime

sudoku_bp = Blueprint('sudoku', __name__)

@sudoku_bp.route('/api/games/sudoku/new', methods=['POST'])
@login_required
def new_sudoku_game():
    """Создание новой игры Судоку"""
    try:
        data = request.get_json()
        difficulty = data.get('difficulty', 'medium')  # easy, medium, hard
        
        # Генерация новой головоломки
        puzzle = generate_sudoku_puzzle(difficulty)
        
        # Создание игровой сессии
        session_id = f"sudoku_{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        game_session = GameSession(
            user_id=current_user.id,
            session_id=session_id,
            game_type='sudoku',
            game_data=json.dumps({
                'puzzle': puzzle['puzzle'],
                'solution': puzzle['solution'],
                'difficulty': difficulty,
                'start_time': datetime.utcnow().isoformat(),
                'moves': [],
                'hints_used': 0,
                'errors': 0
            })
        )
        
        db.session.add(game_session)
        db.session.commit()
        
        return jsonify({
            'session_id': session_id,
            'puzzle': puzzle['puzzle'],
            'difficulty': difficulty,
            'created_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при создании игры Судоку'}), 500

@sudoku_bp.route('/api/games/sudoku/move', methods=['POST'])
@login_required
def make_sudoku_move():
    """Сделать ход в Судоку"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        row = int(data.get('row'))
        col = int(data.get('col'))
        value = int(data.get('value'))
        
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
        
        # Проверка валидности хода
        if not is_valid_move(game_data['puzzle'], row, col, value):
            game_data['errors'] += 1
            game_session.set_game_data(game_data)
            db.session.commit()
            
            return jsonify({
                'valid': False,
                'message': 'Недопустимый ход',
                'errors': game_data['errors']
            })
        
        # Обновление головоломки
        game_data['puzzle'][row][col] = value
        game_data['moves'].append({
            'row': row,
            'col': col,
            'value': value,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Проверка завершения игры
        if is_puzzle_complete(game_data['puzzle']):
            # Сохранение результата
            time_spent = calculate_game_time(game_data['start_time'])
            score = calculate_sudoku_score(game_data, time_spent)
            
            game_score = GameScore(
                user_id=current_user.id,
                game_type='sudoku',
                score=score,
                level=1,
                time_spent=time_spent
            )
            
            db.session.add(game_score)
            db.session.commit()
            
            # Проверка достижений
            from achievements import check_game_achievements
            check_game_achievements(current_user.id, 'sudoku', score, time_spent)
            
            return jsonify({
                'valid': True,
                'completed': True,
                'score': score,
                'time_spent': time_spent,
                'message': 'Поздравляем! Головоломка решена!'
            })
        
        # Сохранение прогресса
        game_session.set_game_data(game_data)
        db.session.commit()
        
        return jsonify({
            'valid': True,
            'completed': False,
            'puzzle': game_data['puzzle'],
            'moves_count': len(game_data['moves'])
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при выполнении хода'}), 500

@sudoku_bp.route('/api/games/sudoku/hint', methods=['POST'])
@login_required
def get_sudoku_hint():
    """Получить подсказку в Судоку"""
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
        
        # Поиск пустой клетки для подсказки
        hint = find_hint_cell(game_data['puzzle'], game_data['solution'])
        
        if hint:
            game_data['hints_used'] += 1
            game_data['puzzle'][hint['row']][hint['col']] = hint['value']
            
            game_session.set_game_data(game_data)
            db.session.commit()
            
            return jsonify({
                'hint': hint,
                'hints_used': game_data['hints_used'],
                'puzzle': game_data['puzzle']
            })
        else:
            return jsonify({'error': 'Подсказка недоступна'}), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при получении подсказки'}), 500

@sudoku_bp.route('/api/games/sudoku/validate', methods=['POST'])
@login_required
def validate_sudoku():
    """Проверка правильности решения Судоку"""
    try:
        data = request.get_json()
        puzzle = data.get('puzzle', [])
        
        if not puzzle:
            return jsonify({'error': 'Головоломка не предоставлена'}), 400
        
        # Проверка правильности решения
        is_valid = is_valid_sudoku_solution(puzzle)
        
        return jsonify({
            'valid': is_valid,
            'message': 'Решение правильное' if is_valid else 'Решение содержит ошибки'
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при проверке решения'}), 500

def generate_sudoku_puzzle(difficulty):
    """Генерация головоломки Судоку"""
    # Создание полного решения
    solution = create_full_sudoku()
    
    # Создание головоломки путем удаления чисел
    puzzle = [row[:] for row in solution]
    
    # Количество клеток для удаления в зависимости от сложности
    cells_to_remove = {
        'easy': 40,
        'medium': 50,
        'hard': 60
    }
    
    remove_count = cells_to_remove.get(difficulty, 50)
    
    # Удаление чисел
    removed = 0
    while removed < remove_count:
        row = random.randint(0, 8)
        col = random.randint(0, 8)
        
        if puzzle[row][col] != 0:
            puzzle[row][col] = 0
            removed += 1
    
    return {
        'puzzle': puzzle,
        'solution': solution
    }

def create_full_sudoku():
    """Создание полного решения Судоку"""
    # Инициализация пустой сетки
    grid = [[0 for _ in range(9)] for _ in range(9)]
    
    # Заполнение диагональных блоков 3x3
    fill_diagonal_boxes(grid)
    
    # Заполнение остальных клеток
    solve_sudoku(grid)
    
    return grid

def fill_diagonal_boxes(grid):
    """Заполнение диагональных блоков 3x3"""
    for i in range(0, 9, 3):
        fill_box(grid, i, i)

def fill_box(grid, row, col):
    """Заполнение блока 3x3"""
    numbers = list(range(1, 10))
    random.shuffle(numbers)
    
    for i in range(3):
        for j in range(3):
            grid[row + i][col + j] = numbers[i * 3 + j]

def solve_sudoku(grid):
    """Решение Судоку с помощью backtracking"""
    for row in range(9):
        for col in range(9):
            if grid[row][col] == 0:
                for num in range(1, 10):
                    if is_safe(grid, row, col, num):
                        grid[row][col] = num
                        if solve_sudoku(grid):
                            return True
                        grid[row][col] = 0
                return False
    return True

def is_safe(grid, row, col, num):
    """Проверка безопасности размещения числа"""
    # Проверка строки
    for x in range(9):
        if grid[row][x] == num:
            return False
    
    # Проверка столбца
    for x in range(9):
        if grid[x][col] == num:
            return False
    
    # Проверка блока 3x3
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if grid[i + start_row][j + start_col] == num:
                return False
    
    return True

def is_valid_move(puzzle, row, col, value):
    """Проверка валидности хода"""
    if row < 0 or row >= 9 or col < 0 or col >= 9:
        return False
    
    if value < 1 or value > 9:
        return False
    
    # Проверка, что клетка пустая
    if puzzle[row][col] != 0:
        return False
    
    # Проверка правил Судоку
    return is_safe(puzzle, row, col, value)

def is_puzzle_complete(puzzle):
    """Проверка завершения головоломки"""
    for row in puzzle:
        if 0 in row:
            return False
    
    return is_valid_sudoku_solution(puzzle)

def is_valid_sudoku_solution(puzzle):
    """Проверка правильности решения Судоку"""
    # Проверка строк
    for row in puzzle:
        if len(set(row)) != 9 or 0 in row:
            return False
    
    # Проверка столбцов
    for col in range(9):
        column = [puzzle[row][col] for row in range(9)]
        if len(set(column)) != 9:
            return False
    
    # Проверка блоков 3x3
    for i in range(0, 9, 3):
        for j in range(0, 9, 3):
            block = []
            for row in range(i, i + 3):
                for col in range(j, j + 3):
                    block.append(puzzle[row][col])
            if len(set(block)) != 9:
                return False
    
    return True

def find_hint_cell(puzzle, solution):
    """Поиск клетки для подсказки"""
    empty_cells = []
    
    for row in range(9):
        for col in range(9):
            if puzzle[row][col] == 0:
                empty_cells.append((row, col))
    
    if empty_cells:
        row, col = random.choice(empty_cells)
        return {
            'row': row,
            'col': col,
            'value': solution[row][col]
        }
    
    return None

def calculate_game_time(start_time_str):
    """Расчет времени игры"""
    start_time = datetime.fromisoformat(start_time_str)
    end_time = datetime.utcnow()
    return int((end_time - start_time).total_seconds())

def calculate_sudoku_score(game_data, time_spent):
    """Расчет очков за игру Судоку"""
    base_score = 100
    
    # Штраф за время
    time_penalty = min(time_spent // 60, 50)  # Максимум 50 очков за время
    
    # Штраф за подсказки
    hint_penalty = game_data['hints_used'] * 10
    
    # Штраф за ошибки
    error_penalty = game_data['errors'] * 5
    
    # Бонус за сложность
    difficulty_bonus = {
        'easy': 0,
        'medium': 25,
        'hard': 50
    }.get(game_data['difficulty'], 0)
    
    score = base_score + difficulty_bonus - time_penalty - hint_penalty - error_penalty
    
    return max(0, score)

def get_sudoku_statistics(user_id):
    """Получение статистики игр Судоку"""
    try:
        games = GameScore.query.filter_by(
            user_id=user_id,
            game_type='sudoku'
        ).all()
        
        if not games:
            return {
                'games_played': 0,
                'average_score': 0,
                'best_score': 0,
                'total_time': 0,
                'average_time': 0
            }
        
        total_score = sum(game.score for game in games)
        total_time = sum(game.time_spent for game in games)
        best_score = max(game.score for game in games)
        
        return {
            'games_played': len(games),
            'average_score': round(total_score / len(games), 2),
            'best_score': best_score,
            'total_time': total_time,
            'average_time': round(total_time / len(games), 2)
        }
        
    except Exception as e:
        return {
            'games_played': 0,
            'average_score': 0,
            'best_score': 0,
            'total_time': 0,
            'average_time': 0
        }

def generate_sudoku_tips():
    """Генерация советов по игре в Судоку"""
    tips = [
        "Начните с поиска очевидных чисел - клеток, где может быть только одно число",
        "Используйте метод исключения - ищите числа, которые не могут быть в определенных клетках",
        "Обращайте внимание на блоки 3x3 - они должны содержать все числа от 1 до 9",
        "Не спешите с подсказками - попробуйте решить самостоятельно",
        "Используйте карандашные пометки для отслеживания возможных чисел",
        "Ищите скрытые одиночки - числа, которые могут быть только в одной клетке блока",
        "Проверяйте строки и столбцы на наличие недостающих чисел",
        "Не бойтесь ошибаться - ошибки помогают учиться"
    ]
    
    return random.choice(tips)
