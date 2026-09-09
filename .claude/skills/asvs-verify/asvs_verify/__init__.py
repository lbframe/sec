#!/usr/bin/env python3
"""asvs_verify — deterministic OWASP ASVS 5.0 requirement engine.

This is the *provable* backbone of the asvs-verify skill. It derives the
applicable requirement set from the authoritative OWASP dataset
(bundled data/asvs-5.0.0.json) rather than from model recall, so the scope of
an attestation is reproducible and auditable.

The engine ships as a named command — `asvs` — so nobody has to invoke raw
Python or know where the script lives:

    uvx --from <path-to-skill> asvs stats --level L2      # zero-install
    uv tool install --from <path-to-skill> asvs-verify    # put `asvs` on PATH
    asvs stats --level L2                                  # once installed

Data files are bundled with the package and resolved via importlib.resources,
so every command works from any working directory (e.g. inside a target repo),
independent of where the package is installed.

ASVS 5.0 level model (verified from the dataset, differs from 4.0.3):
  Each requirement carries a single field `L` = the *minimum* level at which it
  applies. Levels are cumulative:
    L1 = all reqs with L<=1        (baseline / "must for everyone")
    L2 = all reqs with L<=2        (standard for apps handling sensitive data)
    L3 = all reqs with L<=3        (high-assurance / critical)

Commands:
  list      Print applicable requirements for a level (optionally one chapter).
  stats     Print requirement counts per chapter for a level.
  scaffold  Emit a machine-readable attestation checklist (JSON) to fill in.
  report    Roll a filled-in checklist up into an attestation summary.
  chapters  List the 17 chapters.

Usage examples:
  asvs stats --level L2
  asvs list --level L1 --chapter V6
  asvs scaffold --level L2 --target "acme-api" --out checklist.json
  asvs scaffold --level L2 --chapter V6,V7,V8 --out authz.json
  asvs report --checklist checklist.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, OrderedDict
from importlib.resources import files

__version__ = "5.0.0"

# Bundled, importlib-resolved data — works regardless of install location / cwd.
DATA = files(__name__).joinpath("data")
DATASET = DATA.joinpath("asvs-5.0.0.json")
TOOLMAP = DATA.joinpath("tool-map.json")

# Verdict vocabulary. NEEDS-EVIDENCE is a first-class state on purpose: an
# honest "not verified" is worth more than a fabricated pass. See SKILL.md.
VERDICTS = ("PASS", "FAIL", "N/A", "NEEDS-EVIDENCE")
LEVELS = {"L1": 1, "L2": 2, "L3": 3}


def load_dataset(resource=DATASET):
    if not resource.is_file():
        sys.exit(f"error: ASVS dataset not found at {resource}")
    return json.loads(resource.read_text(encoding="utf-8"))


def load_toolmap(resource=TOOLMAP):
    if not resource.is_file():
        return {}
    return json.loads(resource.read_text(encoding="utf-8"))


def iter_requirements(data, max_level=3, chapters=None):
    """Yield (chapter_code, chapter_name, section_name, item) in order."""
    chapset = set(chapters) if chapters else None
    for chap in data["Requirements"]:
        code = chap["Shortcode"]
        if chapset and code not in chapset:
            continue
        for section in chap["Items"]:
            for item in section["Items"]:
                if int(item["L"]) <= max_level:
                    yield code, chap["Name"], section["Name"], item


def parse_chapters(arg):
    if not arg:
        return None
    return [c.strip().upper() for c in arg.split(",") if c.strip()]


def cmd_chapters(args):
    data = load_dataset()
    for chap in data["Requirements"]:
        n = sum(len(s["Items"]) for s in chap["Items"])
        print(f"{chap['Shortcode']:<4} {chap['Name']:<40} {n:>3} reqs")


def cmd_stats(args):
    data = load_dataset()
    lvl = LEVELS[args.level]
    per_chap = OrderedDict()
    per_level = Counter()
    for code, name, _s, item in iter_requirements(data, lvl, parse_chapters(args.chapter)):
        per_chap.setdefault(code, [name, 0])
        per_chap[code][1] += 1
        per_level[item["L"]] += 1
    total = sum(v[1] for v in per_chap.values())
    print(f"ASVS {data['Version']} — target {args.level} (cumulative: includes all L<={lvl})")
    print(f"{'CH':<4} {'CHAPTER':<40} {'REQS':>5}")
    print("-" * 52)
    for code, (name, n) in per_chap.items():
        print(f"{code:<4} {name:<40} {n:>5}")
    print("-" * 52)
    print(f"{'':<4} {'TOTAL APPLICABLE':<40} {total:>5}")
    print(f"\nNew at each tier within scope: "
          f"L1={per_level['1']}  L2+={per_level['2']}  L3+={per_level['3']}")


def cmd_list(args):
    data = load_dataset()
    lvl = LEVELS[args.level]
    for code, _n, section, item in iter_requirements(data, lvl, parse_chapters(args.chapter)):
        print(f"[{item['Shortcode']:<9} L{item['L']}] {item['Description']}")


def cmd_scaffold(args):
    data = load_dataset()
    toolmap = load_toolmap()
    lvl = LEVELS[args.level]
    rows = []
    for code, cname, section, item in iter_requirements(data, lvl, parse_chapters(args.chapter)):
        rows.append(OrderedDict([
            ("id", item["Shortcode"]),
            ("chapter", code),
            ("chapter_name", cname),
            ("section", section),
            ("min_level", f"L{item['L']}"),
            ("requirement", item["Description"]),
            ("verdict", "NEEDS-EVIDENCE"),
            ("mechanism", toolmap.get(code, {}).get("mechanism", "inspection")),
            ("suggested_tools", toolmap.get(code, {}).get("tools", [])),
            ("evidence", ""),          # REQUIRED for PASS/FAIL: file:line, config, scan output
            ("remediation", ""),       # REQUIRED for FAIL: how to fix
            ("notes", ""),
        ]))
    out = OrderedDict([
        ("standard", "OWASP ASVS"),
        ("version", data["Version"]),
        ("target_level", args.level),
        ("chapters", parse_chapters(args.chapter) or "ALL"),
        ("target", args.target or "<describe the app/repo under test>"),
        ("total_requirements", len(rows)),
        ("verdict_vocabulary", list(VERDICTS)),
        ("requirements", rows),
    ])
    text = json.dumps(out, indent=2, ensure_ascii=False)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print(f"wrote {len(rows)} requirements -> {args.out}")
    else:
        print(text)


def cmd_report(args):
    with open(args.checklist, encoding="utf-8") as fh:
        cl = json.load(fh)
    reqs = cl["requirements"]
    counts = Counter(r.get("verdict", "NEEDS-EVIDENCE") for r in reqs)
    total = len(reqs)
    # PASS/FAIL need evidence; N/A needs justification; FAIL needs remediation.
    problems = []
    for r in reqs:
        v = r.get("verdict")
        if v in ("PASS", "FAIL") and not str(r.get("evidence", "")).strip():
            problems.append(f"{r['id']}: verdict {v} with no evidence")
        if v == "N/A":
            evidence = r.get("evidence")
            if not isinstance(evidence, str) or not evidence.strip():
                problems.append(f"{r['id']}: N/A with no justification in evidence")
        if v == "FAIL" and not str(r.get("remediation", "")).strip():
            problems.append(f"{r['id']}: FAIL with no remediation")
        if v not in VERDICTS:
            problems.append(f"{r['id']}: invalid verdict '{v}'")
    verified = counts["PASS"] + counts["FAIL"] + counts["N/A"]
    print(f"# ASVS Attestation Summary — {cl.get('target','?')}")
    print(f"Standard: {cl.get('standard')} {cl.get('version')}  Target: {cl.get('target_level')}")
    print(f"Chapters: {cl.get('chapters')}\n")
    print(f"{'VERDICT':<16}{'COUNT':>6}{'PERCENT':>9}")
    for v in VERDICTS:
        pct = (counts[v] / total * 100) if total else 0
        print(f"{v:<16}{counts[v]:>6}{pct:>8.1f}%")
    print("-" * 31)
    print(f"{'TOTAL':<16}{total:>6}")
    cov = (verified / total * 100) if total else 0
    print(f"\nCoverage (verified, not NEEDS-EVIDENCE): {verified}/{total} = {cov:.1f}%")
    passable = counts["PASS"] + counts["N/A"]
    conf = (passable / total * 100) if total else 0
    print(f"Conformance (PASS+N/A of total):         {passable}/{total} = {conf:.1f}%")
    if counts["NEEDS-EVIDENCE"]:
        print(f"\n!! {counts['NEEDS-EVIDENCE']} requirement(s) NOT yet verified — "
              f"attestation is INCOMPLETE until these are resolved.")
    if problems:
        print(f"\n!! {len(problems)} integrity problem(s) — an honest attestation must fix these:")
        for p in problems[:50]:
            print(f"   - {p}")
    verdict = "INCOMPLETE" if (counts["NEEDS-EVIDENCE"] or problems) else (
        "CONFORMANT" if counts["FAIL"] == 0 else "NON-CONFORMANT")
    print(f"\nRESULT: {verdict} @ {cl.get('target_level')}")
    return 1 if problems else 0


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="asvs",
        description="OWASP ASVS 5.0 deterministic requirement engine")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("chapters", help="list the 17 chapters")
    sp.set_defaults(func=cmd_chapters)

    sp = sub.add_parser("stats", help="requirement counts per chapter for a level")
    sp.add_argument("--level", choices=LEVELS, default="L2")
    sp.add_argument("--chapter", help="comma-separated chapter codes, e.g. V6,V7")
    sp.set_defaults(func=cmd_stats)

    sp = sub.add_parser("list", help="list applicable requirements")
    sp.add_argument("--level", choices=LEVELS, default="L2")
    sp.add_argument("--chapter", help="comma-separated chapter codes, e.g. V6,V7")
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("scaffold", help="emit an attestation checklist (JSON)")
    sp.add_argument("--level", choices=LEVELS, default="L2")
    sp.add_argument("--chapter", help="comma-separated chapter codes, e.g. V6,V7")
    sp.add_argument("--target", help="name/description of the app under test")
    sp.add_argument("--out", help="output file (default: stdout)")
    sp.set_defaults(func=cmd_scaffold)

    sp = sub.add_parser("report", help="roll a filled checklist into a summary")
    sp.add_argument("--checklist", required=True, help="filled scaffold JSON")
    sp.set_defaults(func=cmd_report)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
