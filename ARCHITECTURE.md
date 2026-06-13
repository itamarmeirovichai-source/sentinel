# ARCHITECTURE.md — Sentinel MVP

> v0.1 · Phase 2. Stack ו-interception אושרו 2026-06-13. כולל threat model.

---

## 1. עקרונות מנחים

1. **Default-deny** — פעולה שלא הותרה במפורש נחסמת.
2. **Fail-closed** — אם שכבת ההכרעה עצמה נכשלת (שגיאה ב-policy/audit), הפעולה **נחסמת**, לא רצה. אבטחה > זמינות.
3. **Append-only + tamper-evident** — ה-audit לא נמחק ולא משתנה; כל שינוי מתגלה ב-`verify`.
4. **Interceptor מופשט** — הליבה (policy/audit/kill/detect) לא יודעת איך יורטה הפעולה. SDK wrapper היום, MCP-proxy מחר — אותה ליבה.
5. **Sentinel הוא נקודת כשל high-value** — מתייחסים לקוד שלנו עצמו כמשטח תקיפה (סעיף 6).

## 2. Stack (אושר)

| רכיב | בחירה | נימוק |
|---|---|---|
| שפה | **Python 3.11+** | העולם של MeiroX + ecosystem הסוכנים; מסלול מהיר |
| Interception | **SDK wrapper** (decorator/wrap) מאחורי `Interceptor` interface | מכסה את ה-tools הישירים של MeiroX, framework-agnostic, דטרמיניסטי ל-tests-first; MCP-proxy נכנס כ-adapter בלי שכתוב |
| Audit store | **SQLite** + hash-chain | embeddable, tamper-evident פשוט, משדרג ל-Postgres |
| Policy | **YAML** (`yaml.safe_load`) | declarative, קריא ללקוח, ניתן לעריכה ב-dashboard |
| API/Dashboard | **FastAPI** + עמוד HTML מינימלי | קל, async, OpenAPI חינם |
| בדיקות | **pytest** | tests-first על הליבה הקריטית |

## 3. דיאגרמת רכיבים + data flow

```
   agent (למשל trading_agent)
        │ tool_call(name, args)
        ▼
 ┌─────────────────────────────────────────────────────────┐
 │ Interceptor (SDK wrapper)  →  sentinel.check(ToolCall)   │
 └───────────────────────────────┬─────────────────────────┘
                                  ▼
        ┌──────────────────────────────────────────┐
        │ 1. KillSwitch.active?  → block(reason=kill)│  (fail-closed)
        │ 2. Detector.inspect()  → flags[]           │  (מסמן, לא חוסם)
        │ 3. Policy.evaluate()   → allow/block/      │  (default-deny)
        │                          require_approval  │
        │ 4. combine → Decision                      │
        └───────────────┬────────────────────────────┘
            allow ───────┤────── block / require_approval
              │          │
   execute tool_fn       │ (לא מבוצע)
   (try/except)          │
              │          │
              ▼          ▼
        ┌──────────────────────────────────────────┐
        │ AuditLog.append(record)  (hash-chained,    │
        │   redacted, compliance-mapped)             │
        └───────────────┬────────────────────────────┘
                        ▼
        ┌──────────────────────────────────────────┐
        │ FastAPI: /actions /audit/verify /export    │
        │          /policy /kill /status  + dashboard│
        └────────────────────────────────────────────┘
```

**רצף לקריאה מותרת:** check → allow → execute → append record (status=`executed`/`error`).
**רצף לקריאה חסומה:** check → block → append record (status=`blocked`/`killed`/`pending_approval`), ה-tool **לא** מבוצע.

## 4. מודל הנתונים — רשומת Audit (לב המוצר)

```
AuditRecord
  seq            int          # מונוטוני
  ts             float/iso    # זמן
  agent_id       str
  session_id     str
  tool           str
  args           dict         # אחרי redaction
  decision       enum         # allow | block | require_approval
  policy_rule    str|null     # id הכלל שהתאים (או null=default-deny)
  reason         str
  flags          [str]        # מה-Detector
  status         enum         # executed | blocked | error | pending_approval | killed
  error          str|null
  compliance     {eu_ai_act_art12: bool, owasp_agentic: [str]}
  prev_hash      str(64)
  hash           str(64)      # sha256( prev_hash + canonical_json(payload) )
```

