from datetime import datetime, timezone
from uuid import uuid4
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="OpenDots API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Starter in-memory store. Replace with SQLAlchemy/PostgreSQL repositories before production.
spaces = [{"id":"space-main","name":"General","description":"Shared workspace"}]
agents = [
    {"id":"research","name":"Research Dot","role":"Researcher","instructions":"Research carefully and cite sources.","tools":["web.read"],"status":"idle"},
    {"id":"sales","name":"Sales Dot","role":"Sales strategist","instructions":"Find prospects and draft thoughtful outreach.","tools":["pages.read","pages.draft"],"status":"idle"},
    {"id":"developer","name":"Coding Dot","role":"Developer","instructions":"Write, test and explain code.","tools":["files.read"],"status":"idle"},
]
pages = [{"id":"welcome","title":"Welcome to OpenDots","body":"# Your AI coworker workspace\n\nCreate a Dot, start a conversation, and save useful outcomes as pages.","parent_id":None,"space_id":"space-main","updated_at":datetime.now(timezone.utc).isoformat()}]
drafts = []
messages = []

class ChatInput(BaseModel):
    dot_id: str
    message: str = Field(min_length=1, max_length=12000)

class PageInput(BaseModel):
    title: str
    body: str = ""
    parent_id: str | None = None
    space_id: str = "space-main"

class ReviewInput(BaseModel):
    decision: str

@app.get("/health")
def health():
    return {"status":"ok","services":{
        "database":"demo-mode","redis":"configured" if os.getenv("REDIS_URL") else "missing",
        "ai":"configured" if os.getenv("OPENAI_API_KEY") or os.getenv("OLLAMA_BASE_URL") else "missing",
        "slack":"configured" if os.getenv("SLACK_BOT_TOKEN") else "missing",
        "voice":"configured" if os.getenv("LIVEKIT_URL") and os.getenv("LIVEKIT_API_KEY") else "missing",
        "browser":"configured" if os.getenv("BROWSER_WORKER_URL") else "missing"
    }}

@app.get("/spaces")
def get_spaces(): return spaces

@app.get("/agents")
def get_agents(): return agents

@app.post("/agents")
def create_agent(payload: dict):
    agent = {"id":str(uuid4()),"name":payload.get("name","New Dot"),"role":payload.get("role","Assistant"),
             "instructions":payload.get("instructions",""),"tools":payload.get("tools",[]),"status":"idle"}
    agents.append(agent)
    return agent

@app.get("/pages")
def get_pages(q: str = ""):
    return [p for p in pages if q.lower() in p["title"].lower() or q.lower() in p["body"].lower()]

@app.post("/pages")
def create_page(p: PageInput):
    if p.parent_id and not any(x["id"] == p.parent_id for x in pages):
        raise HTTPException(404, "Parent page not found")
    page = {"id":str(uuid4()), **p.model_dump(), "updated_at":datetime.now(timezone.utc).isoformat()}
    pages.append(page)
    return page

@app.post("/chat")
def chat(payload: ChatInput):
    if not any(a["id"] == payload.dot_id for a in agents):
        raise HTTPException(404, "Dot not found")
    user_msg = {"id":str(uuid4()),"dot_id":payload.dot_id,"role":"user","content":payload.message}
    # Deliberately transparent demo response: connect a model adapter here.
    reply = {"id":str(uuid4()),"dot_id":payload.dot_id,"role":"assistant",
             "content":"I’ve received your task. Connect an AI provider in Settings to enable live model responses. I can still help you organize this request as a page draft."}
    messages.extend([user_msg, reply])
    return {"messages":[user_msg,reply],"draft_available":True}

@app.post("/drafts")
def create_draft(payload: dict):
    draft = {"id":str(uuid4()),"title":payload.get("title","Untitled draft"),
             "body":payload.get("body",""),"status":"pending_review"}
    drafts.append(draft)
    return draft

@app.get("/drafts")
def get_drafts(): return drafts

@app.post("/drafts/{draft_id}/review")
def review_draft(draft_id: str, payload: ReviewInput):
    draft = next((d for d in drafts if d["id"] == draft_id), None)
    if not draft: raise HTTPException(404, "Draft not found")
    if payload.decision not in ("approve","reject"): raise HTTPException(400,"Use approve or reject")
    draft["status"] = "approved" if payload.decision == "approve" else "rejected"
    if payload.decision == "approve":
        pages.append({"id":str(uuid4()),"title":draft["title"],"body":draft["body"],"parent_id":None,
                      "space_id":"space-main","updated_at":datetime.now(timezone.utc).isoformat()})
    return draft
