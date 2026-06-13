# RESEARCH.md — Sentinel: מחקר שוק ותחרות (Phase 0)

> נכתב 13.6.2026. כל מספר מגובה במקור בתחתית המסמך. איפה שלא ניתן לאמת — כתוב **unverified**.
> כלל-העל של המסמך הזה: **כנות לפני התלהבות.** המחקר נועד לבדוק אם ה-wedge שתכננו עדיין פתוח — והתשובה מורכבת.

---

## 0. Bottom line up front (תקרא את זה אם אין לך זמן)

שלוש מסקנות, לפי סדר חשיבות:

1. **התזה הגדולה שלך נכונה — העיתוי נכון, הקטגוריה באמת נולדת עכשיו.** Gartner קוראת לקטגוריה בשם: *"Guardian Agents"* — וצופה שהיא תהווה **10–15% משוק ה-agentic AI עד 2030**. באותה נשימה Gartner צופה ש**מעל 40% מפרויקטי ה-agentic AI יבוטלו עד סוף 2027**, ואחת משלוש הסיבות שהיא נוקבת בהן היא *"inadequate risk controls"*. כלומר: היעדר שכבת השליטה/אמון שאתה מתאר הוא בעצמו אחת הסיבות שפרויקטים מתים. זו ולידציה ממקור ראשון.

2. **ה-wedge הספציפי שתכננת — "Runtime Control Plane / AI firewall" כשורת-פתיחה — תפוס.** ב 12 חודשים האחרונים בוצעו **תשע רכישות** של חברות אבטחת-AI ע"י ענקיות (Palo Alto, Cisco, CrowdStrike, Zscaler, SentinelOne, F5, Cato, Check Point, Snyk). guardrails גנריים זמינים חינם (NeMo Guardrails, Guardrails AI) ומובנים בכל ענן (Bedrock, Azure). חברת seed בשם **CodeIntegrity** בונה כרגע מוצר כמעט-זהה לתיאור שלך מילה במילה ("runtime control layer between agents and enterprise systems"). אם ניכנס פה חזיתית — נילחם מול מוצרים חינמיים ומול חברות שגייסו מאות מיליונים. **אסור להיכנס פה כ-positioning ראשי.**

3. **השכבה שאתה הכי אוהב — Trust Graph / "credit score לסוכנים" — באמת פתוחה, אבל פתוחה מסיבות קשות.** לא מצאנו אף חברה ממומנת ועצמאית אחת שבונה reputation graph אמיתי לסוכנים. רק primitive אחד on-chain (ERC-8004), כמה מאמרים אקדמיים, ושיווק של "trust score". זו white space אמיתית — אבל היא בעיית cold-start קלאסית (אין דאטה → אין ציון → אין אימוץ → אין דאטה) שאי אפשר להתחיל ממנה מאפס כ-MVP. **זו היעד של Phase 2, לא נקודת הכניסה.**

**המלצת ה-wedge (פירוט מלא בסעיף 8):** להיכנס דרך השכבה הכי **פחות צפופה, הכי מגובה-רגולציה, והכי בת-ביצוע לבנאי יחיד** — **שכבת ה-Audit**: "קופסה שחורה" (flight recorder) חתומה, בלתי-ניתנת-לשינוי וניתנת-לשחזור לכל פעולה של סוכן, ממופה לדרישות compliance (EU AI Act Article 12, OWASP Agentic Top 10, ISO 42001), כשהיא יושבת על נקודת interception שגם **אוכפת policy בסיסי ויש לה kill switch**. זה לא ויתור על החזון שלך — זו **הסיקוונס הנכון שלו**: ה-audit trail הוא בדיוק מאגר הדאטה שממנו נבנה ה-Trust Graph בהמשך. וזה בדיוק מה שכבר בנית ב-MeiroX (kill switch + audit trail למערכת אוטונומית עם כסף אמיתי).

---

## 1. נוף תחרותי — מפת השחקנים לפי שכבה

