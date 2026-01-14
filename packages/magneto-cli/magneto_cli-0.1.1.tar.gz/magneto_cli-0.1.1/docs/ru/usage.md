# Руководство по использованию

Это руководство предоставляет подробную информацию о всех функциях и методах использования Magneto.

## Базовое использование

### Преобразование одного файла

```bash
magneto file.torrent
```

### Преобразование всех файлов в папке

```bash
magneto folder/
```

### Указание выходного файла

```bash
magneto folder/ -o output.txt
```

## Форматы вывода

Magneto поддерживает три формата вывода:

### 1. Полный формат (по умолчанию)

```bash
magneto folder/ -f full
```

Пример вывода:
```
================================================================================
Torrent to Magnet Link Conversion Results
================================================================================

File: example.torrent
Magnet Link: magnet:?xt=urn:btih:ABC123...&dn=Example
Info Hash: ABC123...
Name: Example
Trackers: 3 found
--------------------------------------------------------------------------------

================================================================================
Magnet Link List (Links Only)
================================================================================

magnet:?xt=urn:btih:ABC123...&dn=Example
```

### 2. Только ссылки

```bash
magneto folder/ -f links_only
```

Пример вывода:
```
magnet:?xt=urn:btih:ABC123...&dn=Example
magnet:?xt=urn:btih:DEF456...&dn=Another
```

### 3. JSON формат

```bash
magneto folder/ -f json
```

Пример вывода:
```json
[
  {
    "file": "example.torrent",
    "magnet": "magnet:?xt=urn:btih:ABC123...&dn=Example",
    "info_hash": "ABC123...",
    "name": "Example",
    "trackers": [
      "http://tracker1.example.com",
      "http://tracker2.example.com"
    ]
  }
]
```

## Опции поиска

### Рекурсивный поиск

Рекурсивный поиск торрент-файлов в подкаталогах:

```bash
magneto folder/ -r
```

### Поиск с учетом регистра

По умолчанию поиск не учитывает регистр (будут найдены как `.torrent`, так и `.TORRENT`). Если нужен поиск с учетом регистра:

```bash
magneto folder/ --case-sensitive
```

## Опции преобразования

### Включение информации о трекерах

По умолчанию сгенерированные магнитные ссылки не включают информацию о трекерах. Чтобы включить:

```bash
magneto folder/ --include-trackers
```

Сгенерированные магнитные ссылки будут включать все адреса трекеров:
```
magnet:?xt=urn:btih:ABC123...&dn=Example&tr=http://tracker1.com&tr=http://tracker2.com
```

## Опции отображения

### Режим подробного вывода

Отображение подробной информации о обработке:

```bash
magneto folder/ -v
```

Вывод включает:
- Info Hash для каждого файла
- Имя файла
- Количество трекеров

### Тихий режим

Показывать только сообщения об ошибках:

```bash
magneto folder/ -q
```

### Отключить цветной вывод

```bash
magneto folder/ --no-colors
```

## Методы вывода

### Сохранение в файл (по умолчанию)

```bash
magneto folder/ -o output.txt
```

Результаты будут сохранены в указанный файл. Если `-o` не указан, по умолчанию сохраняется в `magnet_links.txt`.

### Вывод в стандартный вывод

```bash
magneto folder/ --stdout
```

Результаты будут выведены непосредственно в терминал без сохранения в файл.

В сочетании с опциями формата:

```bash
# Вывести только ссылки в терминал
magneto folder/ --stdout -f links_only

# Вывести JSON в терминал
magneto folder/ --stdout -f json
```

## Практические примеры

### Пример 1: Пакетное преобразование и сохранение как JSON

```bash
magneto downloads/ -r -f json -o results.json
```

### Пример 2: Быстро получить все магнитные ссылки

```bash
magneto folder/ --stdout -f links_only -q
```

### Пример 3: Преобразование в подробном режиме с трекерами

```bash
magneto folder/ -v --include-trackers -o output.txt
```

### Пример 4: Рекурсивный поиск и вывод в файл

```bash
magneto ~/Downloads/ -r -f full -o ~/magnets.txt
```

## Использование в коде

Помимо инструмента командной строки, Magneto также предоставляет Python API, который можно использовать непосредственно в коде.

### Быстрый старт

Использование функции `torrent_to_magnet` — это самый простой способ интеграции:

```python
from magneto import torrent_to_magnet

# Преобразование из пути к файлу
magnet, info_hash, metadata = torrent_to_magnet("path/to/file.torrent")
print(f"Магнитная ссылка: {magnet}")
print(f"Info Hash: {info_hash}")
print(f"Имя файла: {metadata['name']}")

# Преобразование из URL
magnet, info_hash, metadata = torrent_to_magnet("https://example.com/file.torrent")

# Включить информацию о трекерах
magnet, info_hash, metadata = torrent_to_magnet(
    "file.torrent", 
    include_trackers=True
)
```

