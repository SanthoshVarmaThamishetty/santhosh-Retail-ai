import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss

from agents.llm import call_llm
from agents.web_search import web_search


class RetailAgent:
    def __init__(self):
        print("Loading retail data...")

        products = pd.read_csv("data/products.csv")
        aisles = pd.read_csv("data/aisles.csv")
        departments = pd.read_csv("data/departments.csv")
        order_products_prior = pd.read_csv("data/order_products__prior.csv")

        products_full = (
            products
            .merge(aisles, on="aisle_id")
            .merge(departments, on="department_id")
        )

        popularity = (
            order_products_prior
            .groupby("product_id")
            .size()
            .reset_index(name="order_count")
        )

        products_full = products_full.merge(popularity, on="product_id", how="left")
        products_full["order_count"] = products_full["order_count"].fillna(0)

        self.df = products_full

        self.df["embed_text"] = (
            self.df["product_name"].astype(str) +
            " | aisle: " + self.df["aisle"].astype(str) +
            " | department: " + self.df["department"].astype(str)
        )

        print("Loading embedding model...")

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        embeddings = self.model.encode(
            self.df["embed_text"].tolist(),
            show_progress_bar=True
        )

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

        print("RetailAgent ready.")

    def run(self, query, k=5):

        print("User query:", query)

        # ======================
        # VECTOR SEARCH
        # ======================
        q = self.model.encode([query])
        D, I = self.index.search(q, k)

        results = self.df.iloc[I[0]][
            ["product_name", "aisle", "department", "order_count"]
        ].sort_values("order_count", ascending=False)

        records = results.to_dict(orient="records")

        print("Found records:", len(records))

        # =========================
        # NO DATA → WEB SEARCH
        # =========================
        if len(records) == 0:
            print("Using WEB SEARCH")

            web = web_search(query)

            prompt = f"""
Answer conversationally.

Question:
{query}

Internet info:
{web}
"""

            answer = call_llm(prompt)

            return {"answer": answer}

        # =========================
        # RETAIL DATA FOUND
        # =========================
        print("Using RETAIL DATA")

        retail_text = ""
        for r in records:
            retail_text += f"• {r['product_name']} (aisle: {r['aisle']})\n"

        prompt = f"""
You are a friendly grocery assistant.

User asked:
{query}

Available products:

{retail_text}

Respond naturally like ChatGPT and suggest meals.
"""

        answer = call_llm(prompt)

        # =========================
        # SAFETY FALLBACK
        # =========================
        if not answer or isinstance(answer, dict):
            return {
                "answer": "Here are matching products:\n\n" + retail_text
            }

        return {"answer": answer}
