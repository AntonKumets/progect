import pytest
import sqlite3
import os
from registration.registration import create_db, add_user, authenticate_user, display_users

@pytest.fixture(scope="module")
def setup_database():
    """Фикстура для настройки базы данных перед тестами и её очистки после."""
    create_db()
    yield
    try:
        os.remove('users.db')
    except PermissionError:
        pass

@pytest.fixture
def connection():
    """Фикстура для получения соединения с базой данных и его закрытия после теста."""
    conn = sqlite3.connect('users.db')
    yield conn
    conn.close()


def test_create_db(setup_database, connection):
    """Тест создания базы данных и таблицы пользователей."""
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists, "Таблица 'users' должна существовать в базе данных."

def test_add_new_user(setup_database, connection):
    """Тест добавления нового пользователя."""
    add_user('testuser', 'testuser@example.com', 'password123')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert user

def test_add_existing_user(setup_database, connection):
    add_user('existinguser', 'existing@example.com', 'pass1')
    add_user('existinguser', 'existing@example.com', 'pass2')
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE username='existinguser';")
    count = cursor.fetchone()[0]
    assert count == 1

def test_authenticate_success(setup_database, connection):
    add_user('authuser', 'auth@example.com', 'correctpassword')
    assert authenticate_user('authuser', 'correctpassword') is True

def test_authenticate_nonexistent_user(setup_database, connection):
    assert authenticate_user('ghostuser', 'anypass') is False

def test_authenticate_wrong_password(setup_database, connection):
    add_user('wronguser', 'wrong@example.com', 'realpassword')
    assert authenticate_user('wronguser', 'wrongpassword') is False

def test_display_users(setup_database, connection, capsys):
    add_user('display1', 'disp1@example.com', 'pwd1')
    add_user('display2', 'disp2@example.com', 'pwd2')
    display_users()
    captured = capsys.readouterr()
    assert 'display1' in captured.out
    assert 'display2' in captured.out


"""
Тест добавления пользователя с существующим логином.
Тест успешной аутентификации пользователя.
Тест аутентификации несуществующего пользователя.
Тест аутентификации пользователя с неправильным паролем.
Тест отображения списка пользователей.
"""