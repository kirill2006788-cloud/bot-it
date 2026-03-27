from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import json
import yaml
from datetime import datetime
import re

api_doc_bp = Blueprint('api_doc', __name__)

@api_doc_benerator.route('/api/api-doc/generate', methods=['POST'])
@login_required
def generate_api_documentation():
    """Генерация API документации"""
    try:
        data = request.get_json()
        
        # Параметры API
        api_name = data.get('api_name', 'My API')
        version = data.get('version', '1.0.0')
        description = data.get('description', 'API для моего проекта')
        base_url = data.get('base_url', 'https://api.example.com')
        endpoints = data.get('endpoints', [])
        format_type = data.get('format', 'swagger')  # swagger, openapi, postman
        
        if not endpoints:
            return jsonify({'error': 'Необходимо указать хотя бы один endpoint'}), 400
        
        # Генерация документации
        if format_type == 'swagger':
            doc_content = generate_swagger_doc(api_name, version, description, base_url, endpoints)
        elif format_type == 'openapi':
            doc_content = generate_openapi_doc(api_name, version, description, base_url, endpoints)
        elif format_type == 'postman':
            doc_content = generate_postman_collection(api_name, description, endpoints)
        else:
            return jsonify({'error': 'Неподдерживаемый формат'}), 400
        
        return jsonify({
            'documentation': doc_content,
            'format': format_type,
            'api_name': api_name,
            'version': version,
            'endpoints_count': len(endpoints),
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при генерации API документации'}), 500

@api_doc_bp.route('/api/api-doc/templates', methods=['GET'])
def get_api_doc_templates():
    """Получение шаблонов API документации"""
    try:
        templates = {
            'formats': {
                'swagger': {
                    'name': 'Swagger/OpenAPI 2.0',
                    'description': 'Стандартный формат Swagger',
                    'extension': 'json'
                },
                'openapi': {
                    'name': 'OpenAPI 3.0',
                    'description': 'Современный формат OpenAPI',
                    'extension': 'yaml'
                },
                'postman': {
                    'name': 'Postman Collection',
                    'description': 'Коллекция для Postman',
                    'extension': 'json'
                }
            },
            'endpoint_templates': [
                {
                    'path': '/users',
                    'method': 'GET',
                    'description': 'Получение списка пользователей',
                    'parameters': [
                        {'name': 'page', 'type': 'integer', 'description': 'Номер страницы'},
                        {'name': 'limit', 'type': 'integer', 'description': 'Количество элементов на странице'}
                    ],
                    'responses': [
                        {'code': 200, 'description': 'Успешный ответ', 'schema': 'UserList'}
                    ]
                },
                {
                    'path': '/users/{id}',
                    'method': 'GET',
                    'description': 'Получение пользователя по ID',
                    'parameters': [
                        {'name': 'id', 'type': 'integer', 'description': 'ID пользователя', 'required': True}
                    ],
                    'responses': [
                        {'code': 200, 'description': 'Пользователь найден', 'schema': 'User'},
                        {'code': 404, 'description': 'Пользователь не найден'}
                    ]
                },
                {
                    'path': '/users',
                    'method': 'POST',
                    'description': 'Создание нового пользователя',
                    'parameters': [
                        {'name': 'body', 'type': 'object', 'description': 'Данные пользователя', 'required': True}
                    ],
                    'responses': [
                        {'code': 201, 'description': 'Пользователь создан', 'schema': 'User'},
                        {'code': 400, 'description': 'Неверные данные'}
                    ]
                }
            ],
            'data_models': {
                'User': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'description': 'Уникальный идентификатор'},
                        'name': {'type': 'string', 'description': 'Имя пользователя'},
                        'email': {'type': 'string', 'format': 'email', 'description': 'Email адрес'},
                        'created_at': {'type': 'string', 'format': 'date-time', 'description': 'Дата создания'}
                    }
                },
                'UserList': {
                    'type': 'object',
                    'properties': {
                        'users': {'type': 'array', 'items': {'$ref': '#/definitions/User'}},
                        'total': {'type': 'integer', 'description': 'Общее количество пользователей'},
                        'page': {'type': 'integer', 'description': 'Текущая страница'}
                    }
                }
            }
        }
        
        return jsonify({'templates': templates})
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении шаблонов'}), 500

