# PRD.md — Sentinel MVP

> v0.1 · Phase 1 · wedge מאושר (2026-06-13): **compliance-grade flight recorder + kill switch**.
> מסמך זה מגדיר את ה-MVP של ה-wedge הנבחר **בלבד**. כל מה שמעבר — ב-`ROADMAP.md`.

---

## 1. המשפט האחד

Sentinel יושב בין סוכן AI ל-tools שלו, **אוכף מדיניות** על כל פעולה לפני שהיא קורית, **רושם** אותה ל-audit trail חתום ובלתי-ניתן-לשינוי שאפשר לשחזר ולייצא כ**ראיית compliance**, ומאפשר **kill מיידי** של הסוכן.

## 2. הבעיה (מגובה ב-`RESEARCH.md` §3,§5)

צוותים שפורסים סוכנים אוטונומיים לא מצליחים לקבל אישור להרחיב את האוטונומיה לפעולות בעלות-סיכון (מסחר, billing, כתיבה ל-prod DB) כי:
- **אין רשומה audit-grade** של מה הסוכן עשה — *"רוב ההנהלות לא יאשרו הרחבת סוכנים בלי audit trail."*
- **אין אכיפה** של מה מותר לסוכן — prompt injection הופך סוכן עם הרשאות לכלי תקיפה (EchoLeak, Replit מחק prod DB).
- **אין עצירה מיידית** כשמשהו משתבש.
- **רגולציה מחייבת:** EU AI Act Art. 12 דורש automatic event logging למערכות high-risk — אכיפה מ-**2.8.2026**. קנס עד €35M/7%.

## 3. משתמש היעד

**Beachhead (ה-MVP מכוון אליו):** מפעיל סוכן פיננסי/מסחר אוטונומי — בדיוק העולם של MeiroX, שם audit + kill switch אינם רשות אלא חובה, והכאב חד היום.

| Persona | מי | הכאב | מה Sentinel נותן לו |
|---|---|---|---|
| **A — המפעיל/מהנדס** | מי שמריץ את הסוכן בייצור | "מה הסוכן עשה בלילה? איך אני עוצר אותו עכשיו?" | feed חי, kill switch, policy שחוסם פעולות מסוכנות |
| **B — בעל Risk/Compliance** | מי שחותם על הפריסה | "איך אני מוכיח לרגולטור/לבוס מה קרה?" | audit trail חתום, ניתן-לשחזור, ממופה ל-Art.12 |

**הרחבה עתידית (לא ב-MVP):** כל צוות שמריץ סוכן בייצור הנוגע ב-tools רגישים (DB, payments, email, code-exec).

## 4. Value proposition

> "שים את Sentinel בין הסוכן ל-tools שלו. כל פעולה נבדקת מול ה-policy שלך, נרשמת ל-trail חתום שאפשר לשחזר, ואתה יכול לעצור הכל בלחיצה. עכשיו אתה יכול **להוכיח** מה הסוכן עשה — לעצמך, לבוס, ולרגולטור."

הבידול: אנחנו מוכרים את ה-**פלט** (ראיית compliance + שליטה דטרמיניסטית), לא עוד מסנן prompt-injection. זה מבדל מ-9 הרוכשים ומ-CodeIntegrity, ומ-observability (Langfuse/Datadog) — שם הבידול הוא **tamper-evident + מיפוי רגולטורי + export**, לא tracing.

## 5. Scope — מה בפנים (IN)

1. **Interception layer** — יירוט כל tool call של סוכן. (המנגנון המדויק — proxy / SDK wrapper / middleware — נקבע ב-`ARCHITECTURE.md`.) עדיפות: Python tools + משטח MCP.
2. **Policy engine** — מדיניות declarative ב-YAML, **default-deny**. כללים לפי: שם tool, ספי ארגומנטים (`amount > 500`), rate limit (`N/min`), והכרעות `allow | block | require_approval`.
3. **Audit trail** — append-only, **hash-chained** (כל רשומה = `H(prev_hash + payload)` → tamper-evident), redaction אוטומטי של סודות, ניתן לשחזור (replay) וייצוא (JSON/דוח).
4. **Kill switch** — עצירה מיידית של כל פעולות סוכן/session; פעולות פתוחות מסומנות; **hook** ל-rollback של פעולות הפיכות (לא undo קסם).
5. **Anomaly/injection detection (v1 — heuristics)** — מסמן (לא בהכרח חוסם): lethal-trifecta (קריאת סוד + יציאה החוצה), tool מחוץ ל-baseline, דפוסי exfil מוכרים. **מסומן במפורש כ-v1; ML עתידי.**
6. **API + dashboard מינימלי** — feed פעולות חי, audit viewer, עורך policy, כפתור kill.
7. **Compliance mapping** — כל רשומה/דוח נושאים שדות ממופים ל-**EU AI Act Art. 12** + **OWASP Agentic Top 10**.

