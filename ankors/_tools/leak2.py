"""정답 노출 검사. 사용: BOOK=책폴더 python3 leak2.py [장번호 ...]
초성·빈칸 정답(본문에 3번 미만 나오는 2글자 이상 단어)이 같은 레벨 파일의 다른 문항(ox·chosung·fill_blank·who_said)
question/hint 에 그대로 나오면 출력한다. 0건이 될 때까지 고친다. (sequence items 는 검사하지 않는다)"""
import json, os, sys, pathlib
book = os.environ.get("BOOK", "15소년표류기")
root = pathlib.Path(__file__).resolve().parent.parent / book
chs = [int(a) for a in sys.argv[1:]]
tot = 0
for f in sorted(root.glob("L*/*.json")):
    ch = int(f.stem.split("_Ch")[1][:2])
    if chs and ch not in chs:
        continue
    d = json.loads(f.read_text(encoding="utf-8"))
    qz, body = d.get("quiz") or [], d["content"]
    for i, q in enumerate(qz):
        if q.get("type") not in ("chosung", "fill_blank"):
            continue
        a = str(q["answer"])
        if len(a) < 2 or body.count(a) >= 3:
            continue
        for j, o in enumerate(qz):
            if i == j or o.get("type") == "sequence":
                continue
            if a in str(o.get("question", "")) + " " + str(o.get("hint", "")):
                tot += 1
                print(f"{f.name}: #{i+1} {q['type']} 정답 '{a}' 가 #{j+1} {o['type']} 에 보임: {o.get('question','')[:50]} / hint: {o.get('hint','')[:40]}")
print("leaks:", tot)
