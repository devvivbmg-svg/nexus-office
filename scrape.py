#!/usr/bin/env python3
"""ดึงตารางบอลจาก goal7.co -> docs/fixtures.json (เฉพาะข้อมูลที่หน้าเว็บแสดงจริง)
ใช้: python scrape.py | python scrape.py --selftest | python scrape.py --debug (เก็บ raw.html)"""
import json, re, sys, datetime
URL = 'https://goal7.co/'
MON = {m: i + 1 for i, m in enumerate('มกราคม กุมภาพันธ์ มีนาคม เมษายน พฤษภาคม มิถุนายน กรกฎาคม สิงหาคม กันยายน ตุลาคม พฤศจิกายน ธันวาคม'.split())}
PRICE = re.compile(r'^(เสมอ|\d+(\.\d+)?(/\d+(\.\d+)?)?)$')
TIME = re.compile(r'^(\d{2}):(\d{2})$')
SCORE = re.compile(r'^\d+\s*-\s*\d+$|^\?\s*-\s*\?$')
JUNK = ('คนโหวด', 'ฟันธง', 'กราฟ7m', 'ยิงกัน', 'รอกัน', 'analyse', 'http', 'ทรรศนะ', 'ถ่ายทอดสด')
HEAD = re.compile(r'โปรแกรมฟุตบอล.*?(\d{1,2})\s*(\S+)\s*พ\.ศ\.\s*(\d{4})')

def clean(s):
    s = re.sub(r'^\[[^\]]*\]\s*', '', s.strip())
    return re.sub(r'\s*\[[^\]]*\]$', '', s).strip()

def parse(lines):
    out, lg, base, prev, n, i = [], '', None, '', len(lines), 0
    while i < n:
        s = lines[i]; m = HEAD.search(s)
        if m:
            if base: break  # หยุดเมื่อถึงวันถัดไป/วันก่อนหน้า
            if MON.get(m[2]): base = datetime.date(int(m[3]) - 543, MON[m[2]], int(m[1]))
        elif s.startswith('เวลา') and prev: lg = prev
        elif TIME.match(s) and base:
            hh, mm = int(s[:2]), int(s[3:]); teams, prices = [], []
            j = i + 1
            while j < n and not TIME.match(lines[j]) and not lines[j].startswith('เวลา') and not HEAD.search(lines[j]):
                t = lines[j].strip(); j += 1
                if not t or SCORE.match(t) or any(k in t for k in JUNK): continue
                if PRICE.match(t): prices.append(t)
                elif len(teams) < 2: teams.append(clean(t))
                else: j -= 1; break
            if len(teams) == 2 and all(teams):
                d = base + datetime.timedelta(days=1 if hh < 11 else 0)  # เว็บนับวันถึง ~11:00 ของวันถัดไป
                out.append({'lg': lg, 'h': teams[0], 'a': teams[1], 'ko': f'{d}T{hh:02d}:{mm:02d}', 'ah': prices})
            i = j - 1 if j > i + 1 else i
        if not TIME.match(s): prev = s
        i += 1
    return out

SAMPLE = """บอลวันนี้ โปรแกรมบอล ราคาบอล โปรแกรมฟุตบอล วันเสาร์ที่ 14 พฤศจิกายน พ.ศ.2569
ยูฟ่า เนชั่นส์ ลีก (UEFA Nations League 2026-27)
เวลา
เจ้าบ้าน
21:00
[76]โคโซโว
0.5
0.5/1
อิสราเอล[77]
? - ?
ฟันธงต่อโคโซโว ซัลโวชัย
[76]โคโซโว (75%) คนโหวด 3 คน
00:00
[19]นอร์เวย์
1.5/2
เวลส์[39]
ลีกวัน อังกฤษ (League One England)
เวลา
22:00
[9]เชฟฟิลด์ เว้นส์เดย์
เสมอ
0/0.5
พลีมัธ[5]
02:00
[D1-6] SV รีด
เฟริส เวียนนา[D2-2]
วิเคราะห์บอลวันนี้ โปรแกรมฟุตบอล วันศุกร์ที่ 13 พฤศจิกายน พ.ศ.2569
00:00
มอลโดว่า
คาซัคสถาน""".split('\n')

def main():
    if '--selftest' in sys.argv:
        r = parse(SAMPLE)
        for x in r: print(x)
        assert [(x['lg'][:6], x['h'], x['a'], x['ko']) for x in r] == [('ยูฟ่า ', 'โคโซโว', 'อิสราเอล', '2026-11-14T21:00'), ('ยูฟ่า ', 'นอร์เวย์', 'เวลส์', '2026-11-15T00:00'), ('ลีกวัน', 'เชฟฟิลด์ เว้นส์เดย์', 'พลีมัธ', '2026-11-14T22:00'), ('ลีกวัน', 'SV รีด', 'เฟริส เวียนนา', '2026-11-15T02:00')], 'selftest ล้มเหลว'
        print('selftest OK'); return
    import requests
    from bs4 import BeautifulSoup
    r = requests.get(URL, headers={'User-Agent': 'Mozilla/5.0 (NexusAIOffice personal use)'}, timeout=30)
    r.raise_for_status(); r.encoding = r.apparent_encoding or 'utf-8'
    if '--debug' in sys.argv: open('raw.html', 'w', encoding='utf-8').write(r.text)
    soup = BeautifulSoup(r.text, 'html.parser')
    for t in soup(['script', 'style']): t.decompose()
    lines = [l.strip() for l in soup.get_text('\n').split('\n') if l.strip()]
    fx = parse(lines)
    print(f'พบ {len(fx)} คู่')
    if not fx:
        open('raw.html', 'w', encoding='utf-8').write(r.text)
        sys.exit('ไม่พบคู่แข่งขัน: โครงหน้าเว็บอาจเปลี่ยน (บันทึก raw.html ไว้ตรวจ) — ไม่เขียนทับ fixtures.json')
    json.dump({'updated': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'source': URL, 'fixtures': fx},
              open('docs/fixtures.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

if __name__ == '__main__': main()
