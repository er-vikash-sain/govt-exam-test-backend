# High-Level Design (HLD)
**Project:** AI‑Powered Exam Prep Platform (India‑first)
**Primary Stack:** Python (FastAPI) + Next.js (React) + PostgreSQL + Redis + S3‑compatible object storage

---

## 1) Vision & Goals
**Vision:** Unified platform for Indian competitive exam prep with AI‑generated high‑quality mock tests, deep analytics, and delightful UX across languages.

**Business Goals**
- Acquire ≥1M registered users in 12–18 months with strong retention and conversion.
- Monetize via **credits** (AI generation), **subscriptions**, and **B2B white‑label** for institutes.
- Establish content quality/reliability with SME workflows and scalable moderation.

**Product Goals**
- Coverage for national & state exams (SSC/Banking/Police/Railways/Teaching + state equivalents).
- Fast quiz generation (<20s median), accurate scoring, rich result PDFs, and guidance (weak areas, study plans).
- Multilingual (EN/HI baseline; extendable to regional languages).

**Non‑Goals (HLD scope)**
- Full remote proctoring suite (beyond lite anti‑cheat).
- Offline desktop authoring tools (mobile/web only for now).

---

## 2) Personas & Core Use Cases
- **Aspirant (Beginner/Intermediate):** discover exam → generate/take mocks → download result PDF → follow guided plan.
- **Advanced Aspirant:** topic/difficulty targeting, time management analysis, streaks, and revision scheduling.
- **SME/Editor:** curate syllabi, review/approve AI questions, maintain quality.
- **Institute/Coach (B2B):** batch/class management, assign tests, view cohort analytics, custom branding.

---

## 3) System Context & Topology
```
[User Web (Next.js PWA)]   [Mobile (React Native later)]
              |                          |
              v                          v
           [API Gateway / Ingress + WAF / RateLimiter]
                               |
                          [FastAPI App]
         ┌───────────────┬───────────────┬─────────────────────┐
         v               v               v                     v
   [Auth & Identity] [Catalog]   [Quiz & Attempts]     [AI Orchestrator]
         |               |               |                     |
         v               v               v                     v
     [PostgreSQL]   [PostgreSQL]    [PostgreSQL]           [Redis Queue]
                                                             |      
                                                             v
                                                      [AI Workers]
                                                             |
                                                 [OpenAI/Provider Abstraction]

      [Reporting/PDF Service] <---- HTML payload ---- [FastAPI]
               |  (Node+Puppeteer or Playwright)                
               v
            [S3/MinIO]  <-- presigned URLs -->  Client

   [Search (OpenSearch or PG FTS)]     [Analytics (ClickHouse/BigQuery later)]
   [Notifications (email/SMS/push)]    [Payments & Credits]
```

**Style:** Start as a **modular monolith** (clear domain modules within one FastAPI codebase) → split to services once modules require independent scaling (e.g., AI, PDF, Analytics).

---

## 4) Technology Selections (Justification)
- **Frontend:** Next.js (App Router), React 18, TanStack Query (data), i18n‑ready; PWA for installability.
- **Backend:** FastAPI (async, OpenAPI native), Pydantic v2, uvicorn/gunicorn.
- **DB:** PostgreSQL 16 (strict schema, JSONB for flexible configs), Alembic for migrations.
- **Cache/Queue/Rate‑limit:** Redis 7 (TTL caches; Celery/RQ for jobs; sliding‑window rate limiting).
- **Object Storage:** S3/MinIO for PDFs/exports; presigned URLs.
- **Search:** Phase‑1 Postgres FTS → Phase‑2 OpenSearch for autocomplete and typo tolerance.
- **PDF:** Dedicated **Renderer** (Node + Puppeteer/Playwright) for pixel‑perfect exports.
- **Observability:** OpenTelemetry, Prometheus + Grafana, Loki (logs), Sentry (errors).
- **CI/CD:** GitHub Actions (lint/test/build/migrate/deploy). Docker Compose (dev) → K8s (prod).
- **Payments:** Razorpay/Stripe (UPI/cards), GST‑ready invoices.