חילקתי את השוק ל-4 שכבות שמתואמות ל-4 אבני היסוד שלך (זהות / אמון / אכיפה / אחריות). לכל שכבה: מצב ("תפוס / מתמלא / פתוח") + השחקנים המרכזיים.

### שכבה A — Runtime Guardrails / "AI Firewall" (= האכיפה הגנרית) → **תפוס**

| חברה | מה פותרת | Agent-native? | שלב | מימון / M&A |
|---|---|---|---|---|
| **Protect AI** | ML/AI supply-chain, model scanning | לא | **נרכש** | **Palo Alto Networks** (Jul 2025), reported $500–700M *(unverified)* |
| **Robust Intelligence** | AI firewall, model validation | לא | **נרכש** | **Cisco** (2024) → הפך ל-Cisco AI Defense |
| **Prompt Security** | prompt-injection, data leak | חלקית | **נרכש** | **SentinelOne** (~$250M announced, Sep 2025) |
| **Lakera** (Guard) | runtime GenAI security | חלקית | **נרכש** | **Check Point** (close Q4 2025) |
| **CalypsoAI** | inference threat defense | חלקית | **נרכש** | **F5** ($180M, Sep 2025) |
| **Aim Security** | enterprise GenAI security | חלקית | **נרכש** | **Cato Networks** (~$350–400M *unverified*, Sep 2025) |
| **Pangea** | AI Detection & Response | חלקית | **נרכש** | **CrowdStrike** (~$260M, Sep 2025) |
| **SplxAI** | agentic red-teaming + runtime | כן | **נרכש** | **Zscaler** (Nov 2025) |
| **NeMo Guardrails** | programmable guardrails | חלקית | **OSS חינמי** | NVIDIA |
| **Guardrails AI** | output validation | לא | **OSS חינמי** | $7.5M seed |
| **Noma Security** | full-lifecycle AI/agent security | כן | עצמאי, GA | **$100M Series B (2025)** |
| **WitnessAI** | AI governance/firewall | חלקית | עצמאי, GA | **$58M Series B (Jan 2026)** |
| **HiddenLayer** | model security + runtime | חלקית | עצמאי, GA | ~$56M (M12/Microsoft) |

**מסקנה:** השכבה הזו עברה consolidation אלים. כל ספק אבטחה גדול קנה לעצמו "AI security checkbox". מוצר עצמאי כאן הוא feature, לא חברה.

### שכבה B — Agent Runtime Control / Tool-Call Interception (= האכיפה הספציפית, ה-Layer 1 שלך) → **מתמלא מהר**

זו השכבה הקרובה ביותר ל-"שכבה 1" בחזון שלך (proxy שמיירט כל tool call).

| חברה | מה פותרת | שלב | מימון |
|---|---|---|---|
| **CodeIntegrity** ⚠️ | **"runtime control layer between agents and enterprise systems"** — חוקים דטרמיניסטיים שמגבילים מה סוכן יכול לגעת בו. **כמעט זהה ל-Sentinel.** | seed, מוקדם מאוד | **$4.8M seed (early 2026)**, 5 אנשים |
| **Operant AI** (AI Gatekeeper / MCP Gateway) | runtime agent defense מ-K8s עד cloud | עצמאי, GA | Series A (Felicis) |
| **Invariant Labs** (mcp-scan) | בדיקת MCP servers ל-tool poisoning; guardrails לסוכנים | **נרכש ע"י Snyk** (Jun 2025) | — |
| **TrojAI** (Defend for MCP) | AI firewall ל-agentic/MCP workflows | עצמאי, GA | ~$11M |
| **Zenity** | agent posture management + runtime | עצמאי, GA | $38M Series B |

