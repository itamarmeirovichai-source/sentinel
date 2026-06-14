# Outreach — finding your first design partner

The whole game right now is **one real user**. This is how to get them. Send a few a day,
personalized — never copy-paste spam.

## Who to target (people who actually have the pain)

- Indie hackers / small startups shipping agents that touch **money, email, databases, or code execution**
- Authors of **MCP servers** and agent tools (they care about tool safety already)
- AI engineers piloting agents **in production** at small companies
- Anyone posting "my agent did <unintended thing>" or prompt-injection war stories

## Where to find them

- X search: `"AI agent" production`, `prompt injection`, `agent went rogue`
- HN comments on agent/LLM threads
- r/AI_Agents, r/LLMDevs
- LangChain / CrewAI / MCP Discords
- GitHub: issues on popular agent repos

## DM / email template (short, helpful, no pitch-spam)

> Hey <name> — saw you're building <their agent>. I made a small open-source layer that
> sits between an agent and its tools: it enforces a policy, logs every action
> tamper-evidently, and has a kill switch. It's early and free. Would a 15-min look be
> useful? Happy to help you wire it in. <link>

## If they engage

- Offer to **pair on the integration** (do the work with them).
- Ask the one question that matters: **"What would you need before you'd trust something
  like this in front of a real agent?"** — their answer is your roadmap.

## The zero-risk angle (use this)

> Run it in **monitor mode** — it only watches and logs, never blocks — so there's no risk
> to your agent. See what it *would* have caught, then decide.

## What "success" looks like

One person runs a real agent through Sentinel and tells you it caught/prevented something
real. Write down their exact words. That sentence is your proof — and the start of everything.
