# 앵커도서 한 권 제작 절차 (세션용)

『15소년 표류기』·『80일간의 세계 일주』를 만든 방식을 정리한 문서다. 기준 문서는 같은 폴더의 `ANCHOR_GUIDE.md`이고, 이 문서는 그 지침을 실제로 돌리는 순서와 검사 방법을 적는다.

## 0. 준비

- 원전: `ankors/text/` 의 원문 파일을 쓴다. 원전 없이 기억만으로 쓰지 않는다.
- 스킬: `krin-l1-writing` ~ `krin-l4-writing`, `humanizer-korean` 을 불러서 따른다. 세션에서 Skill 도구로 불러오고, 작성자(서브에이전트)에게는 스킬 내용을 읽게 한다.
- 분량: **L4 기준 약 220쪽(1쪽 ≈ 600자 → L4 약 13만 자) → 약 55장.** 장당 L4 2,000~2,800자(지침 3장).
  - 원작 장이 55개보다 많으면 묶고, 적으면 나눈다. 원작 전체 줄거리를 처음부터 끝까지 다룬다.
- 파일: `ankors/{책폴더}/{L1|L2|L3|L4}/{책폴더}_Ch{NN}_{L}.json` (지침 6장 형식, `status: "draft"`, `reviewed: false`).
  - 장 번호는 두 자리(`Ch01`~`Ch55`). 100장 이상이면 세 자리로 바꾸고 검사 스크립트도 맞춘다.

## 1. 설계 (먼저, 사람이 확인할 수 있게 파일로)

`ankors/{책폴더}/_design.md` 를 만든다.
- 원작 장 ↔ 앵커 장 대응표 (어느 원작 장을 몇 장으로 묶거나 나눴는지)
- 장마다: 장 제목(결말을 드러내지 않게), 장면 3~7개(한 문장, ~함 체, type: 배경·사건·갈등·절정·복선·결말, 핵심 장면은 `절정`)
- **표기 통일표**: 인물·지명·배·동물·사물의 한글 표기. 모든 레벨에서 같은 표기를 쓴다.
- 민감한 내용 처리 원칙: 원작의 시대적 편견 표현(인종·민족·종교 비하)은 옮기지 않고 사실만 남긴다. 죽음·폭력·자살 언급은 L1·L2 에서 자극 없이, L3·L4 도 순화. 결말·반전은 해당 장 전에는 드러내지 않는다.

## 2. 본문 (장마다 L4 → L3 → L2 → L1)

- 원전의 그 장을 끝까지 읽고 쓴다. 원작에 없는 사건·인물을 지어내지 않는다. 원작과 설계가 어긋나면 원작을 따른다.
- L4 를 먼저 쓰고, L3·L2·L1 은 L4 를 줄이지 말고 같은 장면을 그 레벨 기준으로 **새로** 쓴다.
- 다 쓴 뒤 humanizer-korean 기준으로 다듬는다 (번역투, AI 상투어, "~것이다" 남발, 과한 쉼표·대시).
- content 형식: 첫 줄 장 제목, 빈 줄, 본문. 문단 사이 `\n`, 장면 사이 빈 줄 `\n\n`. "장면 1." 같은 표기·해설·주석 금지. 대화는 큰따옴표.
- 대화 비율 목표: L1 33~40%, L2 20~30%, L3 15% 이상.
- 저장은 Python `json.dump(ensure_ascii=False, indent=2)`.

검사 (모두 OK 가 될 때까지, 장·레벨당 최대 3회):
```bash
BOOK={책폴더} NCH={장 수} python3 ankors/_tools/check.py [장번호 ...]
```
분량·문장당 어절 수·L1 대화 비율·네 레벨 scene_list/chapter_title 일치·"장면 N" 표기를 본다.

## 3. 부가 콘텐츠 (본문이 검사를 통과한 장만)

다섯 필드: `intro_static` · `sharing` · `quiz` · `debate` · `problem_solve` (지침 7~9장). content·scene_list·chapter_title 은 바꾸지 않는다.

- `intro_static`: 네 레벨 파일에 **같은 객체**. reading_point 에 L1~L4 모두. characters 는 L1 본문에도 나오는 인물 위주. background 의 연도·날짜는 원작 기준. `pre_reading_avoid` 에는 뒤 장 사건과 결말·반전을 넣는다(마지막 장은 그 장의 결말).
- `sharing`: 레벨마다 따로. anchor_quotes 3개는 그 레벨 본문에 **글자 그대로** 있는 문장. questions 는 scene·emotion·choice 각 1개 이상.
- `debate`: 레벨마다 5개 (type A 3·B 1·C 1, id 1~5). B·C 는 pro_label/con_label 을 `""`. background 는 그 레벨 본문에 있는 사실만, 그 레벨 말투로. level_hint 에 L1~L4.
- `problem_solve`: 레벨마다 5개 (id 1~5). connected_scene 은 scene_list 의 scene 문자열과 **완전히 같게**.
- `quiz`: 레벨마다 17문항, 순서대로 ox 6 → chosung 5 → fill_blank 3 → who_said 2 → sequence 1. 공통 필드 `type`, `usage: "game"`, `level`, `question`, `answer`, `hint`, `difficulty`(easy/medium/hard).
  - ox: answer 는 true/false, 참·거짓 각 2개 이상.
  - chosung: `chosung` 필드는 answer 의 초성(띄어쓰기 유지).
  - fill_blank: question 은 본문 문장에서 한 단어를 `____` 로 바꾼 것. `____` 에 answer 를 넣으면 본문 글자 그대로 (조사 주의).
  - who_said: question 은 본문 대사 그대로(따옴표 없이), answer 는 화자, `options` 4개(answer 포함). **본문에 화자가 분명히 드러난 대사만**, options 는 그 레벨 본문에 나오는 인물만.
  - sequence: `items` 4개(섞은 순서), `answer` 는 같은 4개의 올바른 순서. 같은 시간에 따로 일어난 일을 섞지 않는다.
  - 정답은 **그 레벨 본문만 보고** 알 수 있고 하나여야 한다. hint 도 그 레벨 본문에 있는 정보로만.
  - 한 문항의 정답(초성·빈칸)이 같은 파일의 다른 문항 문장·힌트에 드러나지 않게 한다.

검사 (모두 OK, leaks: 0 이 될 때까지):
```bash
BOOK={책폴더} NCH={장 수} python3 ankors/_tools/check2.py [장번호 ...]
BOOK={책폴더} python3 ankors/_tools/leak2.py [장번호 ...]
```
기계 검사 뒤, 퀴즈 문항마다 "그 레벨 본문만 보고 답할 수 있는가, 정답이 하나인가"를 직접 확인한다.

## 4. 진행 방식

- 작성자(서브에이전트) 여러 명에게 장을 나눠 맡긴다 (한 명당 5~7장). 공통 브리프(이 문서 + `_design.md` + 스킬)를 읽게 한다.
- 본문 묶음이 검사를 통과할 때마다 커밋·푸시하고, 그 묶음의 부가 콘텐츠를 이어서 맡긴다.
- 끝나면 전체 검사 세 가지를 다시 돌리고, 원작과 설계가 어긋난 점·표기 결정·남은 문제를 정리한다.
