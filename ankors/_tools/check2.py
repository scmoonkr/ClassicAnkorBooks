"""부가 콘텐츠 검사.  사용: python3 check2.py [챕터번호 ...]  (없으면 전체)"""
import json, sys, pathlib

import os
BOOK = os.environ.get("BOOK", "15소년표류기")
ROOT = pathlib.Path(__file__).resolve().parent.parent / BOOK
LEVELS = ["L1", "L2", "L3", "L4"]
QUIZ_COUNT = {"ox": 6, "chosung": 5, "fill_blank": 3, "who_said": 2, "sequence": 1}
CHO = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"


def chosung(s):
    out = []
    for c in s:
        code = ord(c) - 0xAC00
        out.append(CHO[code // 588] if 0 <= code < 11172 else c)
    return "".join(out)


def norm(s):
    return " ".join(s.split())


def check_level(d, lv, intro0):
    p = []
    body = norm(d["content"])
    scenes = {s["scene"] for s in d["scene_list"]}

    it = d.get("intro_static") or {}
    for k in ["summary", "characters", "background", "reading_point", "pre_reading_hook", "pre_reading_avoid"]:
        if not it.get(k):
            p.append(f"intro_static.{k} 없음")
    if set((it.get("reading_point") or {}).keys()) != set(LEVELS):
        p.append("reading_point 에 L1~L4 가 다 있어야 함")
    if intro0 is not None and it != intro0:
        p.append("intro_static 이 L1 파일과 다름 (네 레벨 동일해야 함)")

    sh = d.get("sharing") or {}
    qs = sh.get("anchor_quotes") or []
    if not 2 <= len(qs) <= 5:
        p.append(f"anchor_quotes {len(qs)}개")
    for q in qs:
        if norm(q) not in body:
            p.append(f"anchor_quote 본문에 없음: {q[:40]}")
    types = {q.get("type") for q in sh.get("questions") or []}
    if not {"scene", "emotion", "choice"} <= types:
        p.append(f"sharing.questions 타입 부족: {types}")

    db = d.get("debate") or []
    if len(db) != 5 or [x.get("id") for x in db] != [1, 2, 3, 4, 5]:
        p.append(f"debate {len(db)}개 / id 1~5 아님")
    if sorted(x.get("type") for x in db) != ["A", "A", "A", "B", "C"]:
        p.append("debate type 구성 A3·B1·C1 아님")
    for x in db:
        for k in ["topic", "background", "level_hint"]:
            if not x.get(k):
                p.append(f"debate {x.get('id')} {k} 없음")
        if x.get("type") == "A" and not (x.get("pro_label") and x.get("con_label")):
            p.append(f"debate {x.get('id')} A 타입 pro/con 없음")
        if set((x.get("level_hint") or {}).keys()) != set(LEVELS):
            p.append(f"debate {x.get('id')} level_hint L1~L4 아님")

    ps = d.get("problem_solve") or []
    if len(ps) != 5 or [x.get("id") for x in ps] != [1, 2, 3, 4, 5]:
        p.append(f"problem_solve {len(ps)}개 / id 1~5 아님")
    for x in ps:
        for k in ["title", "connected_scene", "intro", "key_question"]:
            if not x.get(k):
                p.append(f"problem_solve {x.get('id')} {k} 없음")
        if x.get("connected_scene") not in scenes:
            p.append(f"problem_solve {x.get('id')} connected_scene 이 scene_list 와 다름")

    qz = d.get("quiz") or []
    cnt = {}
    for i, q in enumerate(qz, 1):
        t = q.get("type")
        cnt[t] = cnt.get(t, 0) + 1
        tag = f"quiz#{i}({t})"
        if q.get("usage") != "game" or q.get("level") != lv:
            p.append(f"{tag} usage/level 오류")
        if q.get("difficulty") not in ("easy", "medium", "hard"):
            p.append(f"{tag} difficulty 오류")
        if not q.get("question") or not q.get("hint"):
            p.append(f"{tag} question/hint 없음")
        a = q.get("answer")
        if t == "ox" and not isinstance(a, bool):
            p.append(f"{tag} answer 가 bool 아님")
        if t == "chosung" and q.get("chosung") != chosung(a or ""):
            p.append(f"{tag} 초성 불일치 {a} → {chosung(a or '')} != {q.get('chosung')}")
        if t == "fill_blank":
            qq = q.get("question", "")
            if qq.count("____") != 1 or norm(qq.replace("____", str(a))) not in body:
                p.append(f"{tag} 빈칸 복원 문장이 본문에 없음: {qq[:40]}")
        if t == "who_said":
            if norm(q.get("question", "")) not in body:
                p.append(f"{tag} 대사가 본문에 없음: {q.get('question', '')[:40]}")
            if a not in (q.get("options") or []):
                p.append(f"{tag} options 에 정답 없음")
        if t == "sequence":
            items, ans = q.get("items") or [], a or []
            if len(items) != 4 or sorted(items) != sorted(ans) or items == ans:
                p.append(f"{tag} items/answer 4개·같은 집합·섞인 순서여야 함")
    if cnt != QUIZ_COUNT:
        p.append(f"quiz 구성 {cnt}")
    oxa = [q.get("answer") for q in qz if q.get("type") == "ox"]
    if oxa.count(True) < 2 or oxa.count(False) < 2:
        p.append("ox 정답이 한쪽으로 치우침")
    return p


def check(ch):
    rows, intro0 = [], None
    for lv in LEVELS:
        f = ROOT / lv / f"{BOOK}_Ch{ch:02d}_{lv}.json"
        d = json.loads(f.read_text(encoding="utf-8"))
        probs = check_level(d, lv, intro0)
        if lv == "L1":
            intro0 = d.get("intro_static")
        rows.append(f"  {lv}: " + ("OK" if not probs else "FIX" + "".join(f"\n      - {x}" for x in probs)))
    print(f"Ch{ch:02d}\n" + "\n".join(rows))


for c in [int(a) for a in sys.argv[1:]] or range(1, int(os.environ.get("NCH", 30)) + 1):
    check(c)
