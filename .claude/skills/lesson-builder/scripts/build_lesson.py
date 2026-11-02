#!/usr/bin/env python3
"""lesson.json → 교안 HTML 한 파일.

사용법:
  python scripts/build_lesson.py lesson.json -o 교안.html

lesson.json 형식은 references/lesson-json.md 를 보세요.
"""
import argparse, html, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = HERE / "assets" / "template.html"


def esc(s):
    return html.escape(str(s), quote=False)


def js(obj):
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")


def fail(msg):
    sys.exit(f"[lesson.json 오류] {msg}")


def check(d):
    for k in ["course", "module", "title", "topic", "core", "goals", "map", "parts"]:
        if k not in d:
            fail(f"'{k}' 항목이 없어요.")
    if not 1 <= len(d["parts"]) <= 9:
        fail("parts는 1~9개여야 해요.")
    for n, p in enumerate(d["parts"], 1):
        for k in ["title", "short", "desc", "sections", "quiz"]:
            if k not in p:
                fail(f"파트 {n}에 '{k}'가 없어요.")
        for i, q in enumerate(p["quiz"], 1):
            for k in ["q", "o", "e"]:
                if k not in q:
                    fail(f"파트 {n} 문제 {i}에 '{k}'가 없어요.")
            if not 2 <= len(q["o"]) <= 4:
                fail(f"파트 {n} 문제 {i}: 보기는 2~4개여야 해요.")
            r = q.get("ref")
            if r is not None and not 1 <= int(r) <= len(p["sections"]):
                fail(f"파트 {n} 문제 {i}: ref {r}에 해당하는 섹션이 없어요.")


