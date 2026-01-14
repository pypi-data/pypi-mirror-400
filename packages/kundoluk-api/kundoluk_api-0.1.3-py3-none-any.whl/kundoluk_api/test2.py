import os
from pathlib import Path

def load_gitignore_patterns(gitignore_path):
    """Загружает шаблоны из .gitignore."""
    patterns = set()
    if gitignore_path.exists():
        with gitignore_path.open('r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                patterns.add(line)
    return patterns

def is_ignored(path, patterns):
    """Проверяет, игнорируется ли путь."""
    # скрытые файлы и папки
    if path.name.startswith('.'):
        return True

    for pattern in patterns:
        if Path(pattern) in path.parents or path.match(pattern):
            return True
    return False

def count_python_lines(file_path):
    """Считает количество строк в Python файле."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except:
        return 0

def print_structure_and_count(path='.', indent=0, patterns=None, stats=None):
    base = Path(path)

    # сортируем: сначала папки, потом файлы
    dirs = []
    files = []
    for item in base.iterdir():
        if is_ignored(item, patterns):
            continue
        if item.is_dir():
            dirs.append(item)
        else:
            files.append(item)

    dirs.sort()
    files.sort()

    # вывод папок
    for d in dirs:
        print('    ' * indent + f"📁 {d.name}")
        stats["folders"] += 1
        print_structure_and_count(d, indent + 1, patterns, stats)

    # вывод файлов
    for f in files:
        print('    ' * indent + f"📄 {f.name}")
        stats["files"] += 1
        if f.suffix == '.py':
            stats["py_files"] += 1
            stats["py_lines"] += count_python_lines(f)


if __name__ == '__main__':
    root = Path('.')
    gitignore_patterns = load_gitignore_patterns(root / '.gitignore')

    stats = {
        "folders": 0,
        "files": 0,
        "py_files": 0,
        "py_lines": 0
    }

    print("📂 Архитектура проекта:\n")
    print_structure_and_count(root, patterns=gitignore_patterns, stats=stats)

    print("\n📊 Базовая статистика:")
    print(f"📁 Папок: {stats['folders']}")
    print(f"📄 Файлов: {stats['files']}")
    print(f"🐍 Python-файлов: {stats['py_files']}")
    print(f"🧮 Строк кода в Python: {stats['py_lines']}")
