from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from agents.retail_agent import RetailAgent

app = FastAPI(title="Retail AI Agent")

# Serve frontend if exists
try:
    app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
except:
    pass

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy agent (IMPORTANT)
agent = None

def get_agent():
    global agent
    if agent is None:
        print("Loading RetailAgent...")
        agent = RetailAgent()
    return agent


@app.get("/")
def home():
    return {"status": "Retail AI backend running"}


@app.get("/query")
def query(q: str):

    q_lower = q.lower().strip()
    words = q_lower.split()

    greetings = ["hi", "hello", "hey"]

    if any(g == w for g in greetings for w in words):
        return {
            "answer": (
                "Hi 👋 I’m your Retail AI Assistant.\n\n"
                "Try asking:\n"
                "• Dinner ideas\n"
                "• Popular snacks\n"
                "• Fruits under $5\n"
                "• Product recommendations\n\n"
                "How can I help you today?"
            )
        }

    if "thank" in q_lower:
        return {"answer": "You’re welcome 🙂"}

    try:
        agent = get_agent()
        result = agent.run(q)
    except Exception as e:
        print("AGENT ERROR:", e)
        return {"answer": "⚠️ Backend error."}

    if isinstance(result, str):
        return {"answer": result}

    if isinstance(result, dict) and "answer" in result:
        return {"answer": result["answer"]}

    if not isinstance(result, dict) or "recommendations" not in result:
        return {"answer": "No results."}

    items = result["recommendations"]

    answer = "Here’s what I found:\n\n"

    for i, r in enumerate(items[:5], 1):
        answer += (
            f"{i}. {r.get('product_name','')} "
            f"(Department: {r.get('department','')}, "
            f"Aisle: {r.get('aisle','')})\n"
        )

    return {"answer": answer}