def build(d):
    P = d["parts"]
    total_q = sum(len(p["quiz"]) for p in P)
    S = []
    S.append(f'''<section class="slide cover opening" id="start" data-where="시작"><div class="cover-in">
<div class="cover-top"><span>{esc(d["course"])}</span><span>교안 · 퀴즈 {total_q}문항</span></div>
<div><h1 class="cover-title">{esc(d["title"])}</h1>
<p class="cover-sub">{esc(d.get("subtitle", ""))}</p></div>
<p class="cover-hint">아래로 내리며 읽어요. 왼쪽 학습 흐름에서 원하는 단원으로 바로 갈 수 있고, 본문 글자를 드래그하면 형광펜을 칠할 수 있어요.</p>
</div></section>''')
    S.append(f'''<section class="slide" id="topic" data-where="학습 주제"><div class="slide-in">
<p class="kicker"><span class="kn">오늘의 학습 주제</span></p>
<div class="slide-body" data-hl="topic" style="max-width:none">
<p class="topic-line">{esc(d["topic"])}</p>
<p class="pull">{d["core"]}</p>
{f"<p>{d['core_tail']}</p>" if d.get("core_tail") else ""}
</div></div></section>''')
    goals = "".join(f'<div><b>{esc(g["verb"])}</b><p>{g["text"]}</p></div>' for g in d["goals"])
    S.append(f'''<section class="slide" id="goals" data-where="학습 목표"><div class="slide-in">
<p class="kicker"><span class="kn">학습 목표</span></p>
<h2 class="slide-title">오늘이 끝나면 할 수 있는 {len(d["goals"])}가지</h2>
<div class="slide-body" data-hl="goals" style="max-width:none"><div class="goalgrid">{goals}</div></div>
</div></section>''')
    m = d["map"]
    layers = "".join(f'<div><b>{esc(x["name"])}</b><span>{x["desc"]}</span></div>' for x in m["layers"])
    steps = "".join(f'<li><b>{esc(x["name"])}</b><small>{esc(x.get("desc", ""))}</small></li>' for x in m.get("steps", []))
    S.append(f'''<section class="slide" id="map" data-where="큰 그림"><div class="slide-in">
<p class="kicker"><span class="kn">큰 그림</span></p>
<h2 class="slide-title">{esc(m["title"])}</h2>
<div class="slide-body" data-hl="map" style="max-width:none">
<div class="mapflow">{layers}</div>
{f'<p class="pl">{esc(m.get("steps_label", ""))}</p><ol class="sflow">{steps}</ol>' if steps else ""}
</div></div></section>''')
    cont = "".join(
        f'<li><button data-go="part{n}"><span class="cn">{n:02d}</span><span><span class="ct">{esc(p["title"])}</span>'
        f'<span class="cd">{esc(p["desc"])}</span><span class="cs">확인 문제 {len(p["quiz"])}문항</span></span></button></li>'
        for n, p in enumerate(P, 1))
    S.append(f'''<section class="slide" id="contents" data-where="차례"><div class="slide-in">
<p class="kicker"><span class="kn">차례</span></p>
<h2 class="slide-title">{len(P)}개의 파트, 파트마다 확인 문제</h2>
<ul class="contents">{cont}</ul>
</div></section>''')
    QUIZ, SHORT = {}, {"intro": "시작"}
    for n, p in enumerate(P, 1):
        pid, secs = f"part{n}", p["sections"]
        SHORT[pid] = p["short"]
        S.append(f'''<section class="slide cover" id="{pid}" data-where="파트 {n}"><div class="cover-in">
<div class="cover-top"><span>파트 {n} / {len(P)}</span><span>섹션 {len(secs)}개 · 확인 문제 {len(p["quiz"])}문항</span></div>
<p class="cover-num">{n:02d}</p>
<div><h2 class="cover-title">{esc(p["title"])}</h2><p class="cover-desc">{esc(p["desc"])}</p></div>
</div></section>''')
        for k, sec in enumerate(secs, 1):
            sid = f"{pid}-{k}"
            S.append(f'''<section class="slide" id="{sid}" data-where="파트 {n}"><div class="slide-in">
<p class="kicker"><span class="kn">파트 {n}</span><span>{esc(p["title"])}</span><span class="kc">{k} / {len(secs)}</span></p>
<h2 class="slide-title">{esc(sec["title"])}</h2>
<div class="slide-body" data-hl="{sid}">
{sec["html"]}
</div></div></section>''')
        S.append(f'''<section class="slide quizslide" id="{pid}-quiz" data-where="파트 {n} 확인 문제"><div class="slide-in">
<p class="kicker"><span class="kn">파트 {n} 확인 문제</span><span>{esc(p["title"])}</span></p>
<div class="quiz" data-part="{pid}"></div>
</div></section>''')
        last = n == len(P)
        QUIZ[pid] = {
            "qs": [{"q": q["q"], "o": q["o"], "a": 0, "e": q["e"], "h": q.get("hint", ""),
                    "r": f"{pid}-{q['ref']}" if q.get("ref") else ""} for q in p["quiz"]],
            "next": "end" if last else f"part{n + 1}",
            "nextLabel": "마치기" if last else f"파트 {n + 1}로",
        }
    sub = f'<p class="cover-sub">{esc(d["deadline"])}</p>' if d.get("deadline") else ""
    S.append(f'''<section class="slide cover opening" id="end" data-where="끝"><div class="cover-in">
<div class="cover-top"><span>{esc(d["title"])}</span><span>끝</span></div>
<div><h2 class="cover-title">수고했어요</h2>{sub}</div>
<div><p class="cover-hint" style="margin-bottom:16px">{d.get("closing", "")}</p>
<button class="btn blue" data-go="start">처음으로</button></div>
</div></section>''')
    t = TEMPLATE.read_text(encoding="utf-8")
    title = f'{d["module"]}'
    for k, v in {"{{TITLE}}": esc(title), "{{COURSE}}": esc(d["course"]), "{{MODULE}}": esc(d["module"]),
                 "{{SLIDES}}": "\n".join(S), "{{QUIZ}}": js(QUIZ), "{{SHORT}}": js(SHORT)}.items():
        t = t.replace(k, v)
    return t, total_q, sum(len(p["sections"]) for p in P)


def main():
    ap = argparse.ArgumentParser(description="lesson.json으로 교안 HTML을 만듭니다.")
    ap.add_argument("json")
    ap.add_argument("-o", "--out", default="lesson.html")
    a = ap.parse_args()
    d = json.loads(pathlib.Path(a.json).read_text(encoding="utf-8"))
    check(d)
    out, nq, ns = build(d)
    pathlib.Path(a.out).write_text(out, encoding="utf-8")
    print(f"완성: {a.out}  (파트 {len(d['parts'])}개, 섹션 {ns}개, 문제 {nq}개, {len(out) // 1024}KB)")


if __name__ == "__main__":
    main()
