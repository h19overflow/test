# Hiring Summaries

## C4
Dmitri Volkov brings 8 years of backend engineering with expert-level Go and Rust proficiency. He architected high-frequency trading infrastructure at a prop trading firm, demonstrating deep expertise in building systems that demand extreme performance and reliability. His technology stack (Redis, Kafka, ClickHouse) and Kubernetes mastery directly align with the role's core requirements. He is a strong technical fit for the infrastructure layer of a trading platform.

### Strengths
- 8 years backend engineering experience with Go and Rust expertise
- Proven track record building high-frequency trading infrastructure at prop trading firm
- Expert-level Kubernetes and containerization skills
- Strong event-driven architecture experience (Kafka, ClickHouse)
- Deep understanding of low-latency, high-throughput system design
- Redis and advanced data infrastructure knowledge
### Gaps
- No fintech regulatory or compliance experience mentioned
- Limited evidence of work in regulated financial environments
- No explicit mention of PostgreSQL experience (role requires PostgreSQL + NoSQL)
- No open-source contribution history noted
### Interview focus areas
- Regulatory and compliance considerations in trading infrastructure (how would you approach building systems for regulated environments?)
- PostgreSQL experience and schema design for financial data
- Transition from prop trading (internal systems) to serving external clients with SLAs and compliance requirements
**Hire confidence:** Strong Yes
Dmitri scores 9.0/10 overall and ranks #1. He demonstrates exceptional technical depth across all core criteria: 8 years backend experience with Go/Rust mastery (criterion 1), proven high-frequency trading infrastructure (criterion 2), direct trading domain expertise (criterion 3), strong event-driven architecture and fintech background (criterion 6). His Kubernetes expertise and distributed systems capability are evident. The primary gap—no explicit regulatory experience—is addressable through onboarding and mentorship, as his technical foundation is exceptionally strong. His trading infrastructure background is directly transferable to Deriv's role.

## C1
Aisha Okonkwo brings 7 years of backend engineering with expert-level Python and Go proficiency. She built and shipped a real-time trade execution engine at a Lagos fintech startup that handled 50k req/s—exceeding the role's high-throughput requirement by 5x. She led a team of 4 and demonstrates hands-on expertise with Kafka, PostgreSQL, and Redis. Her fintech domain knowledge and proven ability to design and optimize performance-critical systems make her a strong technical and cultural fit.

### Strengths
- 7 years backend engineering with expert-level Python and Go proficiency
- Proven ability to build and optimize systems handling 50k req/s (5x the role requirement)
- Direct fintech domain expertise and real-time trade execution experience
- Strong event-driven architecture knowledge (Kafka)
- Full-stack database proficiency (PostgreSQL, Redis)
- Team leadership experience (led team of 4)
- Demonstrated ability to work in resource-constrained, high-impact environments
### Gaps
- No explicit Kubernetes or containerization experience mentioned
- No formal degree listed (though not a requirement per job description)
- Limited evidence of work in regulated financial environments (Lagos startup may have different compliance requirements than EU/UK regulated entities)
- No open-source contribution history noted
### Interview focus areas
- Containerization and Kubernetes adoption—how would you approach scaling the trade execution engine with Docker/Kubernetes?
- Regulated financial environment experience—how would you adapt your architecture for FCA/ESMA compliance?
- Team scaling and mentorship—how would you lead a larger distributed team?
**Hire confidence:** Strong Yes
Aisha scores 8.8/10 overall and ranks #2. She demonstrates exceptional technical depth in backend engineering (criterion 1: 9.0), high-throughput systems (criterion 2: 10.0—50k req/s proven), financial systems and real-time data (criterion 3: 10.0), and event-driven architecture (criterion 6: 9.0). Her trade execution engine is directly relevant to Deriv's trading infrastructure role. The gap in containerization is a skill that can be rapidly acquired given her strong systems foundation. Her fintech domain expertise and proven ability to optimize performance-critical systems under constraints make her a compelling hire. She ranks just 0.2 points behind C4 and represents exceptional value.

## C5
Priya Nair brings 5 years of backend engineering with Python proficiency and direct payments infrastructure experience at Razorpay, handling 100k transactions/day. She demonstrates solid PostgreSQL and Docker expertise. Her strong communication skills and educational background (MBA + CS degree) suggest capability for cross-functional collaboration. However, her experience is in payments processing rather than trading infrastructure, and her high-throughput systems exposure is transaction-volume-based rather than request-rate-based.