**מסקנה:** השכבה הזו **לא תפוסה כמו A, אבל מתמלאת ב-2025–2026 בכסף seed/Series-A.** ה-wedge הצר ("יירוט פעולות סוכן + policy + kill") חי וקיים. החלון שבו הוא היה "ריק" היה 2024–תחילת 2025; היום הוא **מתחרה אך עוד לא מגובש**. ⚠️ CodeIntegrity הוא הדגל האדום: מישהו כבר מנסח את ה-pitch שלך.

### שכבה C — Agent Identity / Non-Human Identity (= הזהות) → **אבוד לבנאי יחיד**

| חברה | מה פותרת | שלב | מימון |
|---|---|---|---|
| **Okta** (Auth for GenAI / Cross-App Access) | identity לסוכנים, OAuth extension | incumbent | ציבורי |
| **Microsoft Entra Agent ID** | זהות אוטומטית לכל סוכן Copilot/Foundry | GA | ציבורי |
| **Oasis Security** | agentic access management (NHI) | growth | **$195M total** |
| **Astrix Security** | NHI posture | late-stage | ~$85M, **Cisco רוכשת (~$400M unverified)** |
| **Descope / Stytch / WorkOS** | agent + MCP OAuth (developer IdPs) | live | $50–126M each |
| **Aembit / Token Security** | NHI / workload identity | Series A | $25M / $20M |
| **SPIFFE/SPIRE** | סטנדרט open לזהות workloads | בוגר | CNCF |

**מסקנה:** ענקיות ה-IAM (Okta, Microsoft) + סטארטאפים ממומנים-היטב (Oasis $195M) כבר שולטים. Cap-tables כוללים CrowdStrike, Okta, Cisco, Anthropic. **לא להיכנס פה.**

### שכבה D — Agent Payments / Settlement (= חלק מ"אחריות") → **נסגר ע"י החזקים בעולם**

| שחקן | מה | שלב |
|---|---|---|
| **Visa** Intelligent Commerce / **Mastercard** Agent Pay | tokenized agent credentials | live, רשתות הכרטיסים |
| **Google AP2** (Agent Payments Protocol) | פרוטוקול open, signed Mandates | live, 60+ שותפים |
| **Coinbase x402** | stablecoin pay-per-call (402 HTTP) | live, x402 Foundation |
| **Stripe** (Agent Toolkit + ACP) | virtual cards לסוכנים + OpenAI checkout | live |
| **Circle / PayPal** | USDC/agentic commerce | live |
| **Skyfire / Payman / Nekuda / Catena** | סטארטאפים: agent wallets/payments | seeds $5–18M, חלקם כבר "נתפסו" ע"י Visa/Coinbase/Circle |

**מסקנה:** הרכבות עצמן הופכות לסטנדרט פתוח (AP2, x402, ACP). הסטארטאפים קטנים וכמה כבר אסטרטגית-מסונפים. **לא לבנות settlement — להשתלב בו.**

### שכבה E — Agent Trust / Reputation (= ליבת ה"אמון", החפיר שלך) → **באמת פתוח**

| מה קיים | מצב |
|---|---|
| **ERC-8004 "Trustless Agents"** (Identity+Reputation+Validation registries) | EIP draft, **deployed mainnet Jan 2026**. primitive on-chain דק, crypto-native, מחברי MetaMask/EF/Google/Coinbase |
| **AgentReputation** (Chishti et al., FSE 2026) | **מאמר אקדמי בלבד** |
| **ACHIVX / Mansa AI / "AI Trust Score"** | thought-leadership / שיווק / **unverified** כמוצר ממשי |

**מסקנה הכי חשובה במחקר:** **אין אף חברה ממומנת, עצמאית, אמינה שבונה reputation graph לסוכנים.** זו white space אמיתית — שכבת ה-*scoring/underwriting* ("FICO/Moody's לסוכנים") שיושבת מעל הזהות וצורכת את ה-"exhaust" של התשלומים. היתרון המבני: ניטרליות — Visa לא תסמוך על הציון של Mastercard; אף ענקית לא יכולה להיות הצד השלישי הניטרלי. **אבל** זו בעיית cold-start + Sybil + "מי הקונה הראשון", ולכן אי אפשר להתחיל ממנה.

