"""앵커도서 챕터 규칙 검사.  사용: python3 check.py [챕터번호 ...]  (없으면 전체)"""
import json, re, sys, pathlib

import os
BOOK = os.environ.get("BOOK", "15소년표류기")
ROOT = pathlib.Path(__file__).resolve().parent.parent / BOOK
SPEC = {  # (min chars, max chars, max eojeol, end-form regex)
    "L1": (500, 800, 7, r"요"),
    "L2": (900, 1300, 10, r"(니다|니까|요)"),
    "L3": (1400, 2000, 14, None),
    "L4": (2000, 2800, 18, None),
}


def sentences(text):
    out = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        # 문장 끝(. ! ? …) 뒤에 따옴표가 붙을 수 있음
        for s in re.split(r'(?<=[.!?…])["”’]?\s+', line):
            s = s.strip().strip('"“”')
            if s:
                out.append(s)
    return out


def check(ch):
    rows, scene_lists, titles = [], [], []
    for lv, (lo, hi, maxe, _) in SPEC.items():
        p = ROOT / lv / f"{BOOK}_Ch{ch:02d}_{lv}.json"
        if not p.exists():
            rows.append(f"  {lv}: MISSING")
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        content = d["content"]
        title, _, body = content.partition("\n\n")
        n = len(body.replace("\n", ""))
        sents = sentences(body)
        lens = [len(s.split()) for s in sents]
        over = [s for s, l in zip(sents, lens) if l > maxe]
        quoted = sum(len(m) for m in re.findall(r'"[^"]*"', body))
        problems = []
        if not lo <= n <= hi:
            problems.append(f"분량 {n}자 (목표 {lo}~{hi})")
        if over:
            limit_ok = lv == "L3" and len(over) <= max(1, len(sents) // 10)
            if not limit_ok:
                problems.append(f"{maxe}어절 초과 {len(over)}문장: " + " | ".join(over[:4]))
        if title != d["chapter_title"]:
            problems.append("content 첫 줄 != chapter_title")
        if re.search(r"장면\s*\d", content):
            problems.append("'장면 N' 표기")
        if lv == "L1" and quoted / max(n, 1) < 0.3:
            problems.append(f"대화 비율 {quoted / n:.0%} (<30%)")
        if d.get("level") != lv:
            problems.append("level 필드 불일치")
        scene_lists.append(json.dumps(d["scene_list"], ensure_ascii=False))
        titles.append(d["chapter_title"])
        stat = f"{n}자, 문장 {len(sents)}, 최장 {max(lens) if lens else 0}어절, 대화 {quoted / max(n, 1):.0%}"
        rows.append(f"  {lv}: {'OK ' if not problems else 'FIX'} {stat}" + ("".join(f"\n      - {p}" for p in problems)))
    if len(set(scene_lists)) > 1:
        rows.append("  !! scene_list 가 레벨마다 다름")
    if len(set(titles)) > 1:
        rows.append("  !! chapter_title 이 레벨마다 다름")
    print(f"Ch{ch:02d}\n" + "\n".join(rows))


chs = [int(a) for a in sys.argv[1:]] or range(1, int(os.environ.get("NCH", 30)) + 1)
for c in chs:
    check(c)