**Hash-chain:** רשומת genesis עם `prev_hash="0"*64`. כל רשומה: `hash = sha256(prev_hash + canonical_json(הכל חוץ מ-hash))`. `verify()` מחשב מחדש את כל השרשרת ובודק (א) כל hash תואם, (ב) כל `prev_hash` תואם ל-hash הקודם. כל עריכה/מחיקה/שינוי-סדר באמצע → מתגלה. (truncation של הזנב — מיטיגציה ב-`ROADMAP.md`: anchoring חיצוני תקופתי.)

> הערה: רשומה אחת לכל tool call, נכתבת אחרי ניסיון הביצוע (עטוף ב-try/except, כך ששגיאת tool עדיין נרשמת). הפער היחיד: process kill באמצע ביצוע. מיטיגציה (roadmap): two-phase logging (intent לפני, outcome אחרי).

## 5. מודל ה-Policy (YAML)

```yaml
version: 1
default: deny                 # default-deny
rules:
  - id: allow-reads
    match: { tool: ["get_*", "read_*"] }     # glob
    action: allow
  - id: cap-order
    match:
      tool: place_order
      args: { amount: { gt: 500 } }          # comparators: gt/gte/lt/lte/eq/in/contains
    action: require_approval
  - id: rate-limit-orders
    match: { tool: place_order }
    rate_limit: { max: 5, per_seconds: 60 }   # מעל הסף → block
    action: allow
  - id: forbid-deletes
    match: { tool: "delete_*" }
    action: block
```

הכרעה: **first-match-wins** (לפי סדר), אחרת `default`. תמיכה: glob על שם tool, comparators על args, rate_limit (sliding window in-memory ל-MVP), ו-`on_flag: block` אופציונלי להסלמה על flag מה-Detector.

## 6. Threat Model (Sentinel עצמו כמשטח תקיפה)

| # | איום | מיטיגציה ב-MVP | סטטוס/roadmap |
|---|---|---|---|
| T1 | **Bypass** — קריאה ל-tool לא-עטוף | helper `wrap_all` + תיעוד; default-deny על מה שמוכר | מגבלת SDK-mode; proxy/egress עתידי הופך bypass לבלתי-אפשרי |
| T2 | **Audit tampering** — עריכת ה-DB | hash-chain → `verify` מגלה כל edit/reorder/delete | anchoring חיצוני נגד truncation (roadmap) |
| T3 | **Log-as-exfil / log injection** | redaction לפני כתיבה; args כ-data בלבד; canonical JSON | — |
| T4 | **Policy evasion** — args שמתחמקים מ-match | **default-deny** + טסטים על matchers | — |
| T5 | **Kill switch failure** | נבדק בכל קריאה, **persisted** (שורד restart), **fail-closed** אם לא נקרא | — |
| T6 | **Sentinel כ-vector** — ReDoS/YAML | `yaml.safe_load`, regexes חסומים | — |
| T7 | **Secrets handling** | redaction; אין סודות בלוג; `.env` (לא מקומיט) | — |
| T8 | **Fail-open** — שגיאה בליבה → tool רץ? | **fail-closed**: כל חריגה ב-check → block (נבדק בטסט) | — |

## 7. מבנה הפרויקט

```
sentinel/
  src/sentinel/
    models.py       # ToolCall, Decision, AuditRecord
    redaction.py    # redaction של סודות
    policy.py       # טעינה + הכרעת YAML (default-deny, glob, comparators, rate-limit)
    audit.py        # AuditLog: SQLite, hash-chain, verify, export
    killswitch.py   # KillSwitch persisted (fail-closed)
    detector.py     # heuristics v1 (lethal-trifecta, off-baseline, injection sigs)
    compliance.py   # מיפוי Art.12 / OWASP Agentic
    sentinel.py     # הליבה: check() + wrap() (Interceptor)
    api.py          # FastAPI + dashboard
    config.py
  policies/example.yaml
  examples/trading_agent.py   # סוכן דמו (beachhead פיננסי)
  tests/                      # tests-first על policy/audit/kill
```

## 8. למה זה לא נועל אותנו

`Interceptor` הוא interface. SDK wrapper הוא מימוש אחד; הליבה (`check()`) מקבלת `ToolCall` ולא יודעת מאיפה הגיע. MCP-proxy עתידי = adapter שבונה `ToolCall` מתעבורת MCP וקורא לאותו `check()`. אפס שכתוב של policy/audit/kill.