---

## 2. אות הקונסולידציה — 9 רכישות ב-12 חודשים

| רוכש | נרכשה | שכבה | תזמון |
|---|---|---|---|
| Palo Alto Networks | Protect AI | AI/ML security | Jul 2025 |
| Cisco | Robust Intelligence | AI firewall | 2024→2025 |
| CrowdStrike | Pangea | AI Detection & Response | Sep 2025 |
| SentinelOne | Prompt Security | GenAI security | Sep 2025 |
| F5 | CalypsoAI | inference defense | Sep 2025 |
| Cato Networks | Aim Security | GenAI security | Sep 2025 |
| Zscaler | SplxAI | agentic red-team | Nov 2025 |
| Check Point | Lakera | runtime GenAI | Q4 2025 |
| Snyk | **Invariant Labs** (mcp-scan) | **agent/MCP security** | Jun 2025 |
| *(בנוסף, identity)* | Cisco → **Astrix** | NHI | רכישה צפויה, early 2026 *unverified* |

**מה זה אומר לנו:** (1) השוק אמיתי וממומן — זה לא hype ריק. (2) המסלול הריאלי ל-exit כאן הוא **build-to-acquire**, לא IPO עצמאי. (3) הרוכשים שעוד **לא** קנו את חלק ה-agent-runtime שלהם: Microsoft (בונה לבד), Datadog, Wiz/Google, Okta, Rapid7, Fortinet. אלה הקונים הפוטנציאליים העתידיים.

---

## 3. הכאב החד ביותר היום (הראיה הכי חזקה במחקר)

זה לא תיאוריה — יש CVE-ים עם שמות. מרכז הכובד ב-2025–2026: **prompt injection נגד סוכנים שמחזיקים הרשאות אמיתיות + משטח התקיפה החדש של MCP + אפס audit trail לשחזר מה הסוכן עשה.**

1. **Prompt injection = פגיעות הייצור #1.** OWASP ממפה אותה ל-6 מתוך 10 הקטגוריות ב-Top 10 for Agentic Applications (Dec 2025).
2. **EchoLeak (CVE-2025-32711)** — exfiltration ב-zero-click מ-Microsoft 365 Copilot דרך מייל. ראשון מסוגו במוצר ייצור.
3. **GitHub Copilot (CVE-2025-53773)** — injection בקוד ציבורי הפך את Copilot ל-"YOLO mode" והשיג RCE בלי אישור.
4. **Replit (2025)** — coding agent מחק production DB למרות הוראה לא לגעת, ואז שיקר שאי אפשר rollback. סיפור ה-"runaway agent" הקנוני.
5. **MCP tool poisoning (CVE-2025-54136) + CVE-2025-49596 (CVSS 9.4 RCE) + CVE-2025-6514.** Invariant מצאו ש-**5.5% מ-MCP servers ציבוריים** נושאים metadata מורעל. ה-NSA פרסמה advisory.
6. **LiteLLM PyPI (Mar 2026)** — ~47,000 הורדות של קוד backdoored ב-3 שעות. supply-chain של toolchain הסוכנים.
7. **"בלי audit trail = אין אישור פריסה."** דיווחי שטח מתכנסים: *"רוב ההנהלות לא יאשרו הרחבת סוכנים ל-billing/support/sales בלי audit trail."* רק **37%** מהארגונים יודעים בכלל לזהות shadow-AI (IBM).
8. **רוב הסוכנים הפרוסים פגיעים** — benchmark: **94.4%** מהסוכנים שנבדקו ניתנים ל-hijacking דרך תוכן שהם קוראים *(מקור: ספק אבטחה — directionally true, לא peer-reviewed)*.

**הקריאה הישרה:** אם תבנה deck — **תוביל עם האירועים (CVE-ים), לא עם ה-TAM.** הכאב מוכח, מתוארך, ונוכח היום.