@api_doc_bp.route('/api/api-doc/validate', methods=['POST'])
@login_required
def validate_api_documentation():
    """Валидация API документации"""
    try:
        data = request.get_json()
        doc_content = data.get('documentation', '')
        format_type = data.get('format', 'swagger')
        
        if not doc_content:
            return jsonify({'error': 'Документация не предоставлена'}), 400
        
        # Валидация документации
        validation_result = validate_documentation(doc_content, format_type)
        
        return jsonify({
            'valid': validation_result['valid'],
            'errors': validation_result.get('errors', []),
            'warnings': validation_result.get('warnings', []),
            'format': format_type
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при валидации документации'}), 500

def generate_swagger_doc(api_name, version, description, base_url, endpoints):
    """Генерация Swagger документации"""
    swagger_doc = {
        'swagger': '2.0',
        'info': {
            'title': api_name,
            'version': version,
            'description': description,
            'contact': {
                'name': 'API Support',
                'email': current_user.email
            }
        },
        'host': base_url.replace('https://', '').replace('http://', ''),
        'basePath': '/',
        'schemes': ['https', 'http'],
        'consumes': ['application/json'],
        'produces': ['application/json'],
        'paths': {},
        'definitions': {}
    }
    
    # Генерация путей
    for endpoint in endpoints:
        path = endpoint.get('path', '/')
        method = endpoint.get('method', 'GET').lower()
        description = endpoint.get('description', '')
        parameters = endpoint.get('parameters', [])
        responses = endpoint.get('responses', [])
        
        if path not in swagger_doc['paths']:
            swagger_doc['paths'][path] = {}
        
        endpoint_def = {
            'summary': description,
            'description': description,
            'parameters': [],
            'responses': {}
        }
        
        # Параметры
        for param in parameters:
            param_def = {
                'name': param.get('name', ''),
                'in': param.get('in', 'query'),
                'description': param.get('description', ''),
                'required': param.get('required', False),
                'type': param.get('type', 'string')
            }
            
            if param.get('schema'):
                param_def['schema'] = {'$ref': f'#/definitions/{param["schema"]}'}
            
            endpoint_def['parameters'].append(param_def)
        
        # Ответы
        for response in responses:
            response_def = {
                'description': response.get('description', '')
            }
            
            if response.get('schema'):
                response_def['schema'] = {'$ref': f'#/definitions/{response["schema"]}'}
            
            endpoint_def['responses'][str(response.get('code', 200))] = response_def
        
        swagger_doc['paths'][path][method] = endpoint_def
    
    return json.dumps(swagger_doc, indent=2, ensure_ascii=False)

def generate_openapi_doc(api_name, version, description, base_url, endpoints):
    """Генерация OpenAPI 3.0 документации"""
    openapi_doc = {
        'openapi': '3.0.0',
        'info': {
            'title': api_name,
            'version': version,
            'description': description,
            'contact': {
                'name': 'API Support',
                'email': current_user.email
            }
        },
        'servers': [
            {'url': base_url, 'description': 'Production server'}
        ],
        'paths': {},
        'components': {
            'schemas': {}
        }
    }
    
    # Генерация путей
    for endpoint in endpoints:
        path = endpoint.get('path', '/')
        method = endpoint.get('method', 'GET').lower()
        description = endpoint.get('description', '')
        parameters = endpoint.get('parameters', [])
        responses = endpoint.get('responses', [])
        
        if path not in openapi_doc['paths']:
            openapi_doc['paths'][path] = {}
        
        endpoint_def = {
            'summary': description,
            'description': description,
            'parameters': [],
            'responses': {}
        }
        
        # Параметры
        for param in parameters:
            param_def = {
                'name': param.get('name', ''),
                'in': param.get('in', 'query'),
                'description': param.get('description', ''),
                'required': param.get('required', False),
                'schema': {'type': param.get('type', 'string')}
            }
            
            endpoint_def['parameters'].append(param_def)
        
        # Ответы
        for response in responses:
            response_def = {
                'description': response.get('description', ''),
                'content': {
                    'application/json': {
                        'schema': {'type': 'object'}
                    }
                }
            }
            
            endpoint_def['responses'][str(response.get('code', 200))] = response_def
        
        openapi_doc['paths'][path][method] = endpoint_def
    
    return yaml.dump(openapi_doc, default_flow_style=False, allow_unicode=True)

def generate_postman_collection(api_name, description, endpoints):
    """Генерация Postman коллекции"""
    collection = {
        'info': {
            'name': api_name,
            'description': description,
            'schema': 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'
        },
        'item': []
    }
    
    # Генерация запросов
    for endpoint in endpoints:
        path = endpoint.get('path', '/')
        method = endpoint.get('method', 'GET')
        description = endpoint.get('description', '')
        parameters = endpoint.get('parameters', [])
        
        request_item = {
            'name': f'{method} {path}',
            'request': {
                'method': method,
                'header': [
                    {
                        'key': 'Content-Type',
                        'value': 'application/json'
                    }
                ],
                'url': {
                    'raw': '{{base_url}}' + path,
                    'host': ['{{base_url}}'],
                    'path': path.split('/')[1:] if path != '/' else []
                },
                'description': description
            }
        }
        
        # Добавление параметров
        if parameters:
            query_params = []
            path_vars = []
            
            for param in parameters:
                param_location = param.get('in', 'query')
                
                if param_location == 'query':
                    query_params.append({
                        'key': param.get('name', ''),
                        'value': '',
                        'description': param.get('description', '')
                    })
                elif param_location == 'path':
                    path_vars.append({
                        'key': param.get('name', ''),
                        'value': '',
                        'description': param.get('description', '')
                    })
            
            if query_params:
                request_item['request']['url']['query'] = query_params
        
        collection['item'].append(request_item)
    
    return json.dumps(collection, indent=2, ensure_ascii=False)

def validate_documentation(doc_content, format_type):
    """Валидация API документации"""
    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    try:
        if format_type == 'swagger':
            doc = json.loads(doc_content)
            
            # Проверка обязательных полей
            required_fields = ['swagger', 'info', 'paths']
            for field in required_fields:
                if field not in doc:
                    validation_result['errors'].append(f'Отсутствует обязательное поле: {field}')
                    validation_result['valid'] = False
            
            # Проверка версии Swagger
            if doc.get('swagger') != '2.0':
                validation_result['warnings'].append('Рекомендуется использовать Swagger 2.0')
            
            # Проверка путей
            if 'paths' in doc:
                for path, methods in doc['paths'].items():
                    if not methods:
                        validation_result['warnings'].append(f'Путь {path} не содержит методов')
                    
                    for method, definition in methods.items():
                        if 'responses' not in definition:
                            validation_result['errors'].append(f'Метод {method} для пути {path} не содержит responses')
                            validation_result['valid'] = False
        
        elif format_type == 'openapi':
            doc = yaml.safe_load(doc_content)
            
            # Проверка обязательных полей
            required_fields = ['openapi', 'info', 'paths']
            for field in required_fields:
                if field not in doc:
                    validation_result['errors'].append(f'Отсутствует обязательное поле: {field}')
                    validation_result['valid'] = False
            
            # Проверка версии OpenAPI
            if doc.get('openapi') != '3.0.0':
                validation_result['warnings'].append('Рекомендуется использовать OpenAPI 3.0.0')
        
        elif format_type == 'postman':
            doc = json.loads(doc_content)
            
            # Проверка обязательных полей
            required_fields = ['info', 'item']
            for field in required_fields:
                if field not in doc:
                    validation_result['errors'].append(f'Отсутствует обязательное поле: {field}')
                    validation_result['valid'] = False
            
            # Проверка элементов коллекции
            if 'item' in doc and not doc['item']:
                validation_result['warnings'].append('Коллекция не содержит запросов')
        
        else:
            validation_result['errors'].append(f'Неподдерживаемый формат: {format_type}')
            validation_result['valid'] = False
    
    except json.JSONDecodeError as e:
        validation_result['errors'].append(f'Ошибка JSON: {str(e)}')
        validation_result['valid'] = False
    except yaml.YAMLError as e:
        validation_result['errors'].append(f'Ошибка YAML: {str(e)}')
        validation_result['valid'] = False
    except Exception as e:
        validation_result['errors'].append(f'Ошибка валидации: {str(e)}')
        validation_result['valid'] = False
    
    return validation_result

def generate_endpoint_template(method, path, description):
    """Генерация шаблона endpoint"""
    return {
        'path': path,
        'method': method,
        'description': description,
        'parameters': [],
        'responses': [
            {
                'code': 200,
                'description': 'Успешный ответ'
            }
        ]
    }

def add_parameter_template(endpoint, name, param_type, description, required=False, location='query'):
    """Добавление параметра к endpoint"""
    parameter = {
        'name': name,
        'type': param_type,
        'description': description,
        'required': required,
        'in': location
    }
    
    endpoint['parameters'].append(parameter)
    return endpoint

def add_response_template(endpoint, code, description, schema=None):
    """Добавление ответа к endpoint"""
    response = {
        'code': code,
        'description': description
    }
    
    if schema:
        response['schema'] = schema
    
    endpoint['responses'].append(response)
    return endpoint

def generate_crud_endpoints(resource_name, base_path):
    """Генерация CRUD endpoints для ресурса"""
    endpoints = []
    
    # GET /resource - список ресурсов
    endpoints.append(generate_endpoint_template(
        'GET', base_path, f'Получение списка {resource_name}'
    ))
    
    # GET /resource/{id} - получение ресурса
    endpoints.append(generate_endpoint_template(
        'GET', f'{base_path}/{{id}}', f'Получение {resource_name} по ID'
    ))
    
    # POST /resource - создание ресурса
    endpoints.append(generate_endpoint_template(
        'POST', base_path, f'Создание нового {resource_name}'
    ))
    
    # PUT /resource/{id} - обновление ресурса
    endpoints.append(generate_endpoint_template(
        'PUT', f'{base_path}/{{id}}', f'Обновление {resource_name}'
    ))
    
    # DELETE /resource/{id} - удаление ресурса
    endpoints.append(generate_endpoint_template(
        'DELETE', f'{base_path}/{{id}}', f'Удаление {resource_name}'
    ))
    
    return endpoints
