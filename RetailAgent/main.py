from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from agents.retail_agent import RetailAgent


app = FastAPI(title="Retail AI Agent")

# Serve frontend
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# CORS (dev safe)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load agent once
agent = RetailAgent()


@app.get("/")
def home():
    return FileResponse("frontend/index.html")


@app.get("/query")
def query(q: str):

    q_lower = q.lower().strip()
    words = q_lower.split()

    print("\nUSER QUERY:", q)

    # ------------------
    # Small Talk (SAFE)
    # ------------------

    greetings = ["hi", "hello", "hey"]

    # Only match FULL WORD greetings
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
        return {
            "answer": "You’re welcome 🙂 Let me know if you need anything else!"
        }

    # ------------------
    # Agent Layer
    # ------------------

    try:
        result = agent.run(q)
    except Exception as e:
        print("AGENT ERROR:", e)
        return {
            "answer": "⚠️ Something went wrong while processing your request."
        }

    # DEBUG
    print("RESULT TYPE:", type(result))
    print("RESULT VALUE:", result)

    # ------------------
    # Direct LLM String
    # ------------------

    if isinstance(result, str):
        return {
            "answer": result
        }

    # ------------------
    # Dict Answer
    # ------------------

    if isinstance(result, dict) and "answer" in result:
        return {
            "answer": result["answer"]
        }

    # ------------------
    # CSV Product Results
    # ------------------

    if not isinstance(result, dict) or "recommendations" not in result:
        return {
            "answer": "Sorry - I couldn’t find anything related. Try asking differently."
        }

    items = result["recommendations"]

    if not items:
        return {
            "answer": "I couldn’t find matching products. Try another query!"
        }

    answer = "Here’s what I found for you:\n\n"

    for i, r in enumerate(items[:5], 1):
        answer += (
            f"{i}. {r.get('product_name','')} "
            f"(Department: {r.get('department','')}, "
            f"Aisle: {r.get('aisle','')})\n"
        )

    answer += "\nThese results are ranked using semantic similarity and historical popularity."

    return {
        "answer": answer
    }
