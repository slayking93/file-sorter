# Spec: File Sorter by Extension

## Objective

Небольшое CLI-приложение на Python, которое сортирует файлы в указанной папке, раскладывая их в подпапки по расширениям. Один файл — одна категория (расширение в нижнем регистре, без ведущей точки). Назначение — навести порядок в каталогах `Downloads`, рабочих папках и т. п.

User story: пользователь запускает `sort ./messy-folder` и получает структуру вида `messy-folder/jpg/`, `messy-folder/pdf/`, `messy-folder/no_extension/` и т. д. Файлы перемещены (не скопированы), конфликты имён разрешаются добавлением суффикса `_1`, `_2`, …

## Tech Stack

- Python 3.10+
- Только стандартная библиотека: `argparse`, `pathlib`, `shutil`, `sys`, `dataclasses`
- pytest (только для разработки, в `requirements-dev.txt`)

## Commands

```bash
# Запуск напрямую
python sort.py <path_to_folder>

# Запуск с флагами
python sort.py <path_to_folder> --recursive
python sort.py <path_to_folder> --dry-run

# Установка как пакет (даёт команду `sort`)
pip install -e .
sort <path_to_folder>

# Тесты
pip install -r requirements-dev.txt
pytest -q
```

## Project Structure

```
.
├── SPEC.md
├── README.md
├── LICENSE
├── pyproject.toml           # точка установки пакета, console_script `sort`
├── requirements-dev.txt     # pytest
├── sort.py                  # CLI entry point
└── src/
    └── sorter.py            # чистая логика: classify, iter_files, plan_moves, run
```

## CLI Flags

- `--recursive` / `-r` — обходить подпапки. Сами подпапки остаются на месте, файлы из них перемещаются в категориальные папки верхнего уровня.
- `--dry-run` / `-n` — показать план перемещений без изменения FS. Реализовано через `plan_moves()`, без побочных эффектов.

## Code Style

- Type hints обязательны для публичных функций.
- Docstring в стиле Google — кратко, по делу.
- Имена: `snake_case` для функций/переменных, `PascalCase` для классов.
- Максимальная длина строки — 100 символов.
- Без wildcard-импортов.
- Чистая логика (`plan_moves`) отделена от исполнения (`run`) — это позволяет dry-run без дублирования кода.

```python
def plan_moves(files: Iterable[Path], dest_root: Path) -> list[Move]:
    """Build a list of planned file moves without touching disk."""
    moves: list[Move] = []
    for src in files:
        ext = classify(src)
        target_dir = dest_root / ext
        target = resolve_collision(target_dir, src.name)
        moves.append(Move(src=src, target=target))
    return moves
```

## Testing Strategy

- Фреймворк: **pytest** с фикстурой `tmp_path` для изоляции (никаких следов в реальной FS).
- Уровни:
  - Unit: `classify()` (расширение → категория), `resolve_collision()` (логика суффиксов), `iter_files()` (top level vs recursive).
  - Integration: `run()` целиком на временной директории с фиктивными файлами.
- Покрытие: все ветви `classify()` + happy path `run()` + пустая папка + коллизия + рекурсия + идемпотентность.
- Никаких моков `pathlib` — мы работаем с реальной временной FS, это надёжнее и читаемее.

## Boundaries

**Always:**
- Запускать `pytest -q` перед коммитом.
- Валидировать путь: папка должна существовать и быть директорией, иначе — понятная ошибка в stderr и код выхода 2.
- По умолчанию не ходить в подпапки рекурсивно (безопаснее). Рекурсия — явный флаг.
- Двигать файлы через `shutil.move`.

**Ask first:**
- Изменения в CLI-интерфейсе (новые флаги).
- Добавление зависимостей.

**Never:**
- Удалять файлы.
- Перезаписывать существующие файлы (только переименование через суффикс).
- Трогать `pathlib`-симлинки как ходы по ним — обрабатываем как обычные файлы (через `is_file()`).

## Success Criteria

1. `sort ./folder` создаёт подпапки по расширениям для всех файлов верхнего уровня.
2. `sort ./folder --recursive` обрабатывает и подпапки (сами подпапки сохраняются).
3. `sort ./folder --dry-run` печатает план без изменения FS.
4. Расширения приводятся к нижнему регистру, без ведущей точки (`report.PDF` → папка `pdf`).
5. Файлы без расширения попадают в подпапку `no_extension`.
6. При коллизии имён в целевой папке используется суффикс `_1`, `_2`, …; оригинал не перезаписывается.
7. Несуществующий путь → сообщение в stderr + exit code 2.
8. Пустая папка — не падает, подпапки не создаются.
9. `pytest -q` проходит зелёным (17 тестов).

## Open Questions

- **Конфиг-файл для маппинга расширений** (например, группировать `.jpeg` и `.jpg` в одну папку `images/`). Сейчас правило «один файл — одно расширение как есть». Если будет нужен маппинг — это отдельный итеративный шаг с YAML/TOML конфигом.
- **Кастомное имя для `no_extension`.** Сейчас захардкожено. Можно вынести в флаг при необходимости.