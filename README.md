# SupportGPT

> **AI customer support assistant** — FAQ matching, sentiment-aware escalation, and LLM-generated responses. Built with Amazon Bedrock (Claude) and FastAPI.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Amazon Bedrock](https://img.shields.io/badge/powered%20by-Amazon%20Bedrock-orange.svg)](https://aws.amazon.com/bedrock/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)](https://www.docker.com/)

---

## Live Demo

> **[Coming soon — deploying to Hugging Face Spaces]**
>
> To run locally, follow the [Quick Start](#quick-start) below.

---

## What Problem This Solves

Most customer support workloads are repetitive: the same 20 questions account for 80% of tickets. SupportGPT handles those automatically via a FAQ layer, uses sentiment analysis to detect frustrated customers before they escalate themselves, and falls back to Claude for everything else. Human agents only see the hard cases.

---

## Demo

```
Customer: "How do I return an item?"
SupportGPT: [FAQ match] "Returns are accepted within 30 days with original receipt..."
handled_by: faq | sentiment_score: 0.72 | escalate: false

Customer: "I've been waiting 3 weeks and NOBODY is helping me this is unacceptable"
SupportGPT: [Escalating to human agent — frustrated customer detected]
handled_by: escalation | sentiment_score: 0.18 | escalate: true

Customer: "Can you explain your enterprise pricing options?"
SupportGPT: [Bedrock] "Our enterprise plans are customized based on team size and usage..."
handled_by: llm | sentiment_score: 0.65 | escalate: false
```

**Ticket summary (auto-generated at end of session):**
```
Session: 3 messages | Duration: 4 minutes
Topics: returns policy, shipping delay, enterprise pricing
Escalated: Yes (message 2 — high frustration detected)
Recommended action: Follow up on shipping delay
```

---

## Architecture

```
Customer message
       │
       ▼
FAQ Knowledge Base
(keyword matching)
       │
  match found? ──── yes ──────────────────── Return FAQ answer
       │                                      handled_by: "faq"
      no
       │
       ▼
Sentiment Analysis
(keyword scoring, 0.0–1.0)
       │
  score < 0.3? ──── yes ──────────────────── Escalate to human
       │                                      handled_by: "escalation"
      no
       │
       ▼
Amazon Bedrock
(Claude 3 Haiku)
       │
       ▼
Response + metadata ──────────────────────── Return LLM answer
(handled_by, sentiment_score, escalate)       handled_by: "llm"

Session Summary (on request):
All messages → Bedrock prompt → structured ticket summary
```

**Key design decisions:**
- FAQ layer runs first — avoids unnecessary Bedrock API calls for common questions
- Sentiment check blocks escalatable cases before LLM even runs — no wasted tokens on frustrated customers
- Every response includes `handled_by` metadata — makes the routing logic fully observable
- In-memory sessions by default — swap to Redis for production multi-instance deployments

---

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Amazon Bedrock (Claude 3 Haiku) |
| Sentiment Analysis | Keyword scoring (swap to AWS Comprehend for production) |
| FAQ Matching | Keyword search (swap to FAISS/semantic for production) |
| API | FastAPI + uvicorn |
| Frontend | Streamlit |
| Session Storage | In-memory (Redis recommended for production) |
| Containerization | Docker |

---

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/Rajeshdevandla/support-gpt.git
cd support-gpt
cp .env.example .env
# Fill in your AWS credentials
```

Required environment variables:

| Variable | Description | Default |
|---|---|---|
| `AWS_REGION` | AWS region | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | IAM user access key | required |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key | required |
| `BEDROCK_MODEL_ID` | Bedrock model | `claude-3-haiku` |
| `SENTIMENT_THRESHOLD` | Escalate below this score | `0.3` |

> **AWS setup:** IAM user needs `bedrock:InvokeModel` permission. Enable Claude 3 Haiku in Amazon Bedrock for your region.

### 2. Install and run

```bash
pip install -r requirements.txt

# Start the API
uvicorn api.main:app --reload

# Start the frontend (separate terminal)
streamlit run frontend/app.py
```

### Run with Docker

```bash
docker build -t support-gpt .
docker run -p 8000:8000 --env-file .env support-gpt
```

---

## API Reference

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/session/start` | Start a new support session |
| `POST` | `/chat` | Send a message, get a response |
| `GET` | `/session/{id}/summary` | Get conversation summary for ticket |

**Start a session:**
```bash
curl -X POST http://localhost:8000/session/start
# returns: { "session_id": "abc123" }
```

**Send a message:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc123", "message": "How do I return an item?"}'
```

**Response format:**
```json
{
  "response": "Returns are accepted within 30 days with original receipt...",
  "handled_by": "faq",
  "escalate": false,
  "sentiment_score": 0.72
}
```

---

## Project Structure

```
support-gpt/
├── config.py                  # env vars, validated at startup
├── core/
│   └── chatbot.py             # FAQ matching, sentiment, Bedrock integration
├── api/
│   └── main.py                # FastAPI routes
├── frontend/
│   └── app.py                 # Streamlit chat UI
├── requirements.txt
├── .env.example
└── Dockerfile
```

---

## What I'd Build Next

- **Semantic FAQ matching** — replace keyword search with FAISS embeddings so "how do I send back a product" matches the returns FAQ
- **AWS Comprehend sentiment** — replace keyword scoring with the actual AWS Comprehend API for more accurate frustration detection
- **Redis session storage** — persist sessions across restarts, support multi-instance deployments
- **Analytics dashboard** — track escalation rate, FAQ hit rate, average sentiment by topic
- **Live hosted demo** — deploy to Hugging Face Spaces

---

## Related Projects

- [AskDocs AI](https://github.com/Rajeshdevandla/askdocs-ai) — PDF RAG chatbot using Amazon Bedrock and FAISS
- [AgentFlow](https://github.com/Rajeshdevandla/agent-flow) — Multi-agent orchestration system with Constitutional AI safety layer
- [AI Document Intelligence Platform](https://github.com/Rajeshdevandla/ai-document-intelligence-platform) — Enterprise document processing with Java microservices + OCR

---

*Built by [Rajesh Kumar](https://rajeshdevandla.github.io) — Full Stack Java & AI Developer | Chicago, IL*
