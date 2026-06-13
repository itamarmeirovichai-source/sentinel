# DECISIONS.md — יומן החלטות Sentinel

פורמט: תאריך · החלטה · נימוק · סטטוס.

---

## 2026-06-13 · Phase 0 — מתודולוגיית המחקר
**החלטה:** מחקר תחרותי דרך 4 זרמים מקבילים (runtime security / identity+payments / standards+OSS / market+regulation), כל אחד מחזיר digest ממוקד עם מקורות אמיתיים בלבד.
**נימוק:** כיסוי רחב במהירות + הפרדה בין איסוף-מודיעין (delegated) לבין הסינתזה האסטרטגית ודירוג ה-wedge (נשאר אצלי).
**סטטוס:** ✅ הושלם → `RESEARCH.md`.

## 2026-06-13 · ממצא מרכזי — ה-wedge המקורי תפוס
**החלטה:** לא להיכנס דרך "Runtime Control Plane / AI firewall" גנרי כ-positioning ראשי.
**נימוק:** 9 רכישות ב-12 חודשים, OSS חינמי (NeMo/Guardrails AI), bundling בענן, ו-CodeIntegrity (seed) בונה מוצר כמעט-זהה. תחרות מול חינם + מאות מיליוני $.
**סטטוס:** ✅ הוכרע במחקר.

## 2026-06-13 · בחירת wedge — **מאושר** ✅
**החלטה:** wedge = **"compliance-grade flight recorder + kill switch"** — interception שמפיק audit trail חתום וממופה-רגולציה. **מוצר אופקי**, beachhead ראשון = סוכנים פיננסיים/מסחר אוטונומיים (MeiroX-style), ואז התרחבות.
**נימוק:** השכבה הכי פחות צפופה, מגובה ב-deadline רגולטורי (EU AI Act Art. 12 — 2.8.2026), בת-ביצוע לבנאי יחיד, וזורעת את ה-Trust Graph דרך הדאטה. ראה `RESEARCH.md` §8.
**סטטוס:** ✅ **אושר ע"י Itamar (2026-06-13).** עוברים ל-PRD.

## 2026-06-13 · Phase 1 — PRD
**החלטה:** הפרדה חדה: PRD מגדיר *מה* (תרחישים, scope, DoD); *איך* מיירטים (proxy/SDK/middleware) נדחה במכוון ל-ARCHITECTURE (נקודת החלטה נפרדת).
**נימוק:** מנגנון ה-interception הוא ההחלטה הארכיטקטונית הכי קשה-להפוך — לא לקבע אותה ב-PRD לפני שמציגים trade-offs.
**סטטוס:** ✅ `PRD.md` נכתב.

## החלטות פתוחות לנקודות הבאות
- בחירת stack (שפה / איך מיירטים — proxy vs SDK wrapper vs middleware / DB ל-audit) — **לשאול לפני בחירה** (Phase 2).
- האם MVP מתמקד בפרוטוקול אחד (MCP) או cross-protocol — לשאול (Phase 1/2).
