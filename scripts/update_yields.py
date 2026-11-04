"""국고채 3년·10년 일별 금리를 받아 index.html의 <script id="market"> 블록을 갱신한다.

1순위: 네이버 증권 (KR3YT=RR, KR10YT=RR, 장 마감 후 당일 종가)
2순위: 한국은행 ECOS 817Y002 시장금리(일별) — 환경변수 ECOS_API_KEY가 없으면 sample 키
매번 최근 약 130일치를 같은 출처로 다시 받아 통째로 바꾼다(출처 혼합 방지).
"""
import json, os, re, sys, urllib.request
from datetime import datetime, timedelta, timezone

PATH = "index.html"
KST = timezone(timedelta(hours=9))
DAYS = 130
UA = {"User-Agent": "Mozilla/5.0 (ktb10y yield updater)"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def naver(code, since):
    out = {}
    for page in range(1, 8):
        rows = get(f"https://api.stock.naver.com/marketindex/bond/{code}/prices?page={page}&pageSize=60")
        if not rows:
            break
        for r in rows:
            out[r["localTradedAt"][:10]] = float(r["closePrice"])
        if min(out) < since:
            break
    return out


def ecos(item, since):
    key = os.environ.get("ECOS_API_KEY") or "sample"
    start, end = since.replace("-", ""), datetime.now(KST).strftime("%Y%m%d")
    out, i = {}, 1
    while True:
        j = get(f"https://ecos.bok.or.kr/api/StatisticSearch/{key}/json/kr/{i}/{i + 9}/817Y002/D/{start}/{end}/{item}")
        s = j.get("StatisticSearch")
        if not s:
            break
        for r in s["row"]:
            t = r["TIME"]
            out[f"{t[:4]}-{t[4:6]}-{t[6:]}"] = float(r["DATA_VALUE"])
        i += 10
        if i > int(s["list_total_count"]):
            break
    return out


SOURCES = [
    ("네이버 증권", lambda s: (naver("KR3YT=RR", s), naver("KR10YT=RR", s))),
    ("한국은행 ECOS", lambda s: (ecos("010200000", s), ecos("010210000", s))),
]


def main():
    now = datetime.now(KST)
    since = (now - timedelta(days=DAYS)).strftime("%Y-%m-%d")
    today = now.strftime("%Y-%m-%d")
    for name, fn in SOURCES:
        try:
            y3, y10 = fn(since)
            days = sorted(d for d in set(y3) & set(y10) if since <= d <= today)
            if len(days) >= 20:
                break
            print(f"{name}: 데이터 부족 ({len(days)}일)", file=sys.stderr)
        except Exception as e:  # noqa: BLE001
            print(f"{name} 실패: {e}", file=sys.stderr)
    else:
        raise SystemExit("금리 데이터를 가져오지 못함")
    rows = [[d, round(y3[d], 3), round(y10[d], 3)] for d in days]
    block = json.dumps({"updated": now.strftime("%Y-%m-%d %H:%M KST"), "source": name, "rows": rows},
                       ensure_ascii=False, separators=(",", ":"))
    html = open(PATH, encoding="utf-8").read()
    new, n = re.subn(r'(<script type="application/json" id="market">)(.*?)(</script>)',
                     lambda m: m.group(1) + block + m.group(3), html, flags=re.S)
    if n != 1:
        raise SystemExit("index.html에서 market 블록을 찾지 못함")
    open(PATH, "w", encoding="utf-8").write(new)
    print(f"{name}: {rows[0][0]} ~ {rows[-1][0]} {len(rows)}일, 최근 3년 {rows[-1][1]} / 10년 {rows[-1][2]}")


if __name__ == "__main__":
    main()
