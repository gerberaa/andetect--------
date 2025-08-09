# Як зробити внесок у AnDetect Browser

Дякуємо за ваш інтерес до розвитку AnDetect Browser! Цей документ містить інструкції для контрибуторів.

## 📋 Зміст

- [Кодекс поведінки](#кодекс-поведінки)
- [Як допомогти](#як-допомогти)
- [Налаштування середовища розробки](#налаштування-середовища-розробки)
- [Процес розробки](#процес-розробки)
- [Стандарти коду](#стандарти-коду)
- [Тестування](#тестування)
- [Документація](#документація)
- [Створення Pull Request](#створення-pull-request)

## 🤝 Кодекс поведінки

### Наші зобов'язання

Ми зобов'язуємося зробити участь у нашому проекті комфортною для всіх, незалежно від:
- Віку, розміру тіла, інвалідності
- Етнічної приналежності, гендерної ідентичності
- Рівня досвіду, національності
- Зовнішності, раси, релігії
- Сексуальної ідентичності та орієнтації

### Очікувана поведінка

- Використання доброзичливої та інклюзивної мови
- Повага до різних точок зору та досвіду
- Прийняття конструктивної критики
- Зосередженість на тому, що найкраще для спільноти
- Емпатія до інших учасників спільноти

### Неприйнятна поведінка

- Використання сексуалізованої лексики або образів
- Тролінг, образливі коментарі, особисті атаки
- Публічні або приватні домагання
- Публікація приватної інформації без дозволу
- Інша поведінка, неприйнятна в професійному середовищі

## 🚀 Як допомогти

### Звітування про баги

Перед створенням звіту про помилку:
1. Перевірте [існуючі issues](https://github.com/your-username/andetect-browser/issues)
2. Переконайтесь, що ви використовуєте останню версію
3. Перевірте, чи помилка не описана в документації

#### Створення звіту про баг

```markdown
**Опис помилки**
Короткий опис того, що пішло не так.

**Кроки для відтворення**
1. Перейдіть до '...'
2. Натисніть на '...'
3. Прокрутіть до '...'
4. Спостерігайте помилку

**Очікувана поведінка**
Що мало статися.

**Скриншоти**
Додайте скриншоти, якщо це допомагає пояснити проблему.

**Середовище:**
 - OS: [e.g. Windows 11]
 - Python версія: [e.g. 3.11.0]
 - Версія браузера: [e.g. 1.0.0]

**Додаткова інформація**
Будь-яка інша інформація про проблему.
```

### Пропозиції покращень

#### Створення запиту на нову функцію

```markdown
**Чи пов'язана ваша пропозиція з проблемою?**
Опишіть проблему. Ex. Я завжди розчарований коли [...]

**Опишіть рішення, яке ви хочете**
Чіткий опис того, що ви хочете, щоб сталося.

**Опишіть альтернативи**
Опишіть альтернативні рішення або функції.

**Додаткова інформація**
Додайте будь-яку іншу інформацію про пропозицію.
```

### Типи контрибуцій

- **🐛 Виправлення багів** - знаходження та виправлення помилок
- **✨ Нові функції** - додавання нового функціоналу
- **📚 Документація** - покращення документації
- **🧪 Тестування** - написання тестів
- **🎨 UI/UX** - покращення інтерфейсу
- **🔧 Інфраструктура** - налаштування CI/CD, інструментів
- **🌐 Переклади** - локалізація інтерфейсу

## 🛠️ Налаштування середовища розробки

### 1. Fork та клонування

```bash
# Fork репозиторію через GitHub UI
# Потім клонуйте ваш fork
git clone https://github.com/YOUR-USERNAME/andetect-browser.git
cd andetect-browser

# Додайте upstream remote
git remote add upstream https://github.com/original-username/andetect-browser.git
```

### 2. Створення середовища

```bash
# Створення віртуального середовища
python -m venv dev_env
dev_env\Scripts\activate  # Windows
# source dev_env/bin/activate  # Linux/macOS

# Встановлення залежностей
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Якщо є
```

### 3. Встановлення dev інструментів

```bash
# Linting та форматування
pip install black flake8 isort mypy

# Тестування
pip install pytest pytest-cov pytest-qt

# Pre-commit hooks
pip install pre-commit
pre-commit install
```

### 4. Налаштування IDE

#### Visual Studio Code
```json
{
    "python.defaultInterpreterPath": "./dev_env/Scripts/python.exe",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true
}
```

#### PyCharm
1. File → Settings → Project → Python Interpreter
2. Додайте interpreter з `dev_env/Scripts/python.exe`
3. Налаштуйте Code Style → Python → Black

## 🔄 Процес розробки

### 1. Створення гілки

```bash
# Оновлення main гілки
git checkout main
git pull upstream main

# Створення нової гілки
git checkout -b feature/new-feature-name
# або
git checkout -b bugfix/issue-number-description
```

### 2. Конвенції назв гілок

- `feature/описова-назва` - нові функції
- `bugfix/номер-issue-опис` - виправлення багів
- `hotfix/критична-помилка` - критичні виправлення
- `docs/тип-документації` - документація
- `refactor/компонент` - рефакторинг
- `test/тип-тестів` - тести

### 3. Робота з кодом

```bash
# Регулярні коміти
git add .
git commit -m "type: короткий опис змін"

# Синхронізація з upstream
git pull upstream main
git rebase main  # Якщо потрібно
```

### 4. Типи комітів

Використовуємо [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - нова функція
- `fix:` - виправлення багу
- `docs:` - зміни в документації
- `style:` - форматування коду
- `refactor:` - рефакторинг
- `test:` - додавання тестів
- `chore:` - інші зміни

#### Приклади:
```bash
git commit -m "feat: add Tor integration settings dialog"
git commit -m "fix: resolve memory leak in data cleaner"
git commit -m "docs: update installation instructions"
git commit -m "test: add unit tests for privacy manager"
```

## 📏 Стандарти коду

### Python Style Guide

Ми дотримуємося [PEP 8](https://www.python.org/dev/peps/pep-0008/) з деякими доповненнями:

```python
# Імпорти
import os
import sys
from typing import Dict, List, Optional

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QWidget

# Локальні імпорти
from .privacy_protection import PrivacyManager


class ExampleClass(QObject):
    """Приклад класу з документацією."""
    
    signal_example = pyqtSignal(str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.example_attribute = "example"
    
    def example_method(self, param: str) -> bool:
        """
        Приклад методу з документацією.
        
        Args:
            param: Опис параметра
            
        Returns:
            Опис повернутого значення
            
        Raises:
            ValueError: Коли щось йде не так
        """
        if not param:
            raise ValueError("Parameter cannot be empty")
        
        return True
```

### Форматування коду

```bash
# Автоматичне форматування
black *.py
isort *.py

# Перевірка стилю
flake8 *.py
mypy *.py
```

### Конфігурація інструментів

#### pyproject.toml
```toml
[tool.black]
line-length = 88
target-version = ['py38']

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.mypy]
python_version = "3.8"
strict = true
```

## 🧪 Тестування

### Структура тестів

```
tests/
├── unit/
│   ├── test_privacy_protection.py
│   ├── test_tor_integration.py
│   └── test_security_scanner.py
├── integration/
│   ├── test_browser_integration.py
│   └── test_tor_integration.py
└── ui/
    ├── test_main_window.py
    └── test_settings_dialog.py
```

### Написання тестів

```python
import pytest
from unittest.mock import Mock, patch

from andetect_browser.privacy_protection import PrivacyManager


class TestPrivacyManager:
    """Тести для PrivacyManager."""
    
    def setup_method(self):
        """Налаштування для кожного тесту."""
        self.privacy_manager = PrivacyManager()
    
    def test_init(self):
        """Тест ініціалізації."""
        assert self.privacy_manager is not None
        assert hasattr(self.privacy_manager, 'fingerprint_protection')
    
    @patch('andetect_browser.privacy_protection.requests.get')
    def test_update_blocklist(self, mock_get):
        """Тест оновлення списку блокування."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "tracker1.com\ntracker2.com"
        
        result = self.privacy_manager.update_blocklist()
        
        assert result is True
        mock_get.assert_called_once()
    
    def test_block_tracker(self):
        """Тест блокування трекера."""
        tracker_url = "https://analytics.google.com/collect"
        
        result = self.privacy_manager.should_block(tracker_url)
        
        assert result is True
```

### Запуск тестів

```bash
# Всі тести
pytest

# Конкретний файл
pytest tests/unit/test_privacy_protection.py

# З покриттям
pytest --cov=andetect_browser --cov-report=html

# Швидкі тести
pytest -m "not slow"

# UI тести
pytest tests/ui/ --qt-api=pyqt5
```

### Маркування тестів

```python
import pytest

@pytest.mark.slow
def test_tor_connection():
    """Повільний тест з'єднання з Tor."""
    pass

@pytest.mark.network
def test_download_blocklist():
    """Тест, що потребує мережі."""
    pass

@pytest.mark.ui
def test_settings_dialog():
    """UI тест."""
    pass
```

## 📚 Документація

### Docstrings

Використовуємо Google style docstrings:

```python
def complex_function(param1: str, param2: int = 10) -> Dict[str, Any]:
    """
    Виконує складну операцію.
    
    Args:
        param1: Опис першого параметра
        param2: Опис другого параметра. Defaults to 10.
        
    Returns:
        Словник з результатами операції, що містить:
            - 'success': bool, чи успішна операція
            - 'data': Any, дані результату
            
    Raises:
        ValueError: Якщо param1 порожній
        ConnectionError: Якщо не вдається підключитися
        
    Example:
        >>> result = complex_function("test", 20)
        >>> print(result['success'])
        True
    """
    pass
```

### Коментарі

```python
# TODO: Додати підтримку IPv6
# FIXME: Виправити memory leak у цій функції
# NOTE: Цей код працює тільки на Windows
# HACK: Тимчасове рішення до версії 2.0

def example_function():
    # Перевірка валідності даних
    if not data:
        return False
    
    # Складна логіка, що потребує пояснення
    # Тут ми робимо X тому що Y
    result = complex_calculation(data)
    
    return result
```

## 📝 Створення Pull Request

### 1. Підготовка

```bash
# Переконайтесь, що всі тести проходять
pytest

# Форматування коду
black .
isort .

# Перевірка lint
flake8 .
mypy .

# Оновлення документації (якщо потрібно)
# Додавання записів в CHANGELOG.md
```

### 2. Push змін

```bash
git push origin feature/your-feature-name
```

### 3. Створення PR

#### Шаблон PR

```markdown
## Опис

Короткий опис того, що робить цей PR.

## Тип змін

- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)  
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Як тестувати

1. Крок 1
2. Крок 2
3. Крок 3

## Чеклист

- [ ] Мій код дотримується стандартів проекту
- [ ] Я провів самостійний огляд коду
- [ ] Я прокоментував код в складних місцях
- [ ] Я оновив документацію
- [ ] Мої зміни не генерують нових попереджень
- [ ] Я додав тести, що підтверджують ефективність моїх змін
- [ ] Нові та існуючі unit тести проходять локально
- [ ] Я оновив CHANGELOG.md

## Скриншоти (якщо є UI зміни)

Додайте скриншоти до/після.

## Додаткові нотатки

Будь-яка додаткова інформація для ревьюерів.
```

### 4. Code Review Process

#### Для автора PR:
- Відповідайте на коментарі протягом 48 годин
- Вносьте зміни в тій же гілці
- Позначайте conversations як resolved після виправлення

#### Для ревьюерів:
- Надавайте конструктивний фідбек
- Перевіряйте функціональність, не тільки код
- Тестуйте зміни локально для великих PR

## 🔧 Інструменти розробки

### Pre-commit Hooks

`.pre-commit-config.yaml`:
```yaml
repos:
-   repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
    -   id: black
        language_version: python3

-   repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
    -   id: isort

-   repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
    -   id: flake8

-   repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
    -   id: mypy
```

### Makefile

```makefile
.PHONY: install test lint format clean

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=andetect_browser --cov-report=html

lint:
	flake8 andetect_browser/
	mypy andetect_browser/

format:
	black andetect_browser/ tests/
	isort andetect_browser/ tests/

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/
```

## 📞 Отримання допомоги

- **GitHub Issues** - для запитань про розробку
- **Discussions** - для загальних дискусій
- **Discord/Telegram** - для швидкої допомоги (якщо є)
- **Email** - dev@andetect-browser.com

## 🎉 Визнання контрибуторів

Усі контрибутори додаються до:
- AUTHORS.md файлу
- GitHub contributors page
- Release notes для значних внесків

Дякуємо за ваш внесок у AnDetect Browser! 🚀