---

## 5) Domain Modules (within FastAPI)
1. **Auth & Identity** – email/OTP + password, OAuth (Google) optional; JWT access/refresh, device tokens, RBAC/ABAC, audit logs.
2. **Catalog** – India‑wide taxonomy: states → exam bodies → exams → syllabi → topics; versioned syllabi.
3. **Question Bank** – normalized questions & options, difficulty, language, explanation, version, status, checksum de‑dupe.
4. **Quiz Orchestrator** – quiz configs, assembly, attempts, scoring, negative marking, randomization.
5. **AI Orchestrator** – prompt templates, provider abstraction, schema validation, cost tracking, caching, moderation flags.
6. **Reporting/PDF** – builds HTML result payloads; Renderer service returns PDFs to S3; presigned download links.
7. **Search** – index management; cross‑entity search; autocomplete.
8. **Analytics & Guidance** – mastery metrics, topic heatmaps, study plan generator (spaced repetition / weak‑area targeting).
9. **Payments & Credits** – wallet, transactions, entitlements, subscriptions (feature flags wired, enable later).
10. **Notifications** – email/SMS/WhatsApp/push; templating; delivery audits.
11. **Community/Q&A** – threads on questions/quizzes; moderation tools.
12. **Institutes (B2B)** – organizations, batches, assignments, cohort dashboards, branding.

---

## 6) Data Model (High‑level)
**Catalog**
- `states(id, name, code)`
- `exam_bodies(id, state_id?, name, scope enum[national,state])`
- `exams(id, body_id, name, level, languages[], active)`
- `syllabi(id, exam_id, version, notes)`
- `topics(id, syllabus_id, parent_id?, title, difficulty_band)`

**Users & Monetization**
- `users(id, email, phone?, pass_hash, role, status, locale, tz, created_at)`
- `user_profiles(user_id, display_name, city, state_id?, meta jsonb)`
- `wallets(user_id, balance_credits)`
- `transactions(id, user_id, type[credit|debit], amount, reason, gateway_ref, created_at)`
- `plans(id, name, price, period, entitlements jsonb)`
- `subscriptions(id, user_id, plan_id, status, start, end)`
- `entitlements(id, code, description)` + `user_entitlements(user_id, entitlement_id, source, valid_from, valid_to)`

**Content & Quizzes**
- `question_bank(id, exam_id, topic_id, stem, explanation, difficulty, source[ai|manual], language, status, checksum, version)`
- `question_options(id, question_id, text, is_correct, order_idx)`
- `quiz_templates(id, exam_id, title, config jsonb)`
- `quizzes(id, exam_id, owner_user_id, title, config jsonb, generated_from_template_id?, status)`
- `quiz_questions(quiz_id, question_id, order_idx)`
- `attempts(id, quiz_id, user_id, started_at, finished_at, score_raw, score_pct, duration_sec, breakdown jsonb)`
- `attempt_answers(attempt_id, question_id, selected_option_id, is_correct, time_spent_ms)`

**AI & Ops**
- `ai_jobs(id, type[generate_questions|explanations], payload jsonb, status, provider, token_cost, created_at, completed_at, error_msg)`
- `ai_content(id, ai_job_id, content_type[questions|rationales], content jsonb, checksum)`
- `audit_logs(id, actor_user_id, action, entity, entity_id, meta jsonb, created_at)`

**Community & B2B**
- `threads(id, entity_type[question|quiz], entity_id, title?, created_by, status)`
- `posts(id, thread_id, body, created_by, status, created_at)`
- `institutes(id, name, branding_json, owner_user_id)`
- `batches(id, institute_id, name)`
- `enrollments(batch_id, user_id, role[teacher|student])`

---

## 7) Key API Surfaces (High‑level)
**Auth**
- `POST /auth/register`, `POST /auth/login`, `POST /auth/otp`, `POST /auth/refresh`, `GET /auth/me`, `POST /auth/logout`

