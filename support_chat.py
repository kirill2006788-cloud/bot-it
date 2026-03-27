from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, User, SupportTicket, SupportMessage, SupportCategory
from datetime import datetime
import json

support_chat_bp = Blueprint('support_chat', __name__)

# Категории поддержки
SUPPORT_CATEGORIES = {
    'technical': {
        'name': 'Техническая поддержка',
        'description': 'Проблемы с функциональностью, баги, ошибки',
        'priority': 'high',
        'response_time': '2 часа'
    },
    'billing': {
        'name': 'Биллинг и платежи',
        'description': 'Вопросы по подписке, платежам, возвратам',
        'priority': 'high',
        'response_time': '1 час'
    },
    'feature': {
        'name': 'Запрос функций',
        'description': 'Предложения по улучшению, новые функции',
        'priority': 'medium',
        'response_time': '24 часа'
    },
    'general': {
        'name': 'Общие вопросы',
        'description': 'Общая информация, инструкции, FAQ',
        'priority': 'low',
        'response_time': '48 часов'
    },
    'api': {
        'name': 'API поддержка',
        'description': 'Вопросы по API, интеграции, документации',
        'priority': 'high',
        'response_time': '4 часа'
    }
}

@support_chat_bp.route('/api/support/tickets', methods=['GET'])
@login_required
def get_support_tickets():
    """Получение тикетов поддержки пользователя"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        status = request.args.get('status', 'all')
        category = request.args.get('category', 'all')
        
        # Фильтрация тикетов
        query = SupportTicket.query.filter_by(user_id=current_user.id)
        
        if status != 'all':
            query = query.filter_by(status=status)
        
        if category != 'all':
            query = query.filter_by(category=category)
        
        # Сортировка по дате создания
        query = query.order_by(SupportTicket.created_at.desc())
        
        # Пагинация
        tickets = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        tickets_data = []
        for ticket in tickets.items:
            # Получение последнего сообщения
            last_message = SupportMessage.query.filter_by(
                ticket_id=ticket.id
            ).order_by(SupportMessage.created_at.desc()).first()
            
            tickets_data.append({
                'id': ticket.id,
                'subject': ticket.subject,
                'category': ticket.category,
                'status': ticket.status,
                'priority': ticket.priority,
                'created_at': ticket.created_at.isoformat(),
                'updated_at': ticket.updated_at.isoformat(),
                'last_message': {
                    'content': last_message.content[:100] + '...' if last_message and len(last_message.content) > 100 else last_message.content if last_message else '',
                    'created_at': last_message.created_at.isoformat() if last_message else None,
                    'is_from_support': last_message.is_from_support if last_message else False
                } if last_message else None,
                'message_count': SupportMessage.query.filter_by(ticket_id=ticket.id).count()
            })
        
        return jsonify({
            'tickets': tickets_data,
            'total': tickets.total,
            'page': page,
            'per_page': per_page,
            'pages': tickets.pages
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении тикетов'}), 500

@support_chat_bp.route('/api/support/tickets', methods=['POST'])
@login_required
def create_support_ticket():
    """Создание нового тикета поддержки"""
    try:
        data = request.get_json()
        subject = data.get('subject', '').strip()
        category = data.get('category', 'general')
        priority = data.get('priority', 'medium')
        content = data.get('content', '').strip()
        
        if not subject or not content:
            return jsonify({'error': 'Тема и содержание обязательны'}), 400
        
        if category not in SUPPORT_CATEGORIES:
            return jsonify({'error': 'Неверная категория'}), 400
        
        # Создание тикета
        ticket = SupportTicket(
            user_id=current_user.id,
            subject=subject,
            category=category,
            priority=priority,
            status='open',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(ticket)
        db.session.flush()  # Получаем ID тикета
        
        # Создание первого сообщения
        message = SupportMessage(
            ticket_id=ticket.id,
            content=content,
            is_from_support=False,
            created_at=datetime.utcnow()
        )
        
        db.session.add(message)
        db.session.commit()
        
        return jsonify({
            'ticket_id': ticket.id,
            'subject': ticket.subject,
            'category': ticket.category,
            'priority': ticket.priority,
            'status': ticket.status,
            'created_at': ticket.created_at.isoformat(),
            'message': 'Тикет создан успешно'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при создании тикета'}), 500

@support_chat_bp.route('/api/support/tickets/<int:ticket_id>', methods=['GET'])
@login_required
def get_support_ticket(ticket_id):
    """Получение конкретного тикета"""
    try:
        ticket = SupportTicket.query.filter_by(
            id=ticket_id,
            user_id=current_user.id
        ).first()
        
        if not ticket:
            return jsonify({'error': 'Тикет не найден'}), 404
        
        # Получение сообщений
        messages = SupportMessage.query.filter_by(
            ticket_id=ticket_id
        ).order_by(SupportMessage.created_at.asc()).all()
        
        messages_data = []
        for message in messages:
            messages_data.append({
                'id': message.id,
                'content': message.content,
                'is_from_support': message.is_from_support,
                'created_at': message.created_at.isoformat(),
                'attachments': message.attachments or []
            })
        
        return jsonify({
            'ticket': {
                'id': ticket.id,
                'subject': ticket.subject,
                'category': ticket.category,
                'priority': ticket.priority,
                'status': ticket.status,
                'created_at': ticket.created_at.isoformat(),
                'updated_at': ticket.updated_at.isoformat()
            },
            'messages': messages_data
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении тикета'}), 500

@support_chat_bp.route('/api/support/tickets/<int:ticket_id>/messages', methods=['POST'])
@login_required
def add_message_to_ticket(ticket_id):
    """Добавление сообщения к тикету"""
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({'error': 'Содержание сообщения обязательно'}), 400
        
        # Проверка существования тикета
        ticket = SupportTicket.query.filter_by(
            id=ticket_id,
            user_id=current_user.id
        ).first()
        
        if not ticket:
            return jsonify({'error': 'Тикет не найден'}), 404
        
        if ticket.status == 'closed':
            return jsonify({'error': 'Тикет закрыт'}), 400
        
        # Создание сообщения
        message = SupportMessage(
            ticket_id=ticket_id,
            content=content,
            is_from_support=False,
            created_at=datetime.utcnow()
        )
        
        db.session.add(message)
        
        # Обновление статуса тикета
        if ticket.status == 'waiting_for_support':
            ticket.status = 'open'
        
        ticket.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message_id': message.id,
            'content': message.content,
            'created_at': message.created_at.isoformat(),
            'ticket_status': ticket.status
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при добавлении сообщения'}), 500

@support_chat_bp.route('/api/support/tickets/<int:ticket_id>/close', methods=['POST'])
@login_required
def close_support_ticket(ticket_id):
    """Закрытие тикета"""
    try:
        ticket = SupportTicket.query.filter_by(
            id=ticket_id,
            user_id=current_user.id
        ).first()
        
        if not ticket:
            return jsonify({'error': 'Тикет не найден'}), 404
        
        if ticket.status == 'closed':
            return jsonify({'error': 'Тикет уже закрыт'}), 400
        
        # Закрытие тикета
        ticket.status = 'closed'
        ticket.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Тикет закрыт',
            'status': ticket.status,
            'closed_at': ticket.updated_at.isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при закрытии тикета'}), 500

@support_chat_bp.route('/api/support/categories', methods=['GET'])
def get_support_categories():
    """Получение категорий поддержки"""
    try:
        return jsonify({
            'categories': SUPPORT_CATEGORIES
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении категорий'}), 500

@support_chat_bp.route('/api/support/faq', methods=['GET'])
def get_faq():
    """Получение часто задаваемых вопросов"""
    try:
        faq = [
            {
                'question': 'Как создать API ключ?',
                'answer': 'Перейдите в раздел "API ключи" в вашем профиле и нажмите "Создать новый ключ". Заполните необходимые поля и сохраните.',
                'category': 'api'
            },
            {
                'question': 'Как отменить подписку?',
                'answer': 'Перейдите в раздел "Платежи" и нажмите "Отменить подписку" рядом с вашей активной подпиской.',
                'category': 'billing'
            },
            {
                'question': 'Как экспортировать данные?',
                'answer': 'В разделе "Экспорт данных" выберите нужный формат (PDF, Excel, JSON) и нажмите "Экспорт".',
                'category': 'general'
            },
            {
                'question': 'Игра не запускается, что делать?',
                'answer': 'Попробуйте обновить страницу или очистить кэш браузера. Если проблема сохраняется, обратитесь в поддержку.',
                'category': 'technical'
            },
            {
                'question': 'Как предложить новую функцию?',
                'answer': 'Создайте тикет в категории "Запрос функций" и подробно опишите вашу идею.',
                'category': 'feature'
            }
        ]
        
        return jsonify({
            'faq': faq,
            'total': len(faq)
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении FAQ'}), 500

@support_chat_bp.route('/api/support/stats', methods=['GET'])
@login_required
def get_support_stats():
    """Получение статистики поддержки пользователя"""
    try:
        # Общая статистика
        total_tickets = SupportTicket.query.filter_by(user_id=current_user.id).count()
        open_tickets = SupportTicket.query.filter_by(
            user_id=current_user.id,
            status='open'
        ).count()
        closed_tickets = SupportTicket.query.filter_by(
            user_id=current_user.id,
            status='closed'
        ).count()
        
        # Статистика по категориям
        category_stats = {}
        for category in SUPPORT_CATEGORIES.keys():
            count = SupportTicket.query.filter_by(
                user_id=current_user.id,
                category=category
            ).count()
            category_stats[category] = count
        
        # Среднее время ответа
        avg_response_time = calculate_average_response_time(current_user.id)
        
        return jsonify({
            'total_tickets': total_tickets,
            'open_tickets': open_tickets,
            'closed_tickets': closed_tickets,
            'category_stats': category_stats,
            'average_response_time_hours': avg_response_time
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении статистики'}), 500

def calculate_average_response_time(user_id):
    """Расчет среднего времени ответа"""
    try:
        # Получение тикетов с ответами от поддержки
        tickets_with_responses = db.session.query(SupportTicket).join(
            SupportMessage, SupportTicket.id == SupportMessage.ticket_id
        ).filter(
            SupportTicket.user_id == user_id,
            SupportMessage.is_from_support == True
        ).all()
        
        total_response_time = 0
        response_count = 0
        
        for ticket in tickets_with_responses:
            # Первое сообщение пользователя
            first_user_message = SupportMessage.query.filter_by(
                ticket_id=ticket.id,
                is_from_support=False
            ).order_by(SupportMessage.created_at.asc()).first()
            
            # Первый ответ поддержки
            first_support_message = SupportMessage.query.filter_by(
                ticket_id=ticket.id,
                is_from_support=True
            ).order_by(SupportMessage.created_at.asc()).first()
            
            if first_user_message and first_support_message:
                response_time = (first_support_message.created_at - first_user_message.created_at).total_seconds() / 3600  # в часах
                total_response_time += response_time
                response_count += 1
        
        return round(total_response_time / response_count, 2) if response_count > 0 else 0
        
    except Exception as e:
        return 0

def get_support_chat_statistics(user_id):
    """Получение статистики чата поддержки"""
    try:
        total_tickets = SupportTicket.query.filter_by(user_id=user_id).count()
        total_messages = SupportMessage.query.join(
            SupportTicket, SupportMessage.ticket_id == SupportTicket.id
        ).filter(SupportTicket.user_id == user_id).count()
        
        return {
            'total_tickets': total_tickets,
            'total_messages': total_messages,
            'average_messages_per_ticket': round(total_messages / total_tickets, 2) if total_tickets > 0 else 0
        }
    except:
        return {
            'total_tickets': 0,
            'total_messages': 0,
            'average_messages_per_ticket': 0
        }

def get_support_chat_tips():
    """Получение советов по чату поддержки"""
    tips = [
        "Четко опишите проблему в теме тикета",
        "Выберите правильную категорию для быстрого ответа",
        "Приложите скриншоты или логи при необходимости",
        "Проверьте FAQ перед созданием тикета",
        "Отвечайте на вопросы поддержки оперативно",
        "Оценивайте качество поддержки",
        "Используйте поиск по существующим тикетам",
        "Закрывайте решенные тикеты"
    ]
    
    return tips
