# Whatnot Seller Copilot

A demo I built after reading Whatnot's engineering blog. Three tools, three documented problems.

**Live demo:** https://dazzling-axolotl-25ce9f.netlify.app

---

## Why I built this

Going through Whatnot's engineering blog, I found three specific problems the team called out publicly:

**1. Back-office workflow complexity**
> "Our buyer and seller communities tell us what's hard, whether it's discovering the right shows, managing complex back-office workflows, or scaling a seller business."
> Source: [Whatnot Engineering 2025 Highlights](https://medium.com/whatnot-engineering/whatnot-engineerings-2025-blog-highlights-e7a63dbd0057)

**2. 5 million listings created daily with no AI assistance**
> "Every day, sellers on Whatnot create more than 5 million product listings to share what they love with the world."
> Source: [Whatnot Engineering 2025 Highlights](https://medium.com/whatnot-engineering/whatnot-engineerings-2025-blog-highlights-e7a63dbd0057)

**3. Scam patterns outpacing rule engines**
> "Fighting fraud and other attacks is an ongoing battle and new tactics are often used to circumvent our checks... messaging is usually tweaked very often."
> Source: [How Whatnot Utilizes GenAI for Trust & Safety](https://medium.com/whatnot-engineering/how-whatnot-utilizes-generative-ai-to-enhance-trust-and-safety-c7968eb6315e)

---

## What it does

**Tab 1: AI Listing Generator**
Seller describes an item, picks category and condition, gets back an optimized listing: title, price range, description, search tags, best time to list, and a quality score. No AI assistance currently exists inside Whatnot for listing quality at the 5M/day scale.

**Tab 2: Scam Conversation Analyzer**
Seller pastes a suspicious DM and gets a scam likelihood score, every red flag with severity, a plain-English assessment, and a suggested safe reply. Mirrors Whatnot's own T&S LLM pipeline but surfaces it directly to sellers as a first line of defense.

**Tab 3: Back Office Automation**
Four AI workflows: smart repricing with market comp analysis, shipping carrier optimization, buyer message templates, and inventory audit with bundle and discount strategy recommendations.

---

## Stack

```
frontend/
    index.html          Vanilla JS, single file, calls backend API

backend/
    main.py             FastAPI, three endpoints: /api/listing /api/scam /api/workflow
    requirements.txt
    .env.example
```

The live demo runs frontend-only via Netlify. The backend is structured for production deployment on Render or Railway with the API key server-side.

---

## Running locally

**Backend**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env        # add your ANTHROPIC_API_KEY
uvicorn main:app --reload
```

API runs at `http://localhost:8000`. Docs at `http://localhost:8000/docs`.

**Frontend**
Open `frontend/index.html` in a browser. Point the API calls to `http://localhost:8000` or use your own API key directly for local testing.

---

Built by Jafar
