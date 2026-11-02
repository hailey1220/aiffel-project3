# 본문에 쓸 수 있는 요소

`sections[].html` 안에서 아래 클래스만 쓴다. 새 클래스나 인라인 스타일은 만들지 않는다.

| 쓰임 | 마크업 |
|---|---|
| 섹션 첫 문단(크고 회색) | `<p class="lead">…</p>` |
| 작은 소제목 | `<p class="pl">…</p>` |
| 표 (가로 스크롤 지원) | `<div class="tw"><table><tr><th>…</th></tr><tr><td>…</td></tr></table></div>` |
| 회색 메모 상자 | `<div class="note"><b>제목</b> · 내용</div>` |
| 팁 (연한 파랑) | `<div class="tip">…</div>` |
| 주의 (주황 선) | `<div class="warn">…</div>` |
| 비교 카드 2~3개 | `<div class="vs"><div><b>제목</b><p>…</p></div><div class="r">…</div></div>` (`r` 주황 위험, `n` 회색 중립) |
| 순서가 있는 세로 단계 | `<ol class="vsteps"><li><b>제목</b>설명</li></ol>` |
| 순서가 있는 가로 흐름 | `<ol class="sflow"><li><b>제목</b><small>설명</small></li></ol>` |
| 탭으로 바꿔 보기 | `<div class="swap"><div data-label="탭 이름">…</div><div data-label="…">…</div></div>` |
| 접어 두는 곁가지 | `<details class="fold"><summary>더 알아보기: …</summary><div class="fold-b">…</div></details>` |
| 코드 | `<p class="pl">파일 경로</p><pre><code>…</code></pre>` (`<` `>`는 `&lt;` `&gt;`) |
| 체크리스트 | `<ul class="goals"><li><span>…</span></li></ul>` |
| 용어 밑줄 강조 | `<span class="tg f">…</span>` (`b` 이중선, `d` 점선) |

규칙:
- 번호(vsteps, sflow)는 **순서가 있을 때만** 쓴다. 순서 없는 목록은 `ul`
- 출처는 문단 끝에 `(출처: …)` 로 짧게
- 따옴표는 ‘ ’ “ ” 를 쓴다 (코드 안은 제외)