**Catalog**
- `GET /catalog/states`
- `GET /catalog/exam-bodies?stateId=...`
- `GET /catalog/exams?bodyId=...`
- `GET /catalog/topics?examId=...`

**Syllabi & Questions (admin/editor)**
- `POST/PATCH /syllabi`, `POST/PATCH /topics`
- `GET /questions?examId&topicId&difficulty&status`
- `PATCH /questions/:id` (approve/disable/edit)

**Quizzes & Attempts**
- `GET /quizzes?examId=...`
- `POST /quizzes` (manual config)
- `POST /attempts` → start
- `POST /attempts/:id/answer` (idempotent)
- `POST /attempts/:id/finish`
- `GET /attempts/:id/pdf` → signed URL

**AI Jobs**
- `POST /ai/jobs` (generate questions/explanations)
- `GET /ai/jobs/:id`

**Payments & Credits**
- `GET /wallet/me`, `POST /wallet/charge`, `GET /transactions`
- `GET /plans`, `POST /subscriptions`, `PATCH /subscriptions/:id`

**Community & B2B**
- `POST /threads`, `POST /posts`, moderation endpoints
- `POST /institutes`, `POST /batches`, `POST /assignments`

_All endpoints: OpenAPI documented, request/response schemas validated (Pydantic)._

---

## 8) Critical Flows
### A) Dependent Dropdown → Exam → Quiz List/Generate
1. Client fetches `states` → `exam_bodies?stateId` → `exams?bodyId` → `topics?examId`.
2. Show available quizzes for that exam.
3. If none match filters, user configures → **Generate via AI**.

### B) AI Quiz Generation
1. Client `POST /ai/jobs` with `{ examId, topics[], numQuestions, difficultyMix, timeLimit, language }`.
2. API validates entitlements & rate limits → enqueue job in Redis.
3. Worker builds prompt from syllabus+constraints → provider (OpenAI) → schema validation/dedupe.
4. Persist to `question_bank` → assemble `quiz` + `quiz_questions` → job status `done`.
5. Client polls `GET /ai/jobs/:id` → navigates to new quiz.

### C) Attempt & Scoring
1. `POST /attempts` to start (returns time limit, shuffled question order & options seed).
2. Client submits answers idempotently; server stores and computes correctness.
3. Finish computes scores (raw, %), topic breakdown, time analytics.
4. Result page offers **Download PDF** (server creates HTML → Renderer → S3 → presigned link).

### D) SME Review
1. Editors view newly generated questions → approve/edit/disable.
2. Versioning ensures future quizzes use latest approved content.

### E) Payments & Credits
1. Wallet purchase → gateway webhook → credit wallet → entitlements applied.
2. AI generation decrements credits; free daily quota via config.

---

## 9) AI Strategy & Safety
- **Provider Abstraction**: `AIProvider` interface (OpenAI today; Anthropic/Local later).
- **Prompting**: domain‑specific system prompts; deterministic JSON schema.
- **Validation**: structural (JSON Schema), semantic (single correct option, duplicates, length limits), heuristics for quality.
- **De‑duplication**: checksum of normalized content.
- **Cost Tracking**: store token usage per job; budget guards; per‑user/day caps.
- **Human‑in‑the‑loop**: SME queues + sampling audits.
- **Policy/Content safety**: toxicity/offensiveness checks.

---

## 10) Security & Compliance
- **AuthN/Z**: JWT access + refresh; RBAC/ABAC; per‑route guards.
- **Transport & At‑Rest**: TLS; PII in Postgres with encryption at rest; secrets in vault (KMS/SSM/Secrets Manager).
- **Rate Limiting & Abuse**: sliding window on auth/AI routes; CAPTCHA on risky endpoints.
- **Data Protection (DPDP/GDPR‑ready)**: consent, profile/data export, deletion, retention windows.
- **Audit Logs**: admin/SME sensitive actions.
- **Anti‑cheat (lite)**: option/sequence randomization; attempt time heuristics; tab‑switch detection (B2B opt‑in).