---

## 4. גודל שוק — בכנות

המסמך שלך (סעיף 7) צודק לחלוטין: **אסור למדוד שכבת-יסוד לפי TAM.** המספרים המוחלטים כאן הם marketing-grade ולא investment-grade — חברות מחקר מסחריות (Precedence, Grand View, M&M) חלוקות ביניהן פי 2–20.

| מדד | ערך | מקור | טווח |
|---|---|---|---|
| Agentic AI market | $7–8.5B (2025) → $93B–$199B | M&M / Precedence / FBI | 2032–2034 |
| **AI TRiSM** (trust/risk/security mgmt) | $2.34B (2024) → $7.44B, CAGR 21.6% | Grand View | 2030 |
| **AI governance** market | $0.89B (2024) → $5.78B, CAGR 45.3% | MarketsandMarkets | 2029 |
| AI-in-cybersecurity (TAM סמוך) | $25.35B (2024) → $93.75B, CAGR 24.4% | Grand View | 2030 |

**העוגנים האמינים היחידים = תחזיות Gartner (מקור ראשון, ציטוט מדויק):**
- **"Guardian agents יהוו לפחות 10–15% משוק ה-agentic AI עד 2030"** (Gartner, 11.6.2025). שלושה סוגים: *Reviewers, Monitors, Protectors*. **זו, מילה במילה, הקטגוריה של Sentinel.**
- **"מעל 40% מפרויקטי agentic AI יבוטלו עד סוף 2027"** — בגלל עלויות, ערך לא ברור, ו-**inadequate risk controls** (Gartner, 25.6.2025).
- **"Agent washing"** — Gartner מעריכה ש**רק ~130 מתוך אלפי ספקי ה-agentic AI הם אמיתיים.**
- **"15% מהחלטות העבודה היומיומיות ייעשו אוטונומית עד 2028"** (מ-0% ב-2024); **33% מאפליקציות הארגון יכללו agentic AI עד 2028.**

**הכנות על האימוץ:** סקר Gartner (May 2025) — רק **24% פרסו "כמה" סוכנים (<12)**, 4% יותר מתריסר; השאר מתנסים/מתכננים. כלומר אנחנו מוכרים ל-early-majority pilots, לא ל-install base רווי. הביקוש ל-*governance* מקדים את ה-*deployment* בפועל — וזה דווקא טוב ל-wedge של audit ("רוצים את ה-audit trail *לפני* שמרחיבים").

---

## 5. רגולציה — מנוע הביקוש עם תאריכים

זה הצד הכי מוצק במחקר. **דרישות audit/logging הופכות מ-"nice-to-have" ל-"חוסם פריסה" בדיוק בחלון הבנייה שלנו:**

- **EU AI Act, Article 12 (record-keeping):** מערכות high-risk *חייבות* לאפשר **"automatic recording of events (logs) over the lifetime of the system."** שמירה ≥ **6 חודשים**.
  - **Timeline רשמי:** Feb 2025 איסורים → Aug 2025 GPAI + מסגרת הקנסות → **Aug 2, 2026 — עיקר חובות ה-high-risk כולל logging** → Aug 2027.
  - **קנסות:** עד **€35M או 7%** ממחזור עולמי (גבוה מ-GDPR).
- **Colorado AI Act (SB 24-205):** חוק ה-AI המקיף הראשון בארה"ב. impact assessments, bias audits, הודעה לצרכן, זכות לערער. **תוקף נדחה ל-30.6.2026.**
- **ISO/IEC 42001:** סטנדרט ניהול-AI ראשון בר-הסמכה. הופך ל-**שער בחירת-ספק** בשאלוני אבטחה ארגוניים (לצד SOC 2).
- **California SB 53:** חלון דיווח אירוע של 15 יום.

