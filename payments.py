from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, User, Payment, Subscription, Plan
import stripe
import json
from datetime import datetime, timedelta
import uuid

payments_bp = Blueprint('payments', __name__)

# Настройка Stripe
stripe.api_key = "sk_test_your_stripe_secret_key"

# Тарифные планы
SUBSCRIPTION_PLANS = {
    'free': {
        'name': 'Бесплатный',
        'price': 0,
        'currency': 'rub',
        'interval': 'month',
        'features': [
            'Базовые инструменты',
            '5 игр в день',
            'Ограниченная аналитика',
            'Поддержка по email'
        ],
        'limits': {
            'api_calls_per_month': 1000,
            'games_per_day': 5,
            'storage_mb': 100
        }
    },
    'pro': {
        'name': 'Pro',
        'price': 999,
        'currency': 'rub',
        'interval': 'month',
        'features': [
            'Все инструменты',
            'Неограниченные игры',
            'Расширенная аналитика',
            'Приоритетная поддержка',
            'API доступ',
            'Экспорт данных'
        ],
        'limits': {
            'api_calls_per_month': 10000,
            'games_per_day': -1,  # неограниченно
            'storage_mb': 1000
        }
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': 4999,
        'currency': 'rub',
        'interval': 'month',
        'features': [
            'Все функции Pro',
            'Персональный менеджер',
            'Кастомные интеграции',
            'SLA 99.9%',
            'Безлимитный API',
            'Приоритетная разработка'
        ],
        'limits': {
            'api_calls_per_month': -1,  # неограниченно
            'games_per_day': -1,
            'storage_mb': -1
        }
    }
}

@payments_bp.route('/api/payments/plans', methods=['GET'])
def get_subscription_plans():
    """Получение доступных тарифных планов"""
    try:
        return jsonify({
            'plans': SUBSCRIPTION_PLANS,
            'current_plan': get_user_current_plan(current_user.id) if current_user.is_authenticated else None
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении тарифных планов'}), 500

@payments_bp.route('/api/payments/subscribe', methods=['POST'])
@login_required
def create_subscription():
    """Создание подписки"""
    try:
        data = request.get_json()
        plan_id = data.get('plan_id', '')
        payment_method_id = data.get('payment_method_id', '')
        
        if not plan_id or plan_id not in SUBSCRIPTION_PLANS:
            return jsonify({'error': 'Неверный тарифный план'}), 400
        
        plan = SUBSCRIPTION_PLANS[plan_id]
        
        # Проверка, есть ли уже активная подписка
        existing_subscription = Subscription.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).first()
        
        if existing_subscription:
            return jsonify({'error': 'У вас уже есть активная подписка'}), 400
        
        # Создание подписки в Stripe
        if plan['price'] > 0:
            stripe_subscription = stripe.Subscription.create(
                customer=current_user.stripe_customer_id or create_stripe_customer(),
                items=[{
                    'price_data': {
                        'currency': plan['currency'],
                        'product_data': {
                            'name': plan['name'],
                        },
                        'unit_amount': plan['price'] * 100,  # в копейках
                        'recurring': {
                            'interval': plan['interval'],
                        },
                    },
                }],
                payment_behavior='default_incomplete',
                payment_settings={'save_default_payment_method': 'on_subscription'},
                expand=['latest_invoice.payment_intent'],
            )
            
            subscription_id = stripe_subscription.id
            client_secret = stripe_subscription.latest_invoice.payment_intent.client_secret
        else:
            # Бесплатный план
            subscription_id = f"free_{current_user.id}_{uuid.uuid4().hex[:8]}"
            client_secret = None
        
        # Создание подписки в базе данных
        subscription = Subscription(
            user_id=current_user.id,
            plan_id=plan_id,
            stripe_subscription_id=subscription_id,
            status='pending' if plan['price'] > 0 else 'active',
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30),
            created_at=datetime.utcnow()
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        return jsonify({
            'subscription_id': subscription.id,
            'stripe_subscription_id': subscription_id,
            'client_secret': client_secret,
            'plan': plan,
            'status': subscription.status
        })
        
    except stripe.error.StripeError as e:
        return jsonify({'error': f'Ошибка Stripe: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при создании подписки'}), 500

@payments_bp.route('/api/payments/subscription/<int:subscription_id>', methods=['GET'])
@login_required
def get_subscription(subscription_id):
    """Получение информации о подписке"""
    try:
        subscription = Subscription.query.filter_by(
            id=subscription_id,
            user_id=current_user.id
        ).first()
        
        if not subscription:
            return jsonify({'error': 'Подписка не найдена'}), 404
        
        plan = SUBSCRIPTION_PLANS.get(subscription.plan_id, {})
        
        return jsonify({
            'id': subscription.id,
            'plan_id': subscription.plan_id,
            'plan_name': plan.get('name', ''),
            'status': subscription.status,
            'current_period_start': subscription.current_period_start.isoformat(),
            'current_period_end': subscription.current_period_end.isoformat(),
            'created_at': subscription.created_at.isoformat(),
            'features': plan.get('features', []),
            'limits': plan.get('limits', {})
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении подписки'}), 500

@payments_bp.route('/api/payments/subscription/<int:subscription_id>/cancel', methods=['POST'])
@login_required
def cancel_subscription(subscription_id):
    """Отмена подписки"""
    try:
        subscription = Subscription.query.filter_by(
            id=subscription_id,
            user_id=current_user.id
        ).first()
        
        if not subscription:
            return jsonify({'error': 'Подписка не найдена'}), 404
        
        if subscription.status != 'active':
            return jsonify({'error': 'Подписка не активна'}), 400
        
        # Отмена в Stripe
        if subscription.stripe_subscription_id:
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=True
            )
        
        # Обновление статуса
        subscription.status = 'cancelled'
        subscription.cancelled_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Подписка отменена',
            'cancelled_at': subscription.cancelled_at.isoformat()
        })
        
    except stripe.error.StripeError as e:
        return jsonify({'error': f'Ошибка Stripe: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при отмене подписки'}), 500