---

## 11) Internationalization & Accessibility
- Content language stored at entity level (question.language).
- Next.js i18n routing; localized UI copy via message catalogs.
- Font fallback sets for Indic scripts; RTL‑ready layout.
- Accessibility: WCAG AA, keyboard nav, color contrast, dyslexia‑friendly mode.

---

## 12) Performance & Scalability
- **API**: async FastAPI; connection pooling; N+1 avoidance; query planning.
- **DB**: proper indexing (exam/topic/difficulty), read replicas as traffic grows.
- **Caching**: Redis for hot lists (catalog, quiz headers), presigned URL caching.
- **Queues**: Redis + Celery/RQ for AI & PDF; autoscale workers.
- **CDN**: static assets & PDFs via CDN; regional edge caching.
- **Search**: move to OpenSearch when FTS relevance/scale requires.

**SLOs (initial)**
- Availability 99.9%
- P95 API latency < 300ms (catalog/quiz read), < 600ms (write)
- AI job success ≥ 99% (excluding provider outages)

---

## 13) Observability & Quality
- **Tracing**: OpenTelemetry (correlate web→API→worker→provider).
- **Metrics**: Prometheus (API throughput, job durations, queue depth, DB latency).
- **Logs**: JSON logs to Loki; PII redaction.
- **Error Tracking**: Sentry with release health.
- **QA**: pytest + coverage gates; Playwright E2E for flows; k6 load tests.

---

## 14) DevOps & Environments
- **Dev**: docker‑compose (Postgres, Redis, MinIO, Renderer, OpenSearch optional).
- **Stage/Prod**: K8s; blue/green deploys; Alembic migrations gated & reversible.
- **Backups/DR**: nightly Postgres snapshot; object storage versioning; restore runbooks.
- **Secrets**: managed via SSM/Secrets Manager; rotation SOPs.

---

## 15) Roadmap (Phased Execution)
- **M0 Foundations (Weeks 0–3):** repo scaffolding (monorepo), auth/RBAC, audit logs, catalog CRUD + seed; CI/CD; observability baseline.
- **M1 Quiz MVP (Weeks 4–8):** question/quiz/attempt models & APIs; attempt UI; scoring; PDF V1.
- **M2 AI & Quality (Weeks 9–14):** AI jobs, prompts, validation; SME console; search V1 (PG FTS).
- **M3 Guidance & Growth (Weeks 15–22):** mastery analytics, study planner; community threads; referrals, streaks.
- **M4 Monetization & B2B (Weeks 23–32):** credits wallet, payments, subscriptions; institutes portal.

---

## 16) Risks & Mitigations
- **AI cost blowups** → credits, quotas, caching/reuse, quality thresholds to avoid re‑gens.
- **Low content quality** → SME review, A/B sampling, difficulty calibration.
- **Scale spikes (seasonal exams)** → autoscale workers, queue backpressure, CDN, pre‑generated popular mocks.
- **Provider outages** → fallback providers, exponential backoff, job retry policies.
- **Compliance drift** → data map, DSR endpoints, periodic audits.

---

## 17) Reference Implementation Skeleton (suggested)
```
repo/
  apps/
    api/           # FastAPI app (modular packages)
    renderer/      # Node + Puppeteer PDF service
    web/           # Next.js (App Router)
  packages/
    schema/        # Pydantic models / OpenAPI contracts shared
    prompts/       # Prompt templates, JSON Schemas
  infra/
    docker-compose.yml
    k8s/           # manifests/helm charts
  docs/
    HLD.md  LLD/ADR/Runbooks
```

---