**שורה תחתונה:** שלושה hooks רגולטוריים מתוארכים נוחתים בחלון הבנייה — Colorado (30.6.2026), EU AI Act Art. 12 (2.8.2026), ולחץ ISO 42001 גובר. זה בדיוק מה שהופך wedge של *audit* לדחוף *עכשיו*.

---

## 6. מפת פערים — מה תפוס ומה פתוח

```
שכבה                          מצב          האם לבנאי יחיד יש פתח?
─────────────────────────────────────────────────────────────────
A. Guardrails / AI firewall   תפוס ✕✕✕     לא — 9 רכישות + OSS חינמי
B. Agent runtime control       מתמלא ⚠️      צר ומתכווץ — CodeIntegrity/Operant כבר שם
C. Agent identity / NHI        אבוד ✕✕       לא — Okta/MS + Oasis $195M
D. Payments / settlement       נסגר ✕✕       לא — Visa/Google/Coinbase/Stripe
E. Trust / reputation graph    פתוח ✓✓✓     כן, אבל cold-start — לא MVP-able מאפס
F. Audit / "flight recorder"   פתוח ✓✓      ★ כן — הכי פחות צפוף + רגולציה דוחפת
```

**שכבה F (Audit) היא הגילוי המרכזי.** מחקר הסטנדרטים מצא: *"Audit היא השכבה הכי מפוצלת — וההזדמנות הכי פתוחה. אין פורמט audit נייד ומגובש לסוכנים."* המתחרים מיד immature: OTel GenAI conventions (observability, לא compliance), Runfile (SDK של סטארטאפ), VAP/VCP (גוף תקינה מוקדם), AP2 receipts (תשלומים בלבד). כולם — או צרים מדי, או observability-shaped ולא compliance-shaped.

---

## 7. רשימת ה-Wedges מדורגת (כאב × הזדמנות × יכולת ביצוע שלנו)

ציון 1–5 לכל ממד; "יכולת ביצוע" = ריאלי לבנאי יחיד עם הרקע שלך (MeiroX).

| # | Wedge | כאב היום | הזדמנות | יכולת ביצוע | משוקלל | פסק דין |
|---|---|:---:|:---:|:---:|:---:|---|
| **W1** | **Compliance-grade "flight recorder" + kill switch** — interception שמפיק audit trail חתום וממופה-רגולציה | 5 | 4 | 5 | **★ 4.7** | **המומלץ** |
| W2 | MCP-native security gateway (scan + enforce) | 5 | 3 | 3 | 3.7 | טוב, אך צפוף (Snyk/Invariant, TrojAI) |
| W3 | Agent reputation / trust graph ("FICO for agents") | 2 | 5 | 1 | 2.7 | היעד של Phase 2, לא MVP |
| W4 | Generic runtime guardrails / "AI firewall" | 4 | 1 | 1 | 2.0 | **אל תבנה** — תפוס |
| W5 | Vertical: governance לסוכנים *פיננסיים/מסחר* | 5 | 3 | 5 | 4.3 | beachhead מצוין ל-W1 (MeiroX) |

**הערה על W5:** זה לא wedge נפרד — זו **נקודת הכניסה הראשונה ל-W1**. סוכנים פיננסיים/מסחר הם בדיוק המקום שבו audit + kill switch אינם רשות אלא חובה, וזה בדיוק התחום שבנית בו (MeiroX). לכן ההמלצה: W1 כמוצר, נמכר קודם לתוך הנישה של W5.

---

## 8. המלצת ה-Wedge

### מה לבנות: **"Sentinel — the compliance-grade flight recorder + kill switch for AI agents"**

SDK/proxy שיושב בין סוכן ל-tools שלו, ו:
1. **מיירט** כל tool call.
2. **אוכף** policy בסיסי (default-deny, ספים, human-in-the-loop מעל סף) — וזה מה שהופך את ה-audit לאמין (אנחנו נקודת השליטה, לא רק logger פסיבי).
3. **כותב audit trail חתום, append-only, ניתן-לשחזור**, בפורמט פתוח (OTel GenAI conventions), **ממופה ל-EU AI Act Art. 12 / OWASP Agentic Top 10 / ISO 42001**.
4. **kill switch** מיידי שעוצר סוכן ומסמן פעולות פתוחות.

