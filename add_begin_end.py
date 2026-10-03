import json
import sys
from pathlib import Path

if len(sys.argv) >= 2:
    input_filename = sys.argv[1]
else:
    input_filename = "dataset.json"

if len(sys.argv) >= 3:
    output_filename = sys.argv[2]
else:
    output_filename = "dataset_with_end.json"

input_path = Path(input_filename)
output_path = Path(output_filename)

if not input_path.exists():
    raise FileNotFoundError(f"Файл не найден: {input_path}")

# === 2. Чтение датасета ===
with input_path.open("r", encoding="utf-8") as f:
    data = json.load(f)

# Поддержка разных форматов (список или обёртка в dict)
if isinstance(data, dict):
    for v in data.values():
        if isinstance(v, list):
            data = v
            break
    else:
        data = [data]

print(f"Всего сэмплов: {len(data)}")

# === 3. Обработка ===
SUFFIX = "\nbegin\nend."

new_data = []
added = 0
skipped_short = 0
skipped_empty = 0
already_ok = 0

for sample in data:
    if not (isinstance(sample, dict) and "output" in sample):
        continue

    new_sample = dict(sample)
    output = sample["output"]
    stripped = output.strip() if isinstance(output, str) else ""

    # Пустой output — не трогаем
    if not stripped:
        skipped_empty += 1
        new_data.append(new_sample)
        continue

    # Короткий вариант — начинается с ## — не трогаем
    if stripped.startswith("##"):
        skipped_short += 1
        new_data.append(new_sample)
        continue

    # Уже заканчивается на end. — не трогаем
    if stripped.endswith("end."):
        already_ok += 1
        new_data.append(new_sample)
        continue

    # Иначе — дописываем суффикс
    # rstrip сохраняет форматирование, но убирает хвостовые пробелы/переводы строк
    new_sample["output"] = output.rstrip() + SUFFIX
    added += 1
    new_data.append(new_sample)

print(f"Дописан '{SUFFIX.strip()}' в: {added}")
print(f"Пропущено коротких (## ...): {skipped_short}")
print(f"Пропущено пустых: {skipped_empty}")
print(f"Уже заканчиваются на 'end.': {already_ok}")

# === 4. Сохранение ===
with output_path.open("w", encoding="utf-8") as f:
    json.dump(new_data, f, ensure_ascii=False, indent=2)

print(f"\nСохранено: {output_path.resolve()}")