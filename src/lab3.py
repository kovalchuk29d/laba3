from functools import reduce
from collections import defaultdict

# Дані
KEYS = ("city", "t_avg", "t_min", "t_max", "precip", "rain_days", "wind_max", "t_anom", "p_anom")
NAME = dict(zip(KEYS, ("Місто", "T сер", "T мін", "T макс", "Опади", "Дощ.дн", "Вітер", "ΔT", "Δопад")))
NUM = KEYS[1:]
NOTE = "  MeteoArhiv.com.ua, 30 днів до 29.10.2026 (Одеса — до 21.10) · T °C, опади мм, вітер м/с, Δ — від норми"
data = [dict(zip(KEYS, r)) for r in [
    ("Київ", 12.1, 5.9, 22.8, 64.0, 14, 4.3, 3.6, 42), ("Львів", 11.2, 3.3, 25.0, 43.2, 13, 6.3, 2.1, -11),
    ("Одеса", 14.7, 5.7, 22.0, 57.7, 9, 5.2, 1.0, 72), ("Харків", 12.7, 4.8, 24.6, 82.2, 9, 4.4, 4.3, 90)]]


# Оформлення та введення
def grid(cells):
    """Малює таблицю; перший рядок — заголовок."""
    w = [max(map(len, col)) for col in zip(*cells)]
    isnum = lambda v: v.replace(".", "").lstrip("+-").isdigit()
    al = [">" if all(map(isnum, col[1:])) else "<" for col in zip(*cells)] 
    line = lambda a, b, c: "  " + a + b.join("─" * (x + 2) for x in w) + c
    print(line("┌", "┬", "┐"))
    for i, row in enumerate(cells):
        print("  │" + "│".join(f" {v:{a}{x}} " for v, a, x in zip(row, al, w)) + "│")
        if i == 0:
            print(line("├", "┼", "┤"))
    print(line("└", "┴", "┘"))

def table(rows, title):
    print(f"\n ▸ {title}")
    if not rows:
        return print("  (нічого не знайдено)")
    pos = {id(r): str(i + 1) for i, r in enumerate(data)}
    fmt = lambda v: f"{v:.1f}" if isinstance(v, float) else str(v)
    grid([["№"] + [NAME[k] for k in KEYS]] + [[pos[id(r)]] + [fmt(r[k]) for k in KEYS] for r in rows])

def num(label, cast=float):
    while True:
        try:
            return cast(input(f"  {label}: ").replace(",", "."))
        except ValueError:
            print("  ✘ Введіть число")

def pick(keys=NUM):
    print("  " + "  ".join(f"{i}) {NAME[k]}" for i, k in enumerate(keys, 1)))
    while True:
        n = num("Номер", int)
        if 1 <= n <= len(keys):
            return keys[n - 1]

def val(k):
    return input(f"  {NAME[k]}: ").strip().title() if k == "city" else num(NAME[k], int if k == "rain_days" else float)

def ask_i():
    i = num("№ запису", int) - 1
    if not 0 <= i < len(data):
        raise IndexError
    return i


# Додавання, видалення, оновлення
def add():
    data.append({k: val(k) for k in KEYS})
    print("  ✔ Додано")

def remove():
    table(data, "Усі записи")
    print(f"  ✔ Видалено «{data.pop(ask_i())['city']}»")

def update():
    table(data, "Усі записи")
    r = data[ask_i()]
    k = pick(KEYS)
    r[k] = val(k)
    print("  ✔ Оновлено")


# Пошук і фільтрація 
def find():
    q = input("  Місто: ").lower()
    table(list(filter(lambda r: q in r["city"].lower(), data)), "Результат пошуку")

def flt():
    k = pick()
    lo, hi = num("Від"), num("До")
    table(list(filter(lambda r: lo <= r[k] <= hi, data)), f"{NAME[k]}: {lo} … {hi}")


# Статистика (map, reduce, min, max)
def stats():
    rows = [["Показник", "Середнє", "Мінімум", "Максимум"]]
    for k in NUM:
        v = list(map(lambda r: r[k], data))
        lo, hi = min(data, key=lambda r: r[k]), max(data, key=lambda r: r[k])
        rows.append([NAME[k], f"{reduce(lambda a, b: a + b, v) / len(v):.1f}", f"{lo[k]} {lo['city']}", f"{hi[k]} {hi['city']}"])
    print()
    grid(rows)


# Групування, сортування, зрізи
def group():
    g = defaultdict(list)
    for r in data:
        g["Вологіше за норму" if r["p_anom"] > 0 else "Сухіше за норму"].append(r)
    print()
    grid([["Група", "Міста", "Сер. T", "Сума опадів"]] + [
        [n, ", ".join(r["city"] for r in rs), f"{sum(r['t_avg'] for r in rs) / len(rs):.1f}",
         f"{sum(r['precip'] for r in rs):.1f}"] for n, rs in g.items()])

def sort_slice():
    k = pick()
    s = sorted(data, key=lambda r: r[k], reverse=input("  За спаданням? (т/н): ") == "т")
    n = num("Розмір зрізу N", int)
    table(s[:n], f"Перші {n}")
    table(s[-n:], f"Останні {n}")


# Множини та словники
def sets():
    c = lambda p: {r["city"] for r in filter(p, data)}
    a, b = c(lambda r: r["t_max"] >= 24), c(lambda r: r["precip"] >= 60)
    s = lambda x: ", ".join(sorted(x)) or "—"
    print()
    grid([["Множина", "Міста"], ["A: T макс ≥ 24 °C", s(a)], ["B: опади ≥ 60 мм", s(b)],
          ["A ∪ B (об'єднання)", s(a | b)], ["A ∩ B (перетин)", s(a & b)], ["A − B (різниця)", s(a - b)]])

def dicts():
    f = {}
    for r in data:
        c = "ΔT ≥ +3 °C" if r["t_anom"] >= 3 else "ΔT < +3 °C"
        f[c] = f.get(c, 0) + 1
    print()
    grid([["Категорія", "К-сть"]] + [[c, str(n)] for c, n in f.items()])
    print("  Індекс місто → №:", {r["city"]: i + 1 for i, r in enumerate(data)})


# Меню
MENU = [("Показати всі записи", lambda: (table(data, "Усі записи"), print(NOTE))), ("Додати запис", add),
        ("Видалити запис", remove), ("Оновити запис", update), ("Пошук за містом", find),
        ("Фільтр за діапазоном", flt), ("Статистика (сер., мін, макс)", stats), ("Групування та агрегація", group),
        ("Сортування та зрізи", sort_slice), ("Операції з множинами", sets), ("Словники: частоти, індекс", dicts)]

def main():
    while True:
        print("\n╔" + "═" * 44 + "╗\n║" + "АНАЛІЗ ПОГОДИ ".center(44) + "║\n╠" + "═" * 44 + "╣")
        for i, (title, _) in enumerate(MENU, 1):
            print(f"║ {i:>2}. {title:<39}║")
        print("║  0. Вийти".ljust(45) + "║\n╚" + "═" * 44 + "╝")
        ch = input("  Ваш вибір ▸ ").strip()
        if ch == "0":
            break
        try:
            if not (ch.isdigit() and 1 <= int(ch) <= len(MENU)):
                raise ValueError
            MENU[int(ch) - 1][1]()
        except (ValueError, IndexError):
            print("  ✘ Некоректний ввід")
        input("\n  Enter — продовжити…")

if __name__ == "__main__":
    main()