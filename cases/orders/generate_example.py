"""Создаёт полностью вымышленные данные для демонстрационного кейса."""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

OUT = Path(__file__).resolve().parent
r = random.Random(42026)
items = [
    ("Кофе и чай", "Кофе арабика", 690),
    ("Кофе и чай", "Чай листовой", 470),
    ("Сладости", "Печенье", 350),
    ("Сладости", "Шоколад", 420),
    ("Для дома", "Термокружка", 1190),
    ("Для дома", "Френч-пресс", 1490),
    ("Подарки", "Подарочный набор", 2190),
]
rows = []
for i in range(124):
    category, product, price = r.choice(items)
    count = r.randint(1, 4)
    status = r.choices(["оплачен", "возврат", "отменён", "в обработке"], [76, 10, 8, 6])[0]
    rows.append({
        "номер_заказа": f"ORD-{10001+i}",
        "дата": str(date(2026, 10, 1) + timedelta(days=r.randint(0, 13))),
        "категория": category,
        "товар": product,
        "количество": str(count),
        "цена": str(price),
        "сумма": str(count * price),
        "статус": status,
    })
# Два типа проблем, с которыми обычно сталкиваются при объединении выгрузок:
for idx in range(73, 82):
    rows[idx]["сумма"] = str(int(rows[idx]["сумма"]) + 120)
for idx in range(93, 97):
    rows[idx]["цена"] = ""
# 14 повторных записей из первой выгрузки попали во вторую.
rows_a = rows[:68]
rows_b = rows[68:] + [dict(rows[i]) for i in range(14)]
headers = list(rows[0])
for filename, data in [("Выгрузка_магазин.csv", rows_a), ("Выгрузка_касса.csv", rows_b)]:
    with (OUT / filename).open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers, delimiter=";")
        w.writeheader(); w.writerows(data)
print(f"Created synthetic rows: {len(rows_a)} + {len(rows_b)} = {len(rows_a)+len(rows_b)}")