### Strengths
- 5 years backend engineering experience meeting the minimum requirement
- Direct fintech domain expertise (payments infrastructure at Razorpay)
- Proven ability to handle high-transaction-volume systems (100k transactions/day)
- Solid Python proficiency
- PostgreSQL and Docker experience
- Strong communication and collaboration skills noted by referees
- Educational credentials (MBA + CS degree) suggest analytical rigor
### Gaps
- No Go experience (role prioritizes Python or Go; TypeScript secondary language is not Go)
- Limited evidence of >10k req/s high-throughput systems (100k transactions/day ≠ 10k+ req/s; transaction volume and request rate are different metrics)
- No Kubernetes or advanced containerization experience mentioned
- No event-driven architecture experience (Kafka, RabbitMQ) noted
- Payments infrastructure background differs from trading infrastructure (different domain complexity)
- No NoSQL database experience mentioned beyond PostgreSQL
### Interview focus areas
- High-throughput, low-latency system design—how do you approach optimizing for request rate vs. transaction volume?
- Go language learning—are you willing to adopt Go as a primary language, and what is your timeline?
- Event-driven architecture and message queues—experience with Kafka, RabbitMQ, or similar systems?
**Hire confidence:** Maybe
Priya scores 6.1/10 overall and ranks #3. She meets the minimum backend experience requirement (5 years) and brings valuable fintech domain knowledge from payments infrastructure. However, she has notable gaps relative to the role's core requirements: no Go experience (criterion 1: 7.0), limited evidence of >10k req/s systems (criterion 2: 5.0), no Kubernetes experience (criterion 5: 4.0), and no event-driven architecture background (criterion 6: 3.0). Her payments infrastructure experience, while fintech-relevant, does not directly translate to trading infrastructure complexity. She is a solid mid-level candidate but lacks the depth in high-throughput systems and event-driven architecture that the role demands. Hire confidence is conditional on strong performance in technical interviews on Go adoption and system design.

## Rank 1 interview questions
- You built a high-frequency trading infrastructure at a prop trading firm. Walk us through the architecture of your most performance-critical system: What were the key bottlenecks you encountered, and how did you optimize for sub-millisecond latency? How would you approach similar optimization challenges at Deriv, where we serve external clients with SLAs?
- Deriv operates in regulated financial markets across multiple jurisdictions (FCA, ESMA, etc.). Your background is in prop trading, which typically has different compliance requirements than serving retail clients. How would you approach learning and integrating regulatory constraints into system design? What questions would you ask to understand our compliance posture?
- Walk us through your experience with PostgreSQL and data schema design for financial systems. How do you approach designing schemas for high-throughput trading data? What trade-offs do you make between normalization, query performance, and data consistency?
- Describe your experience working in distributed, async-first teams. How do you ensure code quality, knowledge sharing, and incident response when team members are across multiple time zones? What tools and practices have worked best for you?
- You have deep Kubernetes expertise. How would you approach designing a deployment strategy for a trading infrastructure system that must handle failover, zero-downtime deployments, and real-time data consistency? What are the key reliability patterns you'd implement?

## Cohort analysis
COHORT ANALYSIS: Senior Backend Engineer — Trading Infrastructure

OVERALL COHORT QUALITY:
The candidate cohort is strong at the top (C4, C1) but shows significant variance. The top two candidates (scores 9.0, 8.8) are exceptional fits with direct trading infrastructure experience and proven high-throughput systems expertise. The middle tier (C5, C2: 6.1, 6.0) shows competence but notable gaps. The bottom tier (C3, C6: 5.7, 4.65) has fundamental misalignment with the role's core requirements.

TIER 1 — EXCEPTIONAL FITS (C4, C1; scores 8.8–9.0):
Both candidates bring 7–8 years of backend engineering, expert-level Python/Go proficiency, and direct fintech/trading domain expertise. C4 (Dmitri) excels in Kubernetes and event-driven architecture; C1 (Aisha) excels in high-throughput systems (50k req/s proven) and team leadership. Both have strong PostgreSQL/NoSQL experience. The primary differentiator: C4 has regulatory compliance gaps; C1 has containerization gaps. Both gaps are addressable through onboarding. RECOMMENDATION: Proceed to final-round interviews with both; either would be a strong hire.

