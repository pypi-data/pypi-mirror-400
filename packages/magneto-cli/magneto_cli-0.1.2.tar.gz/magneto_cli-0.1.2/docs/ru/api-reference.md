# Справочник API

Этот документ описывает Python API Magneto, подходит для разработчиков, которым нужно интегрировать функциональность Magneto в свой код.

## Основные модули

### TorrentConverter

`magneto.core.TorrentConverter` — это основной класс преобразования, отвечающий за преобразование торрент-файлов в магнитные ссылки.

#### Инициализация

```python
from magneto.core import TorrentConverter

converter = TorrentConverter()
```

#### Методы

##### `read_torrent_file(torrent_path: Path) -> bytes`

Читает содержимое торрент-файла.

**Параметры:**
- `torrent_path` (Path): Путь к торрент-файлу

**Возвращает:**
- `bytes`: Двоичное содержимое файла

**Вызывает:**
- `IOError`: Ошибка чтения файла

**Пример:**
```python
from pathlib import Path

data = converter.read_torrent_file(Path("example.torrent"))
```

##### `parse_torrent(torrent_data: bytes) -> Dict`

Парсит данные торрент-файла.

**Параметры:**
- `torrent_data` (bytes): Двоичные данные торрент-файла

**Возвращает:**
- `Dict`: Словарь распарсенных данных торрента

**Вызывает:**
- `ValueError`: Ошибка формата торрент-файла

**Пример:**
```python
torrent_data = converter.parse_torrent(data)
```

##### `get_info_hash(torrent_data: Dict) -> str`

Извлекает Info Hash из данных торрента.

**Параметры:**
- `torrent_data` (Dict): Словарь распарсенных данных торрента

**Возвращает:**
- `str`: Info Hash в виде шестнадцатеричной строки (верхний регистр)

**Вызывает:**
- `ValueError`: В данных торрента отсутствует поле info

**Пример:**
```python
info_hash = converter.get_info_hash(torrent_data)
# Вывод: "ABC123DEF456..."
```

##### `get_torrent_name(torrent_data: Dict) -> Optional[str]`

Извлекает имя файла из данных торрента.

**Параметры:**
- `torrent_data` (Dict): Словарь распарсенных данных торрента

**Возвращает:**
- `Optional[str]`: Имя файла или None, если отсутствует

**Пример:**
```python
name = converter.get_torrent_name(torrent_data)
# Вывод: "Example File"
```

##### `get_trackers(torrent_data: Dict) -> list`

Извлекает список трекеров из данных торрента.

**Параметры:**
- `torrent_data` (Dict): Словарь распарсенных данных торрента

**Возвращает:**
- `list`: Список URL трекеров

**Пример:**
```python
trackers = converter.get_trackers(torrent_data)
# Вывод: ["http://tracker1.example.com", "http://tracker2.example.com"]
```

##### `generate_magnet_link(info_hash: str, name: Optional[str] = None, trackers: Optional[list] = None) -> str`

Генерирует магнитную ссылку.

**Параметры:**
- `info_hash` (str): Строка Info Hash
- `name` (Optional[str]): Имя файла (опционально)
- `trackers` (Optional[list]): Список трекеров (опционально)

**Возвращает:**
- `str`: Полная магнитная ссылка

**Пример:**
```python
magnet = converter.generate_magnet_link(
    info_hash="ABC123...",
    name="Example",
    trackers=["http://tracker.example.com"]
)
# Вывод: "magnet:?xt=urn:btih:ABC123...&dn=Example&tr=http://tracker.example.com"
```

##### `convert(torrent_path: Path, include_trackers: bool = False) -> Tuple[str, str, Dict]`

Преобразует один торрент-файл в магнитную ссылку.

**Параметры:**
- `torrent_path` (Path): Путь к торрент-файлу
- `include_trackers` (bool): Включать ли трекеры в магнитную ссылку

**Возвращает:**
- `Tuple[str, str, Dict]`: (magnet_link, info_hash, metadata)
  - `magnet_link`: Магнитная ссылка
  - `info_hash`: Info Hash
  - `metadata`: Словарь метаданных, содержащий:
    - `name`: Имя файла
    - `trackers`: Список трекеров
    - `info_hash`: Info Hash
    - `file_size`: Размер файла

**Вызывает:**
- `IOError`: Ошибка чтения файла
- `ValueError`: Ошибка формата торрент-файла

**Пример:**
```python
from pathlib import Path

magnet_link, info_hash, metadata = converter.convert(
    Path("example.torrent"),
    include_trackers=True
)

print(f"Magnet: {magnet_link}")
print(f"Info Hash: {info_hash}")
print(f"Name: {metadata['name']}")
print(f"Trackers: {metadata['trackers']}")
```

## Утилитарные функции

### `collect_torrent_files`

`magneto.utils.collect_torrent_files` - Собирает торрент-файлы.

```python
from magneto.utils import collect_torrent_files
from pathlib import Path

# Собрать торрент-файлы в текущей директории
files = collect_torrent_files(Path("folder/"))

# Рекурсивный поиск
files = collect_torrent_files(Path("folder/"), recursive=True)

# Поиск с учетом регистра
files = collect_torrent_files(Path("folder/"), case_sensitive=True)
```