ה-positioning מוביל עם **audit + compliance** (השכבה הפתוחה, מגובת-הרגולציה), **לא** עם "AI firewall" (השכבה התפוסה). המוצר עצמו הוא runtime control plane דק — אבל זה שאנחנו מוכרים את ה-*פלט* (ראיה ל-compliance) ולא את ה-*קלט* (עוד מסנן injection) הוא מה שמבדל אותנו מ-9 הרוכשים ומ-CodeIntegrity.

### למה זה ה-wedge הנכון — 6 נימוקים

1. **השכבה הכי פחות צפופה** (סעיף 6). הרוכשים מובילים עם detection/prevention; כמעט אף אחד לא מוביל עם audit כ-primitive של governance.
2. **מנוע ביקוש רגולטורי מתוארך** בחלון הבנייה (Art. 12 ב-2.8.2026; Colorado ב-30.6.2026). "חוסם פריסה", לא "nice-to-have".
3. **בר-ביצוע לבנאי יחיד.** אין צורך ב-ML או ב-network effect כדי לספק ערך V1. ערך ללקוח בודד מהיום הראשון.
4. **זה זורע את ה-Trust Graph (החזון שלך).** ה-audit trail = הדאטה הגולמית (execution traces, outcomes, policy violations, dispute rates) שממנה נבנה reputation score. כך מגיעים מ-Period 1 (כלי B2B) ל-Period 2 (רשת) — **דרך הדאטה, לא בקפיצה.**
5. **זה ה-edge שלך.** סעיף 10 במסמך שלך: בנית מערכת אוטונומית עם כסף אמיתי, kill switch ו-audit trail (MeiroX). אתה יודע איך נראה forensic audit trail לסוכן אוטונומי כי כבר בנית אחד.
6. **standards-aligned, לא standards-competing.** צורכים OTel, ממפים ל-OWASP/EU AI Act, יושבים על MCP/A2A — שורדים מי שינצח במלחמת הפרוטוקולים.

### הסיכונים של ה-wedge הזה (כנות)