@payments_bp.route('/api/payments/subscription/<int:subscription_id>/reactivate', methods=['POST'])
@login_required
def reactivate_subscription(subscription_id):
    """Реактивация подписки"""
    try:
        subscription = Subscription.query.filter_by(
            id=subscription_id,
            user_id=current_user.id
        ).first()
        
        if not subscription:
            return jsonify({'error': 'Подписка не найдена'}), 404
        
        if subscription.status != 'cancelled':
            return jsonify({'error': 'Подписка не отменена'}), 400
        
        # Реактивация в Stripe
        if subscription.stripe_subscription_id:
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=False
            )
        
        # Обновление статуса
        subscription.status = 'active'
        subscription.cancelled_at = None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Подписка реактивирована',
            'status': subscription.status
        })
        
    except stripe.error.StripeError as e:
        return jsonify({'error': f'Ошибка Stripe: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при реактивации подписки'}), 500

@payments_bp.route('/api/payments/invoices', methods=['GET'])
@login_required
def get_invoices():
    """Получение счетов пользователя"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Получение подписок пользователя
        subscriptions = Subscription.query.filter_by(user_id=current_user.id).all()
        
        invoices = []
        for subscription in subscriptions:
            if subscription.stripe_subscription_id:
                try:
                    stripe_invoices = stripe.Invoice.list(
                        subscription=subscription.stripe_subscription_id,
                        limit=per_page
                    )
                    
                    for invoice in stripe_invoices.data:
                        invoices.append({
                            'id': invoice.id,
                            'subscription_id': subscription.id,
                            'amount': invoice.amount_paid,
                            'currency': invoice.currency,
                            'status': invoice.status,
                            'created': datetime.fromtimestamp(invoice.created).isoformat(),
                            'invoice_url': invoice.invoice_pdf
                        })
                except stripe.error.StripeError:
                    continue
        
        # Сортировка по дате создания
        invoices.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({
            'invoices': invoices,
            'total': len(invoices)
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении счетов'}), 500

@payments_bp.route('/api/payments/webhook', methods=['POST'])
def stripe_webhook():
    """Webhook для обработки событий Stripe"""
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Stripe-Signature')
        
        # Верификация webhook
        event = stripe.Webhook.construct_event(
            payload, sig_header, 'whsec_your_webhook_secret'
        )
        
        # Обработка событий
        if event['type'] == 'invoice.payment_succeeded':
            handle_payment_succeeded(event['data']['object'])
        elif event['type'] == 'invoice.payment_failed':
            handle_payment_failed(event['data']['object'])
        elif event['type'] == 'customer.subscription.updated':
            handle_subscription_updated(event['data']['object'])
        elif event['type'] == 'customer.subscription.deleted':
            handle_subscription_deleted(event['data']['object'])
        
        return jsonify({'status': 'success'})
        
    except ValueError as e:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify({'error': 'Invalid signature'}), 400
    except Exception as e:
        return jsonify({'error': 'Webhook error'}), 500

@payments_bp.route('/api/payments/usage', methods=['GET'])
@login_required
def get_usage_stats():
    """Получение статистики использования"""
    try:
        subscription = get_user_active_subscription(current_user.id)
        if not subscription:
            return jsonify({'error': 'Нет активной подписки'}), 400
        
        plan = SUBSCRIPTION_PLANS.get(subscription.plan_id, {})
        limits = plan.get('limits', {})
        
        # Получение текущего использования
        current_usage = get_current_usage(current_user.id)
        
        return jsonify({
            'plan': plan,
            'limits': limits,
            'current_usage': current_usage,
            'usage_percentage': calculate_usage_percentage(current_usage, limits)
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении статистики'}), 500

def create_stripe_customer():
    """Создание клиента в Stripe"""
    try:
        customer = stripe.Customer.create(
            email=current_user.email,
            name=current_user.username,
            metadata={
                'user_id': current_user.id
            }
        )
        
        # Сохранение ID клиента
        current_user.stripe_customer_id = customer.id
        db.session.commit()
        
        return customer.id
        
    except Exception as e:
        return None

def get_user_current_plan(user_id):
    """Получение текущего плана пользователя"""
    try:
        subscription = get_user_active_subscription(user_id)
        if subscription:
            return SUBSCRIPTION_PLANS.get(subscription.plan_id, SUBSCRIPTION_PLANS['free'])
        return SUBSCRIPTION_PLANS['free']
    except:
        return SUBSCRIPTION_PLANS['free']

def get_user_active_subscription(user_id):
    """Получение активной подписки пользователя"""
    return Subscription.query.filter_by(
        user_id=user_id,
        status='active'
    ).first()

def get_current_usage(user_id):
    """Получение текущего использования"""
    # Здесь можно добавить логику подсчета использования
    return {
        'api_calls_this_month': 0,
        'games_this_day': 0,
        'storage_used_mb': 0
    }

def calculate_usage_percentage(current_usage, limits):
    """Расчет процента использования"""
    percentages = {}
    
    for key, limit in limits.items():
        if limit == -1:  # неограниченно
            percentages[key] = 0
        else:
            current = current_usage.get(key, 0)
            percentages[key] = min((current / limit) * 100, 100)
    
    return percentages

def handle_payment_succeeded(invoice):
    """Обработка успешного платежа"""
    try:
        subscription_id = invoice.subscription
        subscription = Subscription.query.filter_by(
            stripe_subscription_id=subscription_id
        ).first()
        
        if subscription:
            subscription.status = 'active'
            db.session.commit()
            
            # Создание записи о платеже
            payment = Payment(
                user_id=subscription.user_id,
                subscription_id=subscription.id,
                amount=invoice.amount_paid / 100,  # конвертация из копеек
                currency=invoice.currency,
                stripe_payment_intent_id=invoice.payment_intent,
                status='succeeded',
                created_at=datetime.fromtimestamp(invoice.created)
            )
            
            db.session.add(payment)
            db.session.commit()
            
    except Exception as e:
        db.session.rollback()

def handle_payment_failed(invoice):
    """Обработка неудачного платежа"""
    try:
        subscription_id = invoice.subscription
        subscription = Subscription.query.filter_by(
            stripe_subscription_id=subscription_id
        ).first()
        
        if subscription:
            subscription.status = 'past_due'
            db.session.commit()
            
    except Exception as e:
        db.session.rollback()

def handle_subscription_updated(subscription_data):
    """Обработка обновления подписки"""
    try:
        subscription = Subscription.query.filter_by(
            stripe_subscription_id=subscription_data['id']
        ).first()
        
        if subscription:
            subscription.status = subscription_data['status']
            subscription.current_period_start = datetime.fromtimestamp(
                subscription_data['current_period_start']
            )
            subscription.current_period_end = datetime.fromtimestamp(
                subscription_data['current_period_end']
            )
            db.session.commit()
            
    except Exception as e:
        db.session.rollback()

def handle_subscription_deleted(subscription_data):
    """Обработка удаления подписки"""
    try:
        subscription = Subscription.query.filter_by(
            stripe_subscription_id=subscription_data['id']
        ).first()
        
        if subscription:
            subscription.status = 'cancelled'
            subscription.cancelled_at = datetime.utcnow()
            db.session.commit()
            
    except Exception as e:
        db.session.rollback()

def get_payment_statistics(user_id):
    """Получение статистики платежей"""
    try:
        total_payments = Payment.query.filter_by(user_id=user_id).count()
        total_amount = db.session.query(
            db.func.sum(Payment.amount)
        ).filter_by(user_id=user_id).scalar() or 0
        
        return {
            'total_payments': total_payments,
            'total_amount': total_amount,
            'currency': 'RUB'
        }
    except:
        return {
            'total_payments': 0,
            'total_amount': 0,
            'currency': 'RUB'
        }

def get_payment_tips():
    """Получение советов по платежам"""
    tips = [
        "Выберите подходящий тарифный план",
        "Регулярно проверяйте статистику использования",
        "Настройте уведомления о платежах",
        "Сохраняйте квитанции об оплате",
        "Используйте безопасные способы оплаты",
        "Следите за истечением подписки",
        "Обращайтесь в поддержку при проблемах",
        "Рассмотрите годовые планы для экономии"
    ]
    
    return tips
