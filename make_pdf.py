#!/usr/bin/env python3
"""교안 HTML → 태블릿 필기용 PDF (A4 세로).

- 섹션마다 새 쪽에서 시작, 모든 쪽 오른쪽에 줄 메모 칸
- 탭·접기 내용은 모두 펼침
- 확인 문제는 동그라미 보기 + 힌트, 파트마다 정답·해설 쪽과 줄 노트 쪽

준비(처음 한 번):
  pip install playwright
  python -m playwright install chromium

사용법:
  python scripts/make_pdf.py 교안.html -o 교안.pdf
"""
import argparse, asyncio, pathlib, sys

PRINT_JS = r"""
() => {
  const esc = s => s;
  document.querySelectorAll(".topbar,.side,.deckbar,.backq,.toc,.hl-bar").forEach(e => e.remove());
  const lay = document.querySelector(".layout"); if (lay) lay.style.display = "block";
  document.querySelectorAll("details").forEach(d => d.open = true);
  document.querySelectorAll(".swap").forEach(sw => {
    const t = sw.querySelector(".swap-tabs"); if (t) t.remove();
    [...sw.children].filter(c => c.dataset && c.dataset.label).forEach(p => {
      p.hidden = false;
      const h = document.createElement("p"); h.className = "pl"; h.textContent = p.dataset.label; h.style.marginTop = "10px";
      p.before(h);
    });
  });
  const slide = id => document.getElementById(id);
  Object.keys(QUIZ).forEach((pid, pi) => {
    const box = document.querySelector(`.quiz[data-part="${pid}"]`), qs = QUIZ[pid].qs;
    const title = id => { const s = slide(id); const t = s && s.querySelector(".slide-title"); return t ? t.textContent : ""; };
    box.innerHTML = qs.map((q, i) => `<div class="pq"><p class="pq-q"><b>${i + 1}.</b> ${q.q}</p><ol class="pq-o">${q.o.map((o, k) => `<li><span class="pq-c">${k + 1}</span>${o}</li>`).join("")}</ol><p class="pq-h">힌트: ${q.h} <span>· 관련 슬라이드: ${title(q.r)}</span></p></div>`).join("");
    const sec = box.closest(".slide");
    const key = document.createElement("section"); key.className = "slide pkey";
    key.innerHTML = `<div class="slide-in"><p class="kicker"><span class="kn">파트 ${pi + 1} 정답과 해설</span></p><ol class="pk">${qs.map((q, i) => `<li><b>${i + 1}번 · 정답 ${q.a + 1}</b> ${q.o[q.a]}<br><span>${q.e}</span></li>`).join("")}</ol></div>`;
    sec.after(key);
    const note = document.createElement("section"); note.className = "slide pnote";
    note.innerHTML = `<div class="slide-in"><p class="kicker"><span class="kn">파트 ${pi + 1} 노트</span></p><div class="lines"></div></div>`;
    key.after(note);
  });
  document.querySelectorAll(".slide").forEach(s => s.hidden = false);
  const st = document.createElement("style");
  st.textContent = `
  @page{size:A4;margin:14mm 12mm 16mm 16mm}
  html,body{background:#fff!important}
  body{padding:0!important;font-size:11pt;line-height:1.7;color:#151922}
  :root{--paper:#fff;--bar-h:0px;--top-h:0px}
  .slide{display:block!important;min-height:0!important;break-before:page;page-break-before:always;background:#fff;padding-right:44mm;position:relative}
  .slide:first-child{break-before:auto}
  .slide-in,.cover-in{max-width:none!important;padding:0!important;animation:none!important}
  .slide-title{font-size:20pt;margin-bottom:14px;max-width:none}
  .slide-body>p:first-child:not([class]),.slide-body>.lead{font-size:12pt}
  .cover{border-top:0;display:block}
  .cover-in{min-height:250mm;display:flex;flex-direction:column;justify-content:space-between;border-top:5px solid #1F3FE0;padding-top:10mm!important}
  .cover-num{font-size:120pt}
  .cover.opening .cover-title{font-size:48pt}
  .cover-title{font-size:28pt}
  .cover-hint{display:none}
  .cover.opening#end .btn{display:none}
  pre{white-space:pre-wrap;word-break:break-all}
  .tw{overflow:visible}.tw table{min-width:0;font-size:9.5pt}
  .vs,.sflow,.goalgrid,.mapflow{break-inside:avoid}
  .vsteps>li,.tw tr,.pq,.pk li,.note,.tip,.warn{break-inside:avoid}
  .contents button{color:inherit}
  .pq{margin:0 0 16px;padding-bottom:12px;border-bottom:1px solid #DDE2E8}
  .pq-q{font-weight:500;margin:0 0 6px}
  .pq-o{list-style:none;margin:0 0 6px;padding:0}
  .pq-o li{display:flex;gap:10px;margin:0 0 3px}
  .pq-c{flex:none;width:1.5em;height:1.5em;border:1.5px solid #8A93A1;border-radius:50%;display:inline-grid;place-items:center;font-size:8.5pt;margin-top:2px}
  .pq-h{font-size:9pt;color:#5A6371;margin:0}
  .pk{list-style:none;margin:0;padding:0;border-top:2px solid #151922}
  .pk li{padding:9px 0;border-bottom:1px solid #DDE2E8;font-size:10pt}
  .pk b{color:#1A33B8;margin-right:6px}
  .pk span{color:#5A6371}
  .lines{height:235mm;background:repeating-linear-gradient(to bottom,transparent 0,transparent 9mm,#DDE2E8 9mm,#DDE2E8 calc(9mm + 1px))}
  .pnote{padding-right:0}
  .memo{position:fixed;top:0;right:0;bottom:0;width:38mm;border-left:1px solid #DDE2E8;
    background:repeating-linear-gradient(to bottom,transparent 0,transparent 9mm,#EEF1F5 9mm,#EEF1F5 calc(9mm + 1px))}
  .memo span{display:block;background:#fff;font-size:8pt;color:#8A93A1;padding:0 0 2mm 3mm}
  `;
  document.head.appendChild(st);
  const memo = document.createElement("div"); memo.className = "memo"; memo.innerHTML = "<span>메모</span>";
  document.body.appendChild(memo);
}
"""

