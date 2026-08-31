# Take-Home Assignment: Security Engineer (CISO Track)

**Timebox: 2 hours.** We'd rather see a complete, smaller solution than an
ambitious fragment. Use any tools you like — **AI assistants are explicitly
permitted and expected**. We care about how you use them, not whether.

## Background

Tangible's Liquidity Hub is a multi-tenant platform where enterprise clients
(large wealth platforms, private banks) let their advisors and LPs list, bid
on, and transfer positions in private-market funds. Some clients run on
dedicated single-tenant deployments. The stack is roughly: a Directus/Postgres
backend with custom extensions, a React SPA, AWS (ECS, RDS, S3) provisioned
with Terraform, GitHub Actions for CI/CD, Auth0/SSO for identity, and SFTP/API
feeds carrying client position data.

The security engineer role here has two sides, and this assignment mirrors
both: hands-on review of the kind of stack we actually run, and the judgment +
communication the rest of the organization needs from security — clients,
execs, and ops included. It's the first dedicated security hire, with a path
to owning the whole function.

## Part 1 — Security review (~70 min)

`sample-service/` is a snapshot of an internal feed-ingestion service a
contractor team delivered last year: a small Flask API that receives nightly
position-feed files from enterprise clients, its config, the Terraform that
provisions its AWS resources, and the GitHub Actions workflow that builds and
deploys it. It works — client files do get ingested. The question is what
else it allows.

Review it the way you would if this landed on your desk in week one:

1. **Findings register.** Every vulnerability or material weakness you find,
   in any file (the app, the config, the Terraform, the CI workflow — all in
   scope). For each: a title, location (file + line/section), severity with
   one line of justification, a concrete exploit sketch (who can do what,
   from where, and what they get), and the recommended fix.
2. **Patch the top two.** Fix the two issues you would fix *first*, in the
   code/config/IaC itself, and be ready to defend why those two. Minimal,
   correct patches — the service must still do its job.

Deliverable: the findings register (markdown is fine) + your patches.

Static review is fine — you don't need to run the service. If you do run it,
do so only locally.

## Part 2 — Incident scenario (~40 min)

It's 18:40 on a Friday. Monitoring flags that a **valid API token belonging
to one of our enterprise clients** was used in the last hour to bulk-export
~40k position records through our read API, from an ASN we've never seen, at
a rate no integration of theirs has ever used. Ten minutes later, that
client's integration lead (technical, trusted contact) emails: one of their
advisors appears to have had their account taken over *on the client's side*
this morning, and they ask, directly: **"Were you breached? Should we be
telling our LPs anything?"**

Write, in this order:

1. **First 60 minutes** — your concrete action list, in order. What do you
   do, check, and *not* do, and who do you pull in.
2. **Internal note to the CEO** (≤150 words) — what happened, what we know
   vs. don't know, what you're doing, what you need.
3. **Reply to the client** (≤200 words) — answer their question. This is a
   revenue-critical enterprise relationship.
4. **Next quarter** — three changes you'd drive: one technical, one process,
   one organizational. One sentence each.

Judgment beats completeness: we'd rather see five well-chosen actions than
twenty generic ones.

## Part 3 — AI usage note (5 minutes, ~5 bullets)

Briefly: which tools you used, what you used them for, and one place where
you overrode or corrected what the AI gave you (or would have, if it didn't
come up).

## What we're evaluating

- Discovery: do you find the real problems, across app code *and* infra *and*
  CI — with exploit reasoning, not scanner output?
- Severity judgment: do you prioritize by actual exploitability and business
  impact (tenant data exposure, client trust) rather than checklist order?
- Fix quality: minimal, correct, doesn't break the service.
- Incident judgment: containment vs. evidence preservation, what you say to
  whom and when, whether you involve legal/compliance, how you handle a
  frightened client.
- How you use AI: verification and judgment, not copy-paste.

## Ground rules

- Review statically; don't probe or exploit anything that isn't your own
  local copy.
- Don't gold-plate: no SIEM deployments, no re-architecture. Two hours.
- The service is small on purpose. Assume it represents a real service
  handling ~100k rows nightly across dozens of enterprise tenants; be ready
  to discuss what changes at that scale in the debrief, not in code.
- Questions during the assignment window: email us — it's all signal.
