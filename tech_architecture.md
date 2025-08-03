# Tech Architecture: Doraemon 🛒🤖

## Overview

**Doraemon** is a multi-agent product discovery chatbot built using LLMs and real-time search data from Amazon, Flipkart, and Google Shopping. It guides users from vague requirements to a confident buying decision, while also handling follow-up queries.

The system transitions through four key agent states:

- 🟢 **Request Gatherer**
- 🔍 **Product Finder**
- 🧠 **Product Filterer**
- ❓ **Doubt Solver**

---

## 🧩 Agent State Switch Logic

### Phase 1: Request Gathering (`State = Request Gatherer`)
1. **User Input:** Begins with a vague product query (e.g., "I want a bathroom hanger").
2. **Clarification Dialogues:** Request Gatherer asks Yes/No questions to narrow down the requirement.
3. **Budget Inquiry:** Asks for a price range.
4. **Final Filters:** Any specific features, style, or considerations?
5. **Memo Creation:** A structured summary of the user's needs is generated.
6. **State Transition:** Switches to `Product Finder`.

---

### Phase 2: Product Search (`State = Product Finder`)
- **Search String Generation:** LLM generates search-friendly strings based on the memo.
- **Web Search Tools Triggered:**
  - **Amazon**  
    - URL: `https://www.amazon.in/s?k={search_string}`  
    - Scrape:
      - Product Link: `class="a-link-normal s-line-clamp-4 s-link-style a-text-normal"` → prefix with `amazon.in/`
      - Title: `id="productTitle"`
      - Price: `class="a-price-whole"`
      - Specs: `class="prodDetSectionEntry"` and `class="prodDetAttrValue"`
      - Summary Review: `id="product-summary"`

  - **Flipkart**  
    - URL: `https://www.flipkart.com/search?q={search_string}`
    - Scrape:
      - Product Link: `class="CGtC98"` or repeated `href`, prefix with `flipkart.com/`
      - Title: Class containing `VU-ZEz`
      - Price: Class containing `Nx9bqj`
      - Review: Class `_8-rIO3`
      - Specs: Class `_3Fm-hO` (may be missing sometimes)

- **Output:** Top 7 results from each platform = 14 total.
- **State Transition:** Switches to `Product Filterer`.

---

### Phase 3: Product Relevance Filtering (`State = Product Filterer`)
- **Input:** User memo + 14 product details.
- **LLM Relevance Scoring:**
  - Each product is rated on a scale of **1–5** for relevance.
- **Ranking:** Top 5 products are selected.
- **Recommendation:**
  - For each product:
    - ✅ Pros
    - ❌ Cons
  - Final recommended product with a **clear rationale**.
- **State Transition:** Switches to `Doubt Solver`.

---

### Phase 4: Query Resolution (`State = Doubt Solver`)
- **Context:** Uses results from `Product Finder` and `Product Filterer`.
- **Capabilities:**
  - Compare products on demand.
  - Get full details of any product.
  - Search for user-specific reviews via Google (demographic-aware).
  - Modify original requirements and restart the cycle via `Request Gatherer`.
- **End Condition:** Either switch back to Request Gatherer or end the conversation.

---

## 🏗️ System Design

| Component        | Description                                                                                   |
|------------------|-----------------------------------------------------------------------------------------------|
| 🧠 LLM            | Used for memo summarization, query generation, filtering, and product scoring.               |
| 🔄 Autogen Agents | Used in `Request Gatherer` and `Doubt Solver` for human-in-the-loop interactions.            |
| 🧰 Tools          | Scraping scripts built using **Selenium** with HTML heuristics for Amazon and Flipkart.      |
| 🎯 Filtering      | LLM-based relevance scoring + rule-based ranking system.                                      |
| 🌐 Frontend       | Built using **NiceGUI** for a smooth, modern interface.                                       |
| ⚙️ Backend        | Managed via **FastAPI**, serving websocket endpoints and LLM logic endpoints.                 |

---

## 🧪 Additional Notes

- **Error Handling:** Includes fallback flows if products are not found or scraping fails.
- **Scalability:** Future extension includes Google Shopping and possibly price history tracking.
- **Agent Framework:** Autogen is chosen for clarity in state transitions and human-in-the-loop UX.

---

## 🔗 Project Repository

**GitHub:** [github.com/RogueVolf/doraemon](https://github.com/RogueVolf/doraemon)

---

## 💡 Summary

Doraemon demonstrates an end-to-end intelligent product discovery experience with multi-agent orchestration, autonomous tools, and LLM-guided reasoning. It is the **second project** in a series of **9 open-source AI showcases** and was built to push past procrastination and explore real-world applications of agentic AI systems.

---
