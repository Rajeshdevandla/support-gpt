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

**Portfolio:** [rajeshdevandla.github.io](https://rajeshdevandla.github.io)

View the full project overview, architecture, and demo walkthrough on the portfolio site.

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
