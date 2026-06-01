# SupportGPT 🤖

An AI-powered customer support assistant that handles common support questions automatically, detects frustrated customers, and escalates to human agents when needed.

---

## What this does

Customers start a chat session and ask questions. The assistant first checks a FAQ knowledge base for instant answers. For other questions, it runs a sentiment check — if the customer seems very frustrated, it escalates to a human agent instead of trying to answer with AI. For everything else, it uses Amazon Bedrock (Claude) to generate a helpful response.

At the end of a conversation, the assistant can generate a summary for ticket logging.

## How it works

```
Customer message
      │
      ▼
  FAQ check ──── match? ────▶ Return FAQ answer
      │
   no match
      │
      ▼
Sentiment analysis
      │
  score < 0.3? ──── yes ────▶ Escalate to human agent
      │
      no
      │
      ▼
Amazon Bedrock (Claude)
      │
      ▼
   Response + metadata
```

## Tech stack

| Component | Technology |
|-----------|-----------|
| LLM | Amazon Bedrock (Claude 3 Haiku) |
| API | FastAPI |
| Frontend | Streamlit |
| Session storage | In-memory (Redis recommended for production) |
| Containerization | Docker |

## Project structure

```
support-gpt/
├── config.py           # env var config
├── core/
│   └── chatbot.py      # FAQ matching, sentiment analysis, Bedrock integration
├── api/
│   └── main.py         # FastAPI routes
├── requirements.txt
├── .env.example
└── Dockerfile
```

## Getting started

```bash
git clone https://github.com/Rajeshdevandla/support-gpt.git
cd support-gpt
cp .env.example .env
# fill in your AWS credentials
pip install -r requirements.txt
uvicorn api.main:app --reload
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| POST | /session/start | Start a new support session |
| POST | /chat | Send a message, get a response |
| GET | /session/{id}/summary | Get conversation summary for ticket |

**Example flow:**
```bash
# Start session
curl -X POST http://localhost:8000/session/start

# Send message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "YOUR_SESSION_ID", "message": "How do I return an item?"}'
```

## Response metadata

Each chat response includes:
- `handled_by`: "faq" | "llm" | "escalation"
- `escalate`: true if the customer was routed to a human
- `sentiment_score`: 0.0 (very negative) to 1.0 (very positive)

## Environment variables

| Variable | Description | Default |
|----------|-------------|---------|
| AWS_REGION | AWS region | us-east-1 |
| AWS_ACCESS_KEY_ID | AWS access key | required |
| AWS_SECRET_ACCESS_KEY | AWS secret key | required |
| BEDROCK_MODEL_ID | Model to use | claude-3-haiku |
| SENTIMENT_THRESHOLD | Escalate below this score | 0.3 |

## Notes

- FAQ matching uses simple keyword search — a production system would use semantic similarity
- Sentiment analysis uses keyword counting — a production system would use AWS Comprehend
- Session data is in-memory and lost on server restart

---

Built as part of a GenAI portfolio for cloud/AI engineering roles.
