# Desafio Django REST Framework

![Python](https://img.shields.io/badge/python-3.12-blue)
![Django](https://img.shields.io/badge/django-3.1.7-green)
![Django REST Framework](https://img.shields.io/badge/djangorestframework-3.14.0-brightgreen)

Aplicação web construída com Django e Django REST Framework para gerenciamento de **usuários, pedidos e itens de catálogo**, com controle de permissões baseado em grupos (Clientes, Funcionários e Gerência).

---

## Funcionalidades

### Usuários
- Registro de clientes via `/api/users/signup/`
- CRUD completo para Funcionários e Gerência
- Visualização parcial de dados para Clientes

### Pedidos
- Clientes criam e visualizam apenas seus pedidos
- Funcionários gerenciam pedidos de qualquer cliente
- Gerência tem acesso total
- Controle automático de estoque
- Retorno com valor total do pedido

### Itens do Catálogo
- Lista pública resumida para Clientes
- Criação, atualização e exclusão para Funcionário/Gerência
- Filtros por preço, busca por nome/descrição, ordenação

---

## Tecnologias

- Python 3.12
- Django 5.2.5
- Django REST Framework 3.16.1

---

## Instalação

```bash
git clone <git@github.com:JesseJunior28/desafio_djangorf.git>
cd desafio_djangorf
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver