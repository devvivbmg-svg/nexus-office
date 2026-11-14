# NEXUS AI FOOTBALL OFFICE — ตั้งค่าอัปเดตข้อมูลอัตโนมัติ

1. สร้าง repo ใหม่บน GitHub แล้วอัปโหลดไฟล์ในโฟลเดอร์นี้ทั้งหมด (รวม `.github/` และ `docs/`)
2. Settings → Pages → Source: Deploy from a branch → Branch: main, โฟลเดอร์ `/docs`
3. แท็บ Actions → daily-fixtures → Run workflow (รันครั้งแรกด้วยมือ) ตรวจว่าขึ้นเขียว และมีไฟล์ `docs/fixtures.json` ถูกอัปเดต
4. เปิดหน้า Pages ของ repo — แอปจะโหลด fixtures.json เองทุกครั้งที่เปิด และ GitHub จะรันดึงข้อมูลทุกวัน 08:00 น. (เวลาไทย; cron อาจช้าได้ไม่กี่นาที)

## หมายเหตุ
- ดึงเฉพาะ: ลีก ทีม เวลา ค่าราคาต่อรอง (AH) จากหน้าแรก goal7.co ไม่มีฟอร์ม/ข่าวเจ็บ/ราคาน้ำทศนิยม ต้องกรอกเพิ่มเอง คู่ที่ข้อมูลไม่ครบจะเป็น NO BET
- ตัวแยกข้อมูล (`scrape.py`) ผ่านการทดสอบกับข้อมูลตัวอย่างเท่านั้น ยังไม่ได้ทดสอบกับ HTML จริง ถ้า Actions ล้มเหลว ให้ดู log หรือรัน `python scrape.py --debug` แล้วส่ง `raw.html` มาให้ปรับ
- ตรวจเงื่อนไขการใช้งานของ goal7.co ก่อนใช้งานจริง และอย่าตั้งให้ดึงถี่เกินวันละครั้ง
- ทดสอบในเครื่อง: `pip install requests beautifulsoup4 && python scrape.py --selftest`
