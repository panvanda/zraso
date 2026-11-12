"""Merge a small patch into menus.json instead of rewriting the whole file.

Usage: python3 merge_menu.py menus.json patch.json

patch.json:
{
  "updated": "2026-11-12T06:40:00+01:00",
  "weekStart": "2026-11-09",
  "set": { "<restaurant id>": { "YYYY-MM-DD": [ {cat, name, price?, alg?, veg?}, ... ] } },
  "everyday": { "<restaurant id>": [ ...items shown every day... ] }
}
A new weekStart clears every restaurant's days before the patch is applied.
"""
import json
import sys

menus_path, patch_path = sys.argv[1], sys.argv[2]
with open(menus_path, encoding="utf-8") as f:
    data = json.load(f)
with open(patch_path, encoding="utf-8") as f:
    patch = json.load(f)

if patch.get("weekStart") and patch["weekStart"] != data.get("weekStart"):
    data["weekStart"] = patch["weekStart"]
    for r in data["restaurants"]:
        r["days"] = {}

by_id = {r["id"]: r for r in data["restaurants"]}
unknown = [rid for rid in list(patch.get("set", {})) + list(patch.get("everyday", {})) if rid not in by_id]
if unknown:
    sys.exit("Unknown restaurant id(s): " + ", ".join(unknown))

changed = 0
for rid, days in patch.get("set", {}).items():
    for day, items in days.items():
        by_id[rid].setdefault("days", {})[day] = items
        changed += 1
for rid, items in patch.get("everyday", {}).items():
    by_id[rid]["everyday"] = items
    changed += 1

if patch.get("updated"):
    data["updated"] = patch["updated"]

with open(menus_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
print(f"merged {changed} entries")
