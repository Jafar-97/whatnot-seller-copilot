"""
Whatnot Seller Copilot - Backend API
=====================================
FastAPI backend that powers three seller tools:
  1. AI Listing Generator   - optimizes product listings for discoverability
  2. Scam Analyzer          - detects off-platform fraud and social engineering
  3. Back Office Workflows  - automates repricing, shipping, messaging, inventory

Architecture note:
  The frontend (index.html) calls this backend rather than hitting the LLM API
  directly. This keeps API keys server-side, enables rate limiting per seller,
  and makes it easy to log outcomes for future fine-tuning on Whatnot-specific data.
"""

import os
import json
import anthropic
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Whatnot Seller Copilot API",
    description="AI-powered seller tooling built around documented Whatnot engineering challenges",
    version="1.0.0"
)

# Allow frontend to call this backend locally and from Netlify
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Anthropic client
# In production: load from environment variable, never hardcode
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-20250514"


# ─── Request models ───────────────────────────────────────────────────────────

class ListingRequest(BaseModel):
    description: str
    category: str
    condition: str

class ScamRequest(BaseModel):
    conversation: str
    account_age: str

class WorkflowRequest(BaseModel):
    workflow_type: str  # "pricing" | "shipping" | "buyer" | "inventory"
    seller_context: Optional[dict] = None


# ─── Response helpers ─────────────────────────────────────────────────────────

def call_claude(prompt: str, max_tokens: int = 1000) -> dict:
    """
    Wrapper around Anthropic Messages API.
    Returns parsed JSON from Claude's response.
    Raises HTTPException on API or parse errors.
    """
    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = message.content[0].text.strip()
        # Strip markdown code fences if present
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {str(e)}")
    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=f"AI API error: {str(e)}")


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    """Simple health check."""
    return {"status": "ok", "model": MODEL}


@app.post("/api/listing")
def generate_listing(req: ListingRequest):
    """
    Generate an optimized Whatnot product listing.

    Addresses: 5M daily listings created with no AI assistance layer.
    Source: https://medium.com/whatnot-engineering/whatnot-engineerings-2025-blog-highlights-e7a63dbd0057

    Returns title, price range, description, tags, timing, and quality score.
    """
    prompt = f"""You are an expert Whatnot marketplace listing specialist with deep knowledge
of what drives discoverability and conversion on the platform.

Create a high-converting product listing for:
  Item: {req.description}
  Category: {req.category}
  Condition: {req.condition}

Return ONLY valid JSON with this exact structure:
{{
  "title": "optimized listing title under 80 chars, specific and searchable",
  "price_low": 0,
  "price_high": 0,
  "description": "2-3 sentence compelling description that sells the item",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "condition_note": "brief honest condition disclosure",
  "best_time": "best time to list on Whatnot for max visibility",
  "category_tip": "one platform-specific tip for this category",
  "quality_score": 0
}}

price_low and price_high are realistic USD market prices as numbers.
quality_score is 0-100 based on listing completeness and market fit."""

    result = call_claude(prompt)
    return result


@app.post("/api/scam")
def analyze_scam(req: ScamRequest):
    """
    Analyze a seller DM conversation for scam patterns.

    Addresses: scam messaging patterns that evolve faster than rule engines can track.
    Source: https://medium.com/whatnot-engineering/how-whatnot-utilizes-generative-ai-to-enhance-trust-and-safety-c7968eb6315e

    Mirrors Whatnot's internal T&S LLM architecture (zero-shot classification +
    rule engine handoff) but surfaces results directly to sellers.

    Returns scam likelihood, flagged patterns, recommended action, and safe reply draft.
    """
    prompt = f"""You are Whatnot's trust and safety AI. Analyze this seller conversation
for scam patterns, policy violations, and social engineering attempts.

Account age: {req.account_age}
Conversation:
{req.conversation}

Known high-risk patterns to detect:
- Off-platform transaction requests (Venmo, Zelle, PayPal F&F, Cash App)
- Financial incentives to bypass platform ("I'll pay more direct")
- Urgency and pressure tactics
- Fake giveaway or prize claims
- Personal information harvesting
- Normalization phrases ("everyone does this", "I do this all the time")

Return ONLY valid JSON:
{{
  "scam_likelihood": 0.0,
  "risk_level": "low|medium|high",
  "flags": [
    {{
      "type": "flag type",
      "description": "specific evidence from the conversation",
      "severity": "low|medium|high"
    }}
  ],
  "patterns_detected": ["pattern1", "pattern2"],
  "recommended_action": "clear action the seller should take",
  "explanation": "2-3 sentence plain English summary",
  "safe_response": "suggested reply if suspicious"
}}

scam_likelihood is 0.0 to 1.0. Be specific and cite actual message content."""

    result = call_claude(prompt)
    return result


