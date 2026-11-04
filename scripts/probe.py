import urllib.request, sys
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"}
urls=[
 "https://m.stock.naver.com/front-api/marketIndex/prices?category=bond&reutersCode=KR10YT%3DRR&page=1&pageSize=5",
 "https://m.stock.naver.com/front-api/marketIndex/prices?category=bond&reutersCode=KR3YT%3DRR&page=1&pageSize=5",
 "https://api.stock.naver.com/marketindex/bond/KR10YT=RR/prices?page=1&pageSize=5",
 "https://m.stock.naver.com/front-api/marketIndex/productDetail?category=bond&reutersCode=KR10YT%3DRR",
 "https://finance.naver.com/marketindex/interestDailyQuote.naver?marketindexCd=IRR_GOVT03Y&page=1",
 "https://finance.naver.com/marketindex/interestDailyQuote.naver?marketindexCd=IRR_GOVT10Y&page=1",
 "https://ecos.bok.or.kr/api/StatisticSearch/sample/json/kr/1/5/817Y002/D/20261001/20261104/010210000",
]
for u in urls:
    print("==",u)
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=20).read()
        for enc in ("utf-8","euc-kr"):
            try: t=r.decode(enc);break
            except: pass
        import re
        if "<html" in t[:500].lower() or "<table" in t: 
            i=t.find("<tbody");print(re.sub(r"\s+"," ",t[i:i+1200]))
        else: print(t[:900])
    except Exception as e: print("ERR",e)