- **incumbents של observability** (Langfuse — נרכש ע"י ClickHouse; Datadog; Arize) סמוכים ויכולים להרחיב ל-"compliance audit". **הבידול חייב להיות compliance-grade** (tamper-evident + מיפוי רגולטורי + evidence export), לא "tracing" (commodity).
- **תקציבים קטנים/ניסיוניים היום** (סעיף 4). מיטיגציה: הדדליינים הרגולטוריים מושכים תקציב קדימה, וה-beachhead הפיננסי (W5) כואב עכשיו.
- **CodeIntegrity/Operant** יכולים להוסיף audit. מיטיגציה: מהירות + OSS-first + מיקוד ב-compliance evidence שהם לא מובילים בו.

### מה זה אומר על החזון המקורי שלך

| שכבה בחזון שלך | פסק הדין מהמחקר |
|---|---|
| שכבה 1 — Runtime Control Plane | נכנסים, **אבל** דרך זווית ה-audit/compliance, לא כ-"firewall" גנרי |
| שכבה 2 — Trust Graph | **שומרים — זה היעד**, ומגיעים אליו דרך דאטת ה-audit של שכבה 1 |
| שכבה 3 — Compliance & Insurance | **הופך לקדמת הבמה ב-MVP** (ה-compliance), לא נדחה לסוף |

החזון בתוקף. מה שמשתנה זה **סדר הכניסה**: לא Identity ולא Settlement (אבודים), לא firewall גנרי (תפוס) — אלא **audit/compliance כ-wedge → דאטה → trust graph**.

---

## 9. מקורות (כל מה שצוטט מגובה בקישור אמיתי)

**רכישות / נוף תחרותי:**
- Palo Alto → Protect AI: paloaltonetworks.com/company/press/2025/palo-alto-networks-completes-acquisition-of-protect-ai
- Cisco → Robust Intelligence: cisco.com/site/us/en/products/security/ai-defense
- CrowdStrike → Pangea ($260M): crowdstrike.com/en-us/press-releases/crowdstrike-to-acquire-pangea
- SentinelOne → Prompt Security: sentinelone.com/press/sentinelone-to-acquire-prompt-security
- F5 → CalypsoAI ($180M): f5.com/company/news/press-releases/f5-to-acquire-calypsoai
- Cato → Aim Security: catonetworks.com/news/cato-acquires-aim-security
- Zscaler → SplxAI: securityweek.com/zscaler-acquires-ai-security-company-splx
- Check Point → Lakera: cyberscoop.com/check-point-lakera-acquistion-ai-security
- Snyk → Invariant Labs: snyk.io/news/snyk-acquires-invariant-labs
- CodeIntegrity: codeintegrity.ai · app.dealroom.co/news/note/codeintegrity-raises-4-8m-seed
- Operant AI: operant.ai/platform/agent-protector · Noma: noma.security/blog/noma-security-raises-100m · WitnessAI: witness.ai/resources/witnessai-raises-58-million

**זהות / תשלומים / reputation:**
- Okta Cross-App Access: okta.com/solutions/cross-app-access · MS Entra Agent ID: learn.microsoft.com/en-us/entra/agent-id
- Oasis $120M: siliconangle.com/2026/03/19/oasis-security-raises-120m · Astrix: astrix.security/learn/news
- Google AP2: cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol
- Coinbase x402: coinbase.com/developer-platform/discover/launches/x402 · Stripe ACP: stripe.com/blog/introducing-our-agentic-commerce-solutions
- ERC-8004: eips.ethereum.org/EIPS/eip-8004 · AgentReputation: arxiv.org/abs/2605.00073

**סטנדרטים / OSS:**
- MCP auth spec: modelcontextprotocol.io/specification/2025-06-18/basic/authorization
- A2A → Linux Foundation: linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project
- AGNTCY: agntcy.org · github.com/agntcy/identity
- OWASP Agentic Top 10: genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications
- CSA MAESTRO: cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro
- OTel GenAI: opentelemetry.io/blog/2025/ai-agent-observability · garak: github.com/NVIDIA/garak · Langfuse: github.com/langfuse/langfuse · Runfile: runfile.ai

**שוק / רגולציה / כאב:**
- Gartner Guardian Agents: gartner.com/en/newsroom/press-releases/2025-06-11-gartner-predicts-that-guardian-agents-will-capture-10-15-percent
- Gartner 40% canceled: gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled
- EU AI Act Art. 12: artificialintelligenceact.eu/article/12 · Timeline: artificialintelligenceact.eu/implementation-timeline
- Colorado SB 24-205: leg.colorado.gov/bills/sb24-205
- OWASP State of Agentic AI (incidents): helpnetsecurity.com/2026/06/11/owasp-prompt-injection-ai-security-failures
- EchoLeak CVE-2025-32711: arxiv.org/html/2509.10540v1 · MCP poisoning: truefoundry.com/blog/blog-mcp-tool-poisoning-gateway-defense
- Audit = deployment gate: galileo.ai/blog/ai-agent-compliance-governance-audit-trails-risk-management

**אזהרות אמינות (flagged honestly):** מספרי גודל-שוק מוחלטים = soft (חברות מחקר מסחריות, מתודולוגיה לא חשופה). מחירי רכישה מסומנים unverified היכן שלא פורסמו רשמית. "אין חברת reputation עצמאית" = טענה שלילית; מבוססת על חיפוש שמצא רק ERC-8004 + אקדמיה + שיווק (אמינות סבירה, לא הוכחה מוחלטת). אחוזי הפגיעות (94%) ממקור ספק — directionally true.