@app.post("/api/workflow")
def run_workflow(req: WorkflowRequest):
    """
    Run an AI back-office workflow for a seller.

    Addresses: complex back-office workflows sellers struggle to manage at scale.
    Source: https://medium.com/whatnot-engineering/whatnot-engineerings-2025-blog-highlights-e7a63dbd0057

    Supported workflows:
      pricing   - market comp analysis and reprice recommendations
      shipping  - carrier selection and packing instructions
      buyer     - professional message templates for common situations
      inventory - slow mover identification and clearance strategies
    """
    prompts = {
        "pricing": """You are a Whatnot marketplace pricing analyst.
Seller profile: 47 active listings, $2,400 GMV this week, 98% seller rating, categories include trading cards, sneakers, collectibles.

Generate a repricing strategy. Return ONLY valid JSON:
{
  "strategy": "strategy name",
  "summary": "2-3 sentence overview",
  "actions": [
    {"item_type": "type", "current_avg": "$X", "suggested_avg": "$X", "reason": "why"}
  ],
  "expected_impact": "expected GMV change as a result",
  "tip": "one advanced pricing tip for this seller profile"
}""",

        "shipping": """You are a Whatnot fulfillment specialist.
Seller has 3 pending shipments: a PSA graded card, a pair of sneakers, and a vintage jacket.

Generate shipping instructions. Return ONLY valid JSON:
{
  "summary": "brief overview",
  "shipments": [
    {
      "item": "item name",
      "carrier": "recommended carrier",
      "box_size": "recommended box size",
      "packing_tip": "specific packing instruction",
      "estimated_cost": "$X",
      "delivery_days": 3
    }
  ],
  "time_saved": "estimated time saved vs manual lookup",
  "pro_tip": "one fulfillment tip that protects seller rating"
}""",

        "buyer": """You are a Whatnot seller communications specialist.
Draft 3 response templates for common buyer situations that build trust and repeat business.

Return ONLY valid JSON:
{
  "templates": [
    {
      "situation": "situation description",
      "tone": "tone descriptor",
      "message": "full draft message"
    }
  ],
  "tip": "one communication tip that drives repeat buyers on Whatnot"
}""",

        "inventory": """You are a Whatnot inventory optimization specialist.
Seller has 47 listings, $2,400 weekly GMV, 98% rating. Some items have been listed 30+ days without selling.

Return ONLY valid JSON:
{
  "summary": "brief assessment",
  "slow_movers": [
    {
      "item_type": "type",
      "days_listed": 35,
      "strategy": "bundle|discount|relist|auction",
      "reason": "why this strategy works here"
    }
  ],
  "bundle_ideas": ["bundle idea 1", "bundle idea 2"],
  "auction_tip": "when to use auction vs fixed price on Whatnot",
  "expected_clearance": "% of slow inventory cleared in 2 weeks"
}"""
    }

    if req.workflow_type not in prompts:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown workflow type: {req.workflow_type}. Must be one of: pricing, shipping, buyer, inventory"
        )

    result = call_claude(prompts[req.workflow_type])
    return result