### Пример пакетной обработки

```python
from pathlib import Path
from magneto import torrent_to_magnet

def batch_convert(folder_path: str):
    """Пакетное преобразование всех торрент-файлов в папке"""
    folder = Path(folder_path)
    results = []
    
    for torrent_file in folder.glob("*.torrent"):
        try:
            magnet, info_hash, metadata = torrent_to_magnet(torrent_file)
            results.append({
                "file": str(torrent_file),
                "magnet": magnet,
                "info_hash": info_hash,
                "name": metadata["name"]
            })
            print(f"✓ {torrent_file.name}")
        except Exception as e:
            print(f"✗ {torrent_file.name}: {e}")
    
    return results

# Пример использования
results = batch_convert("downloads/")
```

### Пример обработки URL

```python
from magneto import torrent_to_magnet

def convert_from_url(url: str):
    """Загрузить и преобразовать торрент-файл из URL"""
    try:
        magnet, info_hash, metadata = torrent_to_magnet(url, include_trackers=True)
        print(f"Магнитная ссылка: {magnet}")
        print(f"Источник: {metadata.get('source_url', 'N/A')}")
        return magnet
    except IOError as e:
        print(f"Ошибка загрузки: {e}")
    except ValueError as e:
        print(f"Ошибка формата файла: {e}")

# Пример использования
convert_from_url("https://example.com/torrent.torrent")
```

### Обработка ошибок

```python
from magneto import torrent_to_magnet

try:
    magnet, info_hash, metadata = torrent_to_magnet("file.torrent")
except IOError as e:
    print(f"Ошибка чтения файла: {e}")
except ValueError as e:
    print(f"Ошибка формата файла: {e}")
except ImportError as e:
    print(f"Отсутствует зависимость: {e}")
```

### Описание возвращаемых значений

Функция `torrent_to_magnet` возвращает кортеж из трех элементов:

1. **magnet_link** (str): Сгенерированная магнитная ссылка
2. **info_hash** (str): Info Hash торрента (шестнадцатеричная строка, верхний регистр)
3. **metadata** (Dict): Словарь метаданных, содержащий:
   - `name`: Имя файла
   - `trackers`: Список трекеров (включается даже если `include_trackers=False`)
   - `info_hash`: Info Hash
   - `file_size`: Размер файла (в байтах)
   - `source_url`: Исходный URL, если входные данные — URL

### Дополнительные возможности API

Для более продвинутых функций (таких как пользовательские форматы вывода, пакетная обработка и т.д.) см. [Справочник API](/ru/api-reference).

## Справочник аргументов командной строки

### Позиционные аргументы

- `input` - Входной торрент-файл или путь к папке, содержащей торрент-файлы

### Опции вывода

- `-o, --output FILE` - Указать путь к выходному файлу (по умолчанию: `magnet_links.txt` во входной директории)
- `-f, --format {full,links_only,json}` - Формат вывода (по умолчанию: full)
- `--stdout` - Вывести результаты в stdout вместо сохранения в файл

### Опции поиска

- `-r, --recursive` - Рекурсивный поиск торрент-файлов в подкаталогах
- `--case-sensitive` - Поиск расширений файлов с учетом регистра

### Опции преобразования

- `--include-trackers` - Включить информацию о трекерах в магнитные ссылки

### Опции отображения

- `-v, --verbose` - Показать подробную информацию о выводе
- `-q, --quiet` - Тихий режим, показывать только сообщения об ошибках
- `--no-colors` - Отключить цветной вывод

### Другие опции

- `-h, --help` - Показать справочную информацию и выйти
- `--version` - Показать информацию о версии и выйти

## Советы по использованию

### 1. Операции с конвейером

Передача вывода другим командам:

```bash
magneto folder/ --stdout -f links_only | grep "ABC123"
```

### 2. Пакетная обработка больших папок

Для папок, содержащих много файлов, рекомендуется тихий режим:

```bash
magneto large_folder/ -r -q -f links_only -o results.txt
```

### 3. Использование со скриптами

Использование формата JSON упрощает разбор в скриптах:

```bash
magneto folder/ -f json -o results.json
# Затем разобрать JSON с помощью Python/Node.js и т.д.
```

## Обработка ошибок

### Распространенные ошибки

1. **Файл не существует**
   ```
   Error: Path does not exist: /path/to/file
   ```

2. **Ошибка формата файла**
   ```
   ✗ example.torrent: Unable to parse torrent file
   ```

3. **Ошибка прав доступа**
   ```
   Error: Unable to read file /path/to/file: Permission denied
   ```

### Статистика ошибок

После завершения обработки отображается статистика:

```
================================================================================
Processing complete: 10 file(s) total
Success: 8
Failed: 2
================================================================================
```

## Следующие шаги

- [Справочник API](/ru/api-reference) - Узнайте, как использовать Magneto в коде
- [Начало работы](/ru/getting-started) - Повторите базовое использование