## 18) Next (post‑HLD) Deliverables
- **LLD** for each module (Auth, Catalog, Quiz, AI, PDF, Payments).
- **DB Migrations (Alembic)** + seed scripts for top exams.
- **OpenAPI spec** + client SDKs (typescript‑fetch, python)
- **Worker blueprints** (Celery/RQ) with retries/backoff.
- **Renderer contract** (HTML in → PDF out) + componentized HTML templates.
- **Monitoring dashboards** (Grafana) + alert rules.



---

## 19) Student Exam Experience — End‑to‑End UX (Screens, Flows, Best Practices)

### 19.1 Objectives
- Deliver a modern, low‑friction, mobile‑first testing experience with strong reliability on unstable networks.
- Support official patterns students expect (palette states, review/flag, auto‑save) and new value adds (explanations, analytics, study planning).
- Be multilingual, accessible (WCAG AA), and friendly for long sessions.

### 19.2 Screen Inventory (Student)
1. **Onboarding** (Exam Preferences)
2. **Home Dashboard** (goals, resume, weak topics)
3. **Exam Browser** (State → Body → Exam) + search & filters
4. **Topic Selector** (tree, chips) + difficulty/time/number of questions
5. **Quiz List** (saved/available) + **Generate via AI** (job status)
6. **Pre‑Exam Check**
   - Device & network check; font size/theme; language selection; calculator policy; instructions
7. **Exam Instructions** (mandatory scroll + accept)
8. **Test Player** (core exam UI)
9. **Review Page** (question list with states; jump to any)
10. **Submit Flow** (warnings, unanswered tally, confirm)
11. **Result Summary** (score, accuracy, time, topic heatmap)
12. **Detailed Analysis** (per‑topic, per‑difficulty, time per Q, error types)
13. **Solutions & Explanations** (inline step‑by‑step; report issue; discuss)
14. **Download PDF** (result + answer key)
15. **Retake / Variant Generator**
16. **Study Plan** (auto‑generated; calendar integration)
17. **Doubts / Discussions** (thread per question)
18. **Achievements & Streaks** (gamification)
19. **Notifications Center** (exam dates, reminders, replies)
20. **Profile & Settings** (language, accessibility, privacy)

### 19.3 Detailed Flows
#### A) Discover → Configure → Generate
- User selects State → Exam Body → Exam.
- Topic multi‑select (chips + search + "Select all in section").
- Controls: **#Questions**, **Time Limit**, **Difficulty Mix** (E/M/H slider or presets), **Language**.
- If no prebuilt quiz matches → CTA **Generate via AI**. Enqueue job; show status (queued/running/done) with toast + progress.

#### B) Pre‑Exam Check & Instructions
- Quick device/network test (ping + throughput), offline‑grace warning if weak.
- Accessibility presets: font size, dyslexia‑friendly, high contrast, theme (light/dark/system).
- Policy toggles (if B2B exam mode): allow calculator/scratchpad; paste disabled; tab switch warnings.
- Instructions require full‑page scroll + explicit checkbox before **Start Test**.

#### C) Test Player (Core UX)
- Layout (responsive):
  - **Top bar**: Exam name, section, **Timer** (mm:ss), connection badge (Online/Syncing/Offline‑saving), submit button.
  - **Main area**: question stem (MathJax/KaTeX support), images with zoom, code/pre blocks if needed.
  - **Options**: 4–5 options, large touch targets; keyboard shortcuts A/B/C/D; **Mark for Review** toggle.
  - **Right/Bottom panel** (adaptive): question palette with states:
    - Not visited, Viewed, Answered, Marked for Review, Answered+Review.
  - **Tools**: calculator (if enabled), on‑screen numeric keypad (mobile), rough‑work scratchpad, zoom controls, report issue, bookmark.
- **Navigation**: Previous/Next buttons; direct jump via palette; section dropdown (if multi‑section).
- **Auto‑save**: on option select and every 5s; idempotent server writes.
- **Timer**: visible with color cues at 10/5/1 minutes; optional long‑press to hide for anxiety‑sensitive users.
- **Offline & Reconnect**: local queue of answers; background sync; visual re‑sync confirmation.
- **Anti‑cheat (lite)**: tab switch count; excessive copy events → soft warning; B2B: optional camera proctoring (future).

