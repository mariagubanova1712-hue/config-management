#!/usr/bin/env python3
"""Задача 7: автоматическое построение MiniZinc-модели по метаданным пакетов."""
import subprocess
import sys

# Метаданные пакетов: имя -> версия -> {зависимость: ограничение semver}
PACKAGES = {
    "root":   {"1.0.0": {"foo": "^1.0.0", "target": "^2.0.0"}},
    "foo":    {"1.1.0": {"left": "^1.0.0", "right": "^1.0.0"},
               "1.0.0": {}},
    "left":   {"1.0.0": {"shared": ">=1.0.0"}},
    "right":  {"1.0.0": {"shared": "<2.0.0"}},
    "shared": {"2.0.0": {},
               "1.0.0": {"target": "^1.0.0"}},
    "target": {"2.0.0": {}, "1.0.0": {}},
}
ROOT = "root"


def parse(v):
    return tuple(int(x) for x in v.split("."))


def matches(version, spec):
    """Проверка версии на соответствие ограничению semver (^, ~, >=, <=, >, <, =)."""
    v = parse(version)
    for part in spec.split():          # несколько условий через пробел: ">=1.0.0 <2.0.0"
        if part.startswith("^"):
            b = parse(part[1:])
            upper = (b[0] + 1, 0, 0) if b[0] > 0 else (0, b[1] + 1, 0)
            ok = b <= v < upper
        elif part.startswith("~"):
            b = parse(part[1:])
            ok = b <= v < (b[0], b[1] + 1, 0)
        elif part.startswith(">="):
            ok = v >= parse(part[2:])
        elif part.startswith("<="):
            ok = v <= parse(part[2:])
        elif part.startswith(">"):
            ok = v > parse(part[1:])
        elif part.startswith("<"):
            ok = v < parse(part[1:])
        else:
            ok = v == parse(part.lstrip("="))
        if not ok:
            return False
    return True


def build_model(packages, root):
    """Каждый пакет — переменная 0..N, где 0 — «не установлен», i — i-я версия."""
    versions = {p: sorted(vs, key=parse) for p, vs in packages.items()}
    lines = []
    for p, vs in versions.items():
        lines.append(f"% {p}: " + ", ".join(f"{i + 1}={v}" for i, v in enumerate(vs)))
        lines.append(f"var 0..{len(vs)}: {p};")
    lines.append(f"constraint {root} > 0;")
    for p, vs in versions.items():
        for i, v in enumerate(vs, 1):
            for dep, spec in packages[p][v].items():
                ok = [str(j) for j, dv in enumerate(versions[dep], 1) if matches(dv, spec)]
                rhs = f"{dep} in {{{', '.join(ok)}}}" if ok else "false"
                lines.append(f"constraint {p} = {i} -> {rhs};  % {p} {v} -> {dep} {spec}")
    # пакет ставится, только если он кому-то нужен (как в настоящем менеджере)
    for p in versions:
        if p == root:
            continue
        users = [f"{q} = {i}" for q, qvs in versions.items()
                 for i, qv in enumerate(qvs, 1) if p in packages[q][qv]]
        need = " \\/ ".join(users) if users else "false"
        lines.append(f"constraint {p} > 0 -> ({need});")
    # среди допустимых решений выбираем наиболее свежие версии
    score = " + ".join(f"{p}" for p in versions)
    lines.append(f"solve maximize {score};")
    out = " ++ ".join(f'"{p}=" ++ show({p}) ++ "\\n"' for p in versions)
    lines.append(f"output [{out}];")
    return "\n".join(lines), versions


def main():
    model, versions = build_model(PACKAGES, ROOT)
    with open("generated.mzn", "w") as f:
        f.write(model + "\n")
    print(model, "\n")
    res = subprocess.run(["minizinc", "generated.mzn"], capture_output=True, text=True)
    if "UNSATISFIABLE" in res.stdout:
        print("Решения нет")
        sys.exit(1)
    print("Результат:")
    for line in res.stdout.splitlines():
        if "=" in line and not line.startswith(("-", "=")):
            p, i = line.split("=")
            i = int(i)
            print(f"  {p} {versions[p][i - 1] if i else '(не нужен)'}")


if __name__ == "__main__":
    main()
