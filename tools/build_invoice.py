#!/usr/bin/env python3
# 從財政部 RSS 抓統一發票中獎號碼,寫到 app/data/invoice.json
import datetime, json, os, re, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('INVOICE_OUT') or os.path.join(HERE, '..', 'app', 'data', 'invoice.json')
RSS = 'https://invoice.etax.nat.gov.tw/invoice.xml'
KEEP = 3

def claim(year, end_month):
    # 開獎月的次月 6 日起,領三個月
    y, m = year + 1911, end_month + 2
    if m > 12:
        y, m = y + 1, m - 12
    e_y, e_m = (y + 1, m + 3 - 12) if m + 3 > 12 else (y, m + 3)
    return f'{y}-{m:02d}-06', f'{e_y}-{e_m:02d}-05'

def main():
    xml = urllib.request.urlopen(RSS, timeout=30).read().decode('utf8')
    periods = []
    for title, desc in re.findall(r'<title><!\[CDATA\[(\d+年[^\]]*)\]\]></title>.*?<description><!\[CDATA\[(.*?)\]\]>', xml, re.S):
        y, m2 = re.match(r'(\d+)年\s*\d+~(\d+)月', title).groups()
        sp = re.search(r'特別獎:?：?(\d{8})', desc).group(1)
        gr = re.search(r'特獎:?：?(\d{8})', desc.replace('特別獎', '')).group(1)
        fi = re.findall(r'\d{8}', desc.split('頭獎')[1])
        assert len(fi) >= 3
        start, end = claim(int(y), int(m2))
        periods.append({'t': title.replace(' ', ' '), 'sp': sp, 'gr': gr, 'fi': fi, 'from': start, 'to': end})
    assert periods
    data = {'checked': datetime.date.today().isoformat(), 'periods': periods[:KEEP]}
    json.dump(data, open(OUT, 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
    print(json.dumps(data, ensure_ascii=False)[:400])

if __name__ == '__main__':
    main()