#### D) Review & Submit
- **Review page**: table/palette with filters: Unanswered, Marked, Visited; quick jump.
- **Submit**: show unanswered count; confirm modal; final sync; lock test; server computes score.

#### E) Results & Post‑Exam
- **Summary**: Score (raw & %), accuracy, time spent, rank/percentile (if cohort available), topic heatmap, difficulty mix.
- **Suggested actions**: weak topics → targeted practice; auto **Study Plan** with spaced repetition.
- **Solutions**: each Q with correct option, your answer, explanation; related reading links.
- **Doubts**: per‑question thread; @mention mentors; report content issue.
- **Download**: PDF (watermarked) with answer key & highlights.
- **Retake**: same quiz or **Generate Variant** (preserve config, new items).

### 19.4 Test Player Interaction Spec
- **Keyboard**: 1–4 to choose; R to mark review; N/P to navigate; G to go to; S to submit; +/- to zoom.
- **Mobile gestures**: swipe L/R to navigate; long‑press on option to expand explanation (post‑submit only).
- **Visual states**: color‑blind safe palette; focus rings for accessibility; high contrast mode ensured.
- **Math & Media**: KaTeX render; image pinch‑zoom; alt text; captions.
- **Error handling**: sticky banner on sync failure; retry policy exponential; local persistence until ACK.

### 19.5 Edge Cases & Reliability
- Browser refresh/reopen → **restore attempt** (token + attempt lock), resume timer server‑side.
- Network loss during submit → queue final payload, keep user on “Submitting…” with fallbacks; generate receipt id.
- Multi‑device login → block second start or handoff with confirmation (configurable).
- Time expiry mid‑question → auto‑submit with last known answers.
- Daylight/timezone mismatch → server authoritative timer; client is cosmetic.

### 19.6 Accessibility & Localization
- WCAG AA color contrast; semantic roles/landmarks; ARIA for palette and options.
- Screen reader labels for option letters and states.
- Adjustable font size; dyslexia‑friendly font toggle; focus‑visible.
- Full i18n for UI + content; per‑question language; right‑to‑left ready.

### 19.7 Analytics & Telemetry (events)
- `attempt_started`, `question_viewed`, `answer_selected`, `marked_for_review`, `attempt_submitted`, `attempt_restored`, `network_offline`, `network_online`, `time_warning_5m`, `solution_viewed`, `pdf_downloaded`, `variant_generated`.
- Dimensions: exam_id, topic_id, device, lang, latency, reconnect_count.

### 19.8 Notifications
- Before exam (reminder), post‑result (analysis ready), study plan tasks, mentor replies.
- Channels: push (PWA), email, WhatsApp/SMS (opt‑in).

### 19.9 Quality Gates (pre‑launch)
- Load: 5k concurrent attempts, P95 < 300ms read / < 600ms write.
- Chaos: kill network during attempt, Redis delay, AI provider 5xx.
- Browser matrix incl. low‑end Android; memory usage guard.
- A11y audit (axe), keyboard‑only runthrough; color‑blind checks.

### 19.10 APIs Touched (summary)
- `POST /quizzes` (manual) or `POST /ai/jobs` → `GET /ai/jobs/:id`
- `GET /quizzes?examId=...` → list
- `POST /attempts` → start
- `POST /attempts/:id/answer` (idempotent)
- `GET /attempts/:id` (state restore)
- `POST /attempts/:id/finish`
- `GET /attempts/:id/pdf`

### 19.11 PDF Spec (Result)
- Cover: user, exam, attempt info, score, time, accuracy.
- Body: per‑question table (your answer, correct, explanation), topic breakdown charts.
- Footer: watermark, share QR, disclaimer.

### 19.12 Future Enhancements
- Sectional timing; composite exams with multiple sections.
- Adaptive testing mode (item response theory‑lite).
- Proctored mode (camera/mic), plagiarism checks (B2B).
- Offline attempted cache with conflict resolution.