def templates(course, module):
    font = "font-family:'IBM Plex Sans KR','Apple SD Gothic Neo','Malgun Gothic',sans-serif"
    hdr = (f'<div style="width:100%;font-size:7.5pt;color:#8A93A1;padding:0 12mm 0 16mm;{font}">'
           f'{course} / <b style="color:#151922">{module}</b></div>')
    ftr = (f'<div style="width:100%;font-size:7.5pt;color:#8A93A1;padding:0 12mm 0 16mm;{font};text-align:right">'
           '<span class="pageNumber"></span> / <span class="totalPages"></span></div>')
    return hdr, ftr

async def run(src, out):
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        sys.exit("playwright가 없어요. 먼저 실행하세요:\n  pip install playwright\n  python -m playwright install chromium")
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 900, "height": 1200})
        await pg.emulate_media(color_scheme="light")
        await pg.goto(src.resolve().as_uri())
        await pg.wait_for_timeout(1500)
        course = await pg.evaluate("(document.querySelector('.tb-course')||{}).textContent||''")
        module = await pg.evaluate("(document.querySelector('.tb-module')||{}).textContent||''")
        await pg.evaluate(PRINT_JS)
        await pg.wait_for_timeout(500)
        await pg.emulate_media(media="print", color_scheme="light")
        hdr, ftr = templates(course, module)
        await pg.pdf(path=str(out), format="A4", print_background=True, display_header_footer=True,
                     header_template=hdr, footer_template=ftr, prefer_css_page_size=True,
                     margin={"top": "14mm", "bottom": "16mm", "left": "16mm", "right": "12mm"})
        await b.close()

def main():
    ap = argparse.ArgumentParser(description="교안 HTML을 필기용 PDF로 만듭니다.")
    ap.add_argument("html")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    src = pathlib.Path(a.html)
    out = pathlib.Path(a.out) if a.out else src.with_suffix(".pdf")
    asyncio.run(run(src, out))
    print(f"완성: {out}")

if __name__ == "__main__":
    main()