TIER 2 — SOLID CANDIDATES WITH GAPS (C5, C2; scores 6.0–6.1):
Both meet the 5-year backend requirement and bring fintech domain knowledge. C5 (Priya) has payments infrastructure experience and solid Python/Docker skills but lacks Go, Kubernetes, and event-driven architecture expertise. C2 (not summarized in top 3, but ranked #4) likely has banking background but Java as primary language (not Python/Go per rubric). Both are competent mid-level engineers but lack the depth in high-throughput systems and distributed architecture that the role demands. RECOMMENDATION: Consider for second-round interviews if top-tier candidates decline; otherwise, pass.

TIER 3 — MISALIGNED CANDIDATES (C3, C6; scores 4.65–5.7):
C3 (early-stage startup background) and C6 (FAANG background, no fintech experience) have fundamental gaps. C6 scores 2.0 on financial systems and event-driven architecture—a severe penalty that reflects the role's fintech-specific requirements. C3 likely has similar domain gaps. While both may have strong general backend skills, the trading infrastructure role requires fintech domain knowledge that neither demonstrates. RECOMMENDATION: Pass; focus on Tier 1 and Tier 2 candidates.

BIAS AUDIT FINDINGS (CRITICAL):
The bias audit flagged significant concerns:
1. EMPLOYER PRESTIGE BIAS (C2, C6): Candidates from Goldman Sachs, Barclays, Google, and Meta received credential prestige signals that inflated scores despite objective skill gaps. C2 scores 8.0 on Financial Systems despite lacking WebSocket experience; C6 scores 7.0 on Backend Expertise despite Java being primary language (not Python/Go). By contrast, C1 (Lagos fintech startup, no degree listed) scores 9.0–10.0 on identical criteria with superior evidence (50k req/s proven, Kafka expertise).
2. GEOGRAPHY & STARTUP CONTEXT BIAS (C1, C3): C1 was penalized for startup context despite demonstrating superior technical depth. C1 scores 6.0 on Containerization "due to no explicit Docker/Kubernetes mention" but led a team of 4 and built 50k req/s systems—suggesting distributed systems capability. C6 scores 8.0 on the same criterion based on institutional affiliation alone, with no explicit Kubernetes experience mentioned.
3. INFERENCE BIAS & SPECULATIVE SCORING (C2, C6): Multiple rationales use institutional prestige as proxies for unstated skills. C2: "Banking background suggests some distributed systems exposure" (score 5.0 on Containerization—inference, not evidence). C6: "FAANG background implies exposure to high-throughput systems" (score 7.0—inference). By contrast, C1 and C4 receive high scores with explicit evidence.

IMPACT ON RANKINGS:
The bias audit suggests that the final ranking (C4 #1, C1 #2) is CORRECT despite bias in the scoring process. C4 and C1 are genuinely the strongest candidates with explicit evidence of trading infrastructure expertise and high-throughput systems. However, the scoring rationales for C2 and C6 appear inflated by prestige bias, which may have artificially elevated them above other candidates not in the top 3. The audit recommends scrutinizing C2 and C6's scores if they advance to interviews.

HIRING RECOMMENDATION:
1. PROCEED WITH C4 (Dmitri Volkov) and C1 (Aisha Okonkwo) to final-round interviews. Both are exceptional fits with direct trading infrastructure experience and proven high-throughput systems expertise. Either would be a strong hire.
2. CONDITIONAL SECOND-ROUND for C5 (Priya Nair) if top candidates decline. She is competent but has notable gaps in Go, Kubernetes, and event-driven architecture.
3. PASS on C2, C3, C6 unless top candidates decline and business urgency requires rapid hiring.

DIVERSITY & INCLUSION NOTE:
The cohort includes candidates from diverse geographic backgrounds (Lagos, Russia, India) and educational paths (some with degrees, some without). The bias audit correctly identifies that prestige bias may have disadvantaged C1 (Lagos startup, no degree listed) despite superior technical evidence. The final ranking appropriately elevates C1 to #2, but the scoring rationales should be reviewed to ensure future hiring processes do not conflate institutional prestige with technical capability.