---

## 20) Exam Pattern & Assembly Architecture (India‑wide)
**Goal:** Model diverse govt. exam formats once, assemble tests consistently across SSC/IBPS/Railways/State PCS/Teaching, etc.

### 20.1 Pattern Model
- **Exam Pattern**: overall time, negative marking, navigation policy.
- **Sections**: name, optional sectional timer, order, shuffle policy, allow review (Y/N).
- **Constraints**: per‑section topic quotas (min/max), difficulty mix (E/M/H), language, include/exclude tags.
- **Scoring Strategies**: {+1/–0.25, +2/–0.5, zero‑neg, partial for multi‑correct}.
- **Navigation Policies**: free navigation; section‑locked; one‑pass.

### 20.2 Assembly
- **Blueprint → Formization**: resolve constraints to concrete item set; freeze order per section; persist **form hash** to avoid near‑dupes.
- **Equating (lite)**: maintain difficulty parity across alternate forms via target distribution matching.

---

## 21) Question Types & Grouping
**Supported types**: Single‑correct (SCQ), Multi‑correct (MCQ), Numeric Entry, Assertion‑Reason, **Passage/Set** (parent stem with sub‑items).
- Schema adds: `question_type`, `max_correct`, `group_id` (for passage/set), `tags[]`.
- Rendering: KaTeX for math, image attachments with alt text & zoom.
- Scoring rule per item (supports partial for MCQ).

---

## 22) Item Quality & Calibration
- **Item Stats**: facility index (p‑value), discrimination (point‑biserial), avg time, attempts; nightly refresh.
- **Test Reliability**: KR‑20/Cronbach’s alpha per form; flag low‑reliability forms.
- **Lifecycle**: draft → approved → active → **deprecate/retire** based on stats/complaints.
- **Auto‑recommend retire/replace** when p‑value too low/high or discrimination < threshold.

---

## 23) Blueprints & Fixed Forms (Reuse‑first)
- **Blueprints** capture constraints; reusable per exam & language.
- **Fixed Forms** generated from blueprints for instant delivery and peak‑time stability.
- **Reuse policy**: when a student requests a configuration ~equivalent to an existing form in last N hours, serve the form; else enqueue AI generation.
- **Form Hashing**: normalized content hash to prevent intra‑form and cross‑form duplicates.

---

## 24) AI Generation Policy & Cost Control
- **Hierarchy**: Reuse existing form → Use warm pool → Generate via AI.
- **Quotas**: daily free allowance, tiered credits; institute pools.
- **Pre‑warm**: nightly generation for top 50 blueprints per exam (seasonal awareness).
- **De‑dup**: checksum on items and forms; reject near‑duplicates; backoff/retry policy with alternate prompts.
- **Budget guards**: per‑user/day caps, global cap, alerts on burn rate.

---

## 25) CMS (Python API + Next.js Admin) — Governance & Ops
### 25.1 Roles
Admin, Content Manager, SME/Editor, Auditor, Support, Institute Admin (B2B).

### 25.2 Workflows
- Content state machine: **Draft → AI‑pending → SME Review → Approved → Published → Retired**.
- Assignment & SLAs: queues per editor; due dates; reminders.
- Bulk ops: CSV/Excel import; mass status change; topic tree editor with drag‑drop.

### 25.3 Versioning & Publishing
- Syllabus versions with diff & rollback; time‑boxed releases; region/language targeting.
- Asset library for diagrams/images with usage tracking.

### 25.4 Admin Screens (Next.js)
Dashboard • Exams & Patterns • Syllabus Builder • Question Bank & Review Queue • Blueprints & Formize • Releases • Institutes & Batches • Users & Entitlements • Notifications • Audit & Logs • Settings

---

