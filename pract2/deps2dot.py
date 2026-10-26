#!/usr/bin/env python3
"""Задача 3: построение graphviz-графа зависимостей matplotlib (pip) и express (npm)."""
import importlib.metadata as md
import json
import re
import subprocess
import sys


def python_deps(name, edges, seen):
    key = name.lower()
    if key in seen:
        return
    seen.add(key)
    try:
        reqs = md.requires(name) or []
    except md.PackageNotFoundError:
        return
    for r in reqs:
        if "extra ==" in r:          # необязательные (extras) зависимости пропускаем
            continue
        dep = re.split(r"[ ;<>=!~\[(]", r, maxsplit=1)[0]
        edges.add((key, dep.lower()))
        python_deps(dep, edges, seen)


def npm_deps(tree, name, edges):
    for dep, info in (tree.get("dependencies") or {}).items():
        edges.add((name, dep))
        npm_deps(info, dep, edges)


def to_dot(title, edges):
    lines = [f'digraph "{title}" {{', "  rankdir=LR;", "  node [shape=box, style=rounded];"]
    lines += [f'  "{a}" -> "{b}";' for a, b in sorted(edges)]
    lines.append("}")
    return "\n".join(lines)


if __name__ == "__main__":
    which = sys.argv[1]
    edges = set()
    if which == "matplotlib":
        python_deps("matplotlib", edges, set())
    else:  # express: дерево из `npm ls --all --json` в каталоге с установленным express
        tree = json.loads(subprocess.run(["npm", "ls", "--all", "--json"],
                                         capture_output=True, text=True, cwd=sys.argv[2]).stdout)
        npm_deps(tree["dependencies"]["express"], "express", edges)
    print(to_dot(which, edges))
