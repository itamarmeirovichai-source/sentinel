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

## 2026-06-13 · Phase 2 — Stack ו-Interception — **מאושר** ✅
**החלטה:** Python 3.11+ · interception = **SDK wrapper** מאחורי `Interceptor` interface (MCP-proxy כ-adapter עתידי) · audit = **SQLite + hash-chain** · policy = **YAML** · API = **FastAPI** + dashboard מינימלי · בדיקות = **pytest**.
**נימוק:** ה-beachhead (סוכנים פיננסיים/MeiroX) משתמש ב-tools של קריאות ישירות, לא MCP — SDK wrapper מכסה אותם, framework-agnostic, ודטרמיניסטי ל-tests-first. עקרונות: default-deny, fail-closed, append-only. ראה `ARCHITECTURE.md`.
**סטטוס:** ✅ אושר ע"י Itamar. עוברים לבנייה (Phase 3).

## עקרונות אבטחה שנקבעו (מחייבים את כל הקוד)
- **Fail-closed:** חריגה בליבת ההכרעה → block, לא execute.
- **Default-deny:** אין כלל מתאים → block.
- **Tests-first** על policy / kill switch / audit-integrity (קוד קריטי).
- **Sentinel עצמו = משטח תקיפה** — threat model ב-`ARCHITECTURE.md` §6.

## 2026-06-13 · Phase 3 — שינוי כפוי: HTTP layer
**החלטה:** נבדק ש-FastAPI+uvicorn+pydantic מותקנים נקי על Python 3.14.3 → נשארנו עם FastAPI כמתוכנן (לא נפלנו ל-stdlib).
**נימוק:** הסיכון היה wheels חסרים ל-3.14; אומת בפועל לפני התחייבות.
**סטטוס:** ✅

## 2026-06-13 · Phase 4 — בדיקות, demo, אבטחה — הושלם
**החלטה:** 32 טסטים עוברים; E2E demo (5 תרחישים) עובד; tamper detection אומת חי; compliance export עובד; self-security check נקי (`SECURITY.md`).
**הערה כנה:** ה-dashboard אומת פונקציונלית (טסטים + curl חי), אבל ה-preview-MCP לא הצליח להריץ אותו כי ה-sandbox חוסם גישה ל-.venv — מגבלת סביבה, לא באג. רץ תקין תחת `sentinel serve`.
**סטטוס:** ✅ MVP הושלם.

## 2026-06-13 · Post-MVP — הכל חוץ מחיבור MeiroX (לבקשת Itamar)
**החלטה:** Itamar בחר לבצע את כל ההמשך **חוץ** מחיבור הבוט האמיתי — "רק בנינו את זה, אני לא סומך על זה ב-100%". החלטה נכונה: לא לשים שכבת בקרה לא-בדוקה לפני כסף אמיתי. תואם [[feedback_account_anxiety]].
**בוצע ב-3 workstreams:**
- **A (הקשחה):** auth לדאשבורד (Bearer token, `SENTINEL_API_TOKEN`), rate-limit מתמשך (SQLite), two-phase logging (intent+outcome, action_id), approval flow (HITL — park→approve→run-once).
- **B (MCP-proxy):** `MCPProxy` מעל `Sentinel.enforce` משותף (refactor) — אין נתיב bypass.
- **C (OSS):** Apache-2.0, OTel GenAI export (`gen_ai.*`), CI (3.11–3.13), classifiers, CHANGELOG.
**סטטוס:** ✅ 51 טסטים עוברים. חיבור MeiroX נדחה במכוון עד שיש אמון מוכח.

## 2026-06-13 · "תמשיך עד המטרה" — monitor mode, MCP server, OTel SDK, wheel
**החלטה:** להמשיך אוטונומית עד סגירת כל הסקופ הבר-בנייה (בלי MeiroX, בלי פרסום חיצוני שדורש הרשאות).
- **Monitor mode** (`mode="monitor"` / `SENTINEL_MODE=monitor`): observe-only — מתעד את ההכרעה-שהייתה אבל לא חוסם; ה-kill switch עדיין אוכף. גשר האמון: אפשר "shadow" על סוכן אמיתי בלי סיכון — בלי לגעת ב-MeiroX החי.
- **SentinelMCPServer**: שרת MCP אמיתי (חבילת `mcp`, optional extra) שחושף tools עם אכיפה מובנית; `handle_call` טהור ונבדק בלי תלות ב-mcp.
- **OTel SDK exporter** (`record_spans`, extra `otel`): פולט spans אמיתיים, לא רק JSON.
- **wheel + sdist** נבנו ואומתו בהתקנה ל-venv נקי → `pip install sentinel` עובד.
**סטטוס:** ✅ 58 טסטים. נשאר רק לא-קוד (design partner אמיתי) + פרסום PyPI (דורש חשבון — לא מבוצע אוטומטית).