## 26) B2B Institutes (Optional, High Value)
- Organizations with branding; custom domains.
- Batches/classes, enrollments, scheduled/locked tests, cohort analytics.
- Optional proctoring‑lite (tab switches, camera opt‑in), center‑wise CSV exports.

---

## 27) Personalization & Guidance
- **Recommendation service**: next quiz from weakest‑topic × time‑since‑seen; integrates with study plan.
- **Spaced repetition** queues per topic; revision cards from incorrect/slow items.
- **Nudges**: streaks, weekly goals; calendar integration for planned sessions.

---

## 28) Data Model — Additions & Changes
**Exam Patterns**
- `exam_patterns(id, exam_id, name, overall_time_sec, negative_marking_json, policy_json)`
- `exam_sections(id, pattern_id, name, time_sec, order_idx, shuffle, allow_review)`
- `section_constraints(id, section_id, topic_id, min_q, max_q, difficulty_mix_json)`

**Blueprints & Forms**
- `blueprints(id, exam_id, title, config_json, language)`
- `test_forms(id, exam_id, blueprint_id, version, status)`
- `form_items(form_id, question_id, section_id, order_idx)`
- `form_hashes(form_id, content_hash)`

**Question Bank Extensions**
- add cols: `question_type`, `max_correct`, `group_id`, `tags jsonb`
- `item_stats(question_id, attempts, p_value, pbis, avg_time_ms, last_calc_at)`

**CMS Governance**
- `workflows(entity, entity_id, state, assigned_to, due_at)`
- `content_audit(entity, entity_id, change, actor, created_at)`

**B2B**
- `institutes(id, name, branding_json, owner_user_id)`
- `batches(id, institute_id, name)`
- `enrollments(batch_id, user_id, role)`

*(Existing tables for users, wallets, entitlements, quizzes, attempts remain; these are additive.)*

---

## 29) API Surfaces — New & Updated (FastAPI)
**Patterns & Sections**
- `GET /exams/{id}/pattern`
- `POST /patterns` • `PATCH /patterns/{id}`
- `POST /patterns/{id}/sections` • `PATCH /sections/{id}`

**Blueprints & Forms**
- `POST /blueprints` • `GET /blueprints?examId=...`
- `POST /forms` (materialize blueprint)
- `GET /forms?examId=...` • `GET /forms/{id}`

**Smart Generation**
- `POST /generate` → reuse best‑match form or enqueue AI; returns `{quizId?, jobId?}`

**Item Analytics**
- `GET /items/{id}/stats` • `POST /items/recalculate` (admin)

_All payloads validated via Pydantic; OpenAPI auto‑generated._

---

## 30) Critical Flows — Additions
- **Reuse‑Before‑Generate**: find nearest form by `(exam_id, pattern_id, topics, difficulty_mix, count, language)`; threshold match; fallback to AI.
- **Admin Blueprint → Form → Release**: preview fill, quality checks (topic/difficulty coverage, duplicate detector), publish to catalog.
- **Nightly Pre‑warm**: generate top‑K blueprint forms per exam; store ready for instant delivery.

---

## 31) Performance, SRE & Peak Readiness
- Separate workers for **AI** and **PDF**; autoscale independently.
- Queue backpressure with graceful UI (progress/ETA).
- Postgres read replicas for attempt reads; leader for writes; hot indexes on `(exam_id, topic_id, difficulty)`.
- CDN for static & PDFs; cache headers; presigned URLs.
- Synthetic monitoring for attempt start/submit; chaos drills (provider outages, Redis latency).

---

## 32) Acceptance Criteria (Feature‑level “Done”)
- **Student** can discover exam, configure (pattern/topic/difficulty/time/language), instantly start if form exists or generate if not, complete attempt reliably (autosave, offline queue), see analysis, and download PDF.
- **Admin/SME** can model any govt. pattern, create blueprints, generate forms (batch), review/approve AI items, publish on schedule, and audit all changes.
- **System** meets launch SLOs (5k concurrent attempts, P95 < 300/600ms, KR‑20 above threshold) and passes a11y checks.

---
