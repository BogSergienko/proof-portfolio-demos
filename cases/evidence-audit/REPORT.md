# KAI Proof — демонстрационный аудит

Данные вымышленные. Пример не оценивает реальную модель ИИ и не доказывает безопасность системы.

| Событие | Решение | Почему |
|---|---|---|
| EV-01 | VERIFIED | Current source and claim match; no STOP violation. |
| EV-02 | VERIFIED | Current source and claim match; no STOP violation. |
| EV-03 | VALUE_MISMATCH | Claim does not equal source field value. |
| EV-04 | UNVERIFIED | Referenced evidence does not exist. |
| EV-05 | STALE_VERSION | Claim cites a non-current source version. |
| EV-06 | INTEGRITY_FAIL | Evidence content checksum is invalid. |
| EV-07 | BLOCKED_STOP | A write/action was attempted after task STOP. |

Подтверждено: 2; выявлено/заблокировано: 5.
PASS означает совпадение с заранее заданным тестовым эталоном, а не доказанное снижение ошибок реального ИИ.
