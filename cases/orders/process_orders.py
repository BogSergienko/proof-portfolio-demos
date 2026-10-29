"""Демонстрационная автоматизация двух CSV выгрузок без сторонних библиотек.

Пример на вымышленных данных. В настоящем проекте правила согласовывают с клиентом.
Запуск: python process_orders.py
"""
import csv
import json
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUTS = [ROOT / "Выгрузка_магазин.csv", ROOT / "Выгрузка_касса.csv"]
FIELDNAMES = ["номер_заказа", "дата", "категория", "товар", "количество", "цена", "сумма", "статус"]
STATUS = {"оплачен", "возврат", "отменён", "в обработке"}

def export_csv(name, rows, columns):
    with (ROOT / name).open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, delimiter=";")
        writer.writeheader(); writer.writerows(rows)

seen, clean, errors = set(), [], []
raw_count = 0
for source in INPUTS:
    with source.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        if reader.fieldnames != FIELDNAMES:
            raise ValueError(f"Неожиданные колонки в {source.name}")
        for line, row in enumerate(reader, 2):
            raw_count += 1
            oid = row["номер_заказа"].strip()
            issue = None
            if not oid:
                issue = "Нет номера заказа"
            elif oid in seen:
                issue = "Дубликат номера заказа"
            else:
                seen.add(oid)
                try:
                    date.fromisoformat(row["дата"])
                    quantity = int(row["количество"])
                    price = Decimal(row["цена"])
                    value = Decimal(row["сумма"])
                    if quantity <= 0 or price < 0:
                        issue = "Некорректное количество или цена"
                    elif Decimal(quantity) * price != value:
                        issue = "Сумма не совпадает с количеством × ценой"
                    elif row["статус"] not in STATUS:
                        issue = "Неизвестный статус"
                except (ValueError, TypeError, InvalidOperation):
                    issue = "Некорректный формат даты или числа"
            if issue:
                errors.append({"источник": source.name, "строка": line, "причина": issue, **row})
            else:
                clean.append(dict(row))

# Кассовое правило примера: только оплаченное увеличивает выручку,
# возвраты уменьшают её; заказы в обработке и отменённые не включены.
summary = defaultdict(lambda: {"оплачено_руб": Decimal(0), "возвраты_руб": Decimal(0), "число_заказов": 0})
for row in clean:
    item = summary[row["категория"]]
    item["число_заказов"] += 1
    amount = Decimal(row["сумма"])
    if row["статус"] == "оплачен":
        item["оплачено_руб"] += amount
    elif row["статус"] == "возврат":
        item["возвраты_руб"] += amount

summaries = []
for category, s in sorted(summary.items()):
    summaries.append({
        "категория": category,
        "проверенных_заказов": s["число_заказов"],
        "оплачено_руб": int(s["оплачено_руб"]),
        "возвраты_руб": int(s["возвраты_руб"]),
        "итог_руб": int(s["оплачено_руб"] - s["возвраты_руб"]),
    })

export_csv("01_Проверенные_заказы.csv", clean, FIELDNAMES)
export_csv("02_Проблемные_строки.csv", errors, ["источник", "строка", "причина"] + FIELDNAMES)
export_csv("03_Сводка.csv", summaries, ["категория", "проверенных_заказов", "оплачено_руб", "возвраты_руб", "итог_руб"])
metrics = {
    "входных_строк": raw_count,
    "проверенных_строк": len(clean),
    "проблемных_строк": len(errors),
    "дубликатов": sum(x["причина"] == "Дубликат номера заказа" for x in errors),
    "несовпадений_сумм": sum(x["причина"] == "Сумма не совпадает с количеством × ценой" for x in errors),
    "ошибок_формата": sum(x["причина"] == "Некорректный формат даты или числа" for x in errors),
    "выручка_после_возвратов_руб": sum(x["итог_руб"] for x in summaries),
    "демо": "полностью синтетические данные, не реальные продажи",
}
(ROOT / "04_Показатели.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(metrics, ensure_ascii=False, indent=2))
assert metrics["входных_строк"] == metrics["проверенных_строк"] + metrics["проблемных_строк"]
