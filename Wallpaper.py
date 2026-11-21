import ctypes
import random
from pathlib import Path

# Папки для поиска изображений
folders = [
    Path.home() / "Pictures",
    Path.home() / "Downloads",
    Path.home() / "Desktop",
]

extensions = {".jpg", ".jpeg", ".png", ".bmp"}

# Поиск изображений
images = []

for folder in folders:
    if folder.exists():
        images.extend(
            p for p in folder.rglob("*")
            if p.is_file() and p.suffix.lower() in extensions
        )

if not images:
    print("Изображения не найдены!")
    input()
    raise SystemExit

# Выбираем изображение
image = random.choice(images)

# Меняем обои
ctypes.windll.user32.SystemParametersInfoW(
    20, 0, str(image), 3
)

print(f"Обои изменены на: {image.name}")