**Параметры:**
- `input_path` (Path): Входной путь (файл или директория)
- `recursive` (bool): Рекурсивно искать в подкаталогах (по умолчанию: False)
- `case_sensitive` (bool): Учитывать регистр (по умолчанию: False)

**Возвращает:**
- `List[Path]`: Список путей к торрент-файлам

### `get_output_path`

`magneto.utils.get_output_path` - Определяет путь к выходному файлу.

```python
from magneto.utils import get_output_path
from pathlib import Path

# Автоматически определить выходной путь
output = get_output_path(Path("folder/"))

# Указать выходной путь
output = get_output_path(Path("folder/"), Path("custom_output.txt"))
```

**Параметры:**
- `input_path` (Path): Входной путь
- `output_path` (Optional[Path]): Пользовательский выходной путь (опционально)
- `default_name` (str): Имя выходного файла по умолчанию (по умолчанию: "magnet_links.txt")

**Возвращает:**
- `Path`: Путь к выходному файлу

## Модуль UI

### UI

`magneto.ui.UI` - Обработчик пользовательского интерфейса.

```python
from magneto.ui import UI

# Инициализировать UI
ui = UI(verbose=True, quiet=False, use_colors=True)

# Вывести сообщения
ui.print_success("Преобразование успешно")
ui.print_error("Преобразование не удалось")
ui.print_warning("Предупреждающее сообщение")
ui.print_info("Информационное сообщение")
ui.print_verbose("Подробное сообщение")

# Сохранить результаты
results = [
    ("file.torrent", "magnet:...", "ABC123...", {"name": "Example"})
]
ui.save_results(results, Path("output.txt"), format_type="full")

# Вывести результаты в stdout
ui.print_results(results, format_type="json")

# Вывести сводку
ui.print_summary()
```

**Параметры инициализации:**
- `verbose` (bool): Показывать ли подробную информацию (по умолчанию: False)
- `quiet` (bool): Использовать ли тихий режим (по умолчанию: False)
- `use_colors` (bool): Использовать ли цветной вывод (по умолчанию: True)

## Полные примеры

### Пример 1: Пакетное преобразование файлов

```python
from pathlib import Path
from magneto.core import TorrentConverter
from magneto.utils import collect_torrent_files

converter = TorrentConverter()
torrent_files = collect_torrent_files(Path("folder/"), recursive=True)

results = []
for torrent_file in torrent_files:
    try:
        magnet_link, info_hash, metadata = converter.convert(
            torrent_file,
            include_trackers=True
        )
        results.append((str(torrent_file), magnet_link, info_hash, metadata))
        print(f"✓ {torrent_file.name}: {magnet_link}")
    except Exception as e:
        print(f"✗ {torrent_file.name}: {e}")
```

### Пример 2: Пользовательский формат вывода

```python
import json
from pathlib import Path
from magneto.core import TorrentConverter

converter = TorrentConverter()
torrent_file = Path("example.torrent")

magnet_link, info_hash, metadata = converter.convert(torrent_file)

output = {
    "file": str(torrent_file),
    "magnet": magnet_link,
    "info_hash": info_hash,
    "name": metadata.get("name"),
    "trackers": metadata.get("trackers", [])
}

with open("output.json", "w", encoding="utf-8") as f:
    json.dump([output], f, ensure_ascii=False, indent=2)
```

### Пример 3: Интеграция в скрипты

```python
#!/usr/bin/env python3
"""Пользовательский скрипт преобразования"""
from pathlib import Path
from magneto.core import TorrentConverter
from magneto.utils import collect_torrent_files

def convert_folder(folder_path: str, output_file: str):
    converter = TorrentConverter()
    torrent_files = collect_torrent_files(Path(folder_path), recursive=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        for torrent_file in torrent_files:
            try:
                magnet_link, _, _ = converter.convert(torrent_file)
                f.write(f"{magnet_link}\n")
                print(f"✓ {torrent_file.name}")
            except Exception as e:
                print(f"✗ {torrent_file.name}: {e}")

if __name__ == "__main__":
    convert_folder("downloads/", "magnets.txt")
```

## Обработка исключений

### Распространенные исключения

- `IOError`: Ошибка чтения файла
- `ValueError`: Ошибка формата торрент-файла или отсутствие обязательных полей
- `ImportError`: Отсутствие необходимых зависимостей (например, bencode)

### Пример обработки исключений

```python
from magneto.core import TorrentConverter
from pathlib import Path

converter = TorrentConverter()

try:
    magnet_link, info_hash, metadata = converter.convert(Path("file.torrent"))
except IOError as e:
    print(f"Ошибка чтения файла: {e}")
except ValueError as e:
    print(f"Ошибка формата файла: {e}")
except Exception as e:
    print(f"Неизвестная ошибка: {e}")
```

## Подсказки типов

Все функции и классы включают полные подсказки типов для автодополнения IDE и проверки типов.

```python
from typing import Dict, Optional, Tuple, List
from pathlib import Path
```

## Следующие шаги

- [Руководство по использованию](/ru/usage) - Изучить использование командной строки
- [Начало работы](/ru/getting-started) - Изучить базовое использование