## 6. Scope — מה בחוץ (OUT) — מפורש

- ❌ Agent identity / NHI — אנחנו **צורכים** זהות, לא מנפיקים (משתלבים ב-Okta/Entra/MCP-auth).
- ❌ Payments / settlement — משתלבים ב-AP2/x402, לא בונים.
- ❌ **Trust/reputation scoring** — Phase 2. *אבל* סכמת ה-audit מתוכננת מראש להזין אותו (traces, outcomes, violations).
- ❌ ML-based detection — heuristics בלבד ב-MVP.
- ❌ HA / multi-tenant SaaS / billing / insurance brokering.
- ❌ SDK ללא-Python; proxy ל-HTTP שרירותי לא-MCP — עתידי.
- ❌ Undo אוטומטי לפעולות בלתי-הפיכות — רק hook + סימון.

## 7. User Stories (עם acceptance)

| # | Story | Acceptance |
|---|---|---|
| US-1 | כמפעיל, אני עוטף את ה-tools של הסוכן ב-Sentinel כך שכל קריאה נבדקת לפני ביצוע. | tool call לא-עטוף לא יכול לעקוף; קריאה עטופה מייצרת רשומת audit + הכרעה. |
| US-2 | כמפעיל, אני מגדיר policy: "order > $500 דורש אישור; מקס' 5 orders/דקה; אסור `delete_*`". | YAML נטען; פעולה חורגת → `block`/`require_approval`; הכל מתועד. |
| US-3 | כמפעיל, כשמשהו נראה רע אני לוחץ kill והסוכן נעצר מיד. | אחרי kill, כל קריאה → `block` עם סיבה `killed`; מצב מתועד. |
| US-4 | כבעל compliance, אני מייצא דוח audit לחלון זמן ומאמת שהוא tamper-evident. | פקודת `verify` מאשרת hash-chain שלם; שינוי ידני ברשומה → verify נכשל. |
| US-5 | כמפעיל, אני רואה feed חי של פעולות עם ההכרעה וה-policy שהתאים. | dashboard מציג רשומות בזמן-כמעט-אמת עם allow/block/flag + הכלל. |
| US-6 | כסוקר אבטחה, אני מקבל flag כשפעולה תואמת דפוס חשוד (lethal-trifecta). | תרחיש "קרא secret ואז קרא לכתובת חיצונית" → רשומה מסומנת `flagged` עם הסיבה. |

## 8. Definition of Done (MVP)

**פונקציונלי:**
- [ ] סוכן דמו עם ≥3 tools רץ end-to-end דרך Sentinel.
- [ ] 4 התרחישים מודגמים: פעולה תקינה עוברת · חריגת policy נחסמת · פעולה חשודה מסומנת · kill עוצר הכל.
- [ ] audit trail hash-chained; ניסיון tampering מזוהה ע"י `verify` (מגובה בטסט).
- [ ] policy declarative (YAML), default-deny, עם טסטים ל-allow/block/approve/rate-limit.
- [ ] API + dashboard מינימלי: actions / policy / audit / kill.
- [ ] דוח audit כולל מיפוי ל-Art.12 + OWASP Agentic IDs.

**איכות (חוק התשתית — tests-first על קוד קריטי):**
- [ ] policy engine, kill switch, audit-integrity — **טסט נכתב לפני המימוש**.
- [ ] בדיקת אבטחה עצמית: אין credentials חשופים; Sentinel עצמו לא הופך לנקודת exfil; redaction עובד.

**Non-goals ל-DoD:** לקוחות אמיתיים, scale, ML, HA.

## 9. מדדי הצלחה (MVP)

| מדד | יעד |
|---|---|
| E2E demo | 4 התרחישים עוברים, מתועד ב-`DEMO.md` |
| Audit integrity | tampering מזוהה 100% ע"י `verify` |
| Latency overhead per call | מדיד ומדווח (יעד אינדיקטיבי: < ~20ms ב-in-process; proxy mode מדווח בנפרד) |
| Test coverage | ליבה קריטית (policy/kill/audit) מכוסה; כל הטסטים עוברים |

## 10. סיכונים ברמת ה-PRD

- **בידול מ-observability** — חייב להיות compliance-grade (חתום, ממופה-רגולציה, export), אחרת זה "עוד tracing".
- **תקציבים מוקדמים** (אימוץ סוכנים עוד early) — מיטיגציה: beachhead פיננסי כואב היום + deadline רגולטורי מושך תקציב.
- **CodeIntegrity/Operant יוסיפו audit** — מיטיגציה: מהירות, OSS-first, ומיקוד ב-compliance evidence שהם לא מובילים בו.
