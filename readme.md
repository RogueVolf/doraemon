````markdown
# 🛍️ Doraemon — Your AI Product Companion

Doraemon is not just a chatbot — it's a **shopping assistant** that actually understands what you're looking for and curates the best products tailored to your needs.

[🔗 GitHub Repo](https://github.com/RogueVolf/doraemon)

---

## 🧩 Problem Statement

Even with all the AI tools and chatbots out there, finding the *right product* is still frustrating.

Most bots can search — but:
- They don't help you **formulate your requirement** clearly.
- They don’t **filter intelligently** based on reviews or images.
- They don’t show **region-specific** product links.

> Say you want a new shower hanger for your bathroom.  
> You want someone who can:
> - Understand what kind of hanger you need  
> - Clarify use cases, preferences, and budget  
> - Search relevant platforms (Amazon, Flipkart)  
> - Filter the top 5 most suitable products  
> - Ensure results are region-specific  

None of today’s tools can do all of that in one flow. Doraemon does.

---

## 💡 Thought Process

Finding a good product is fundamentally a **data curation task**.  

To solve this, we need a multi-step process:
1. **Gather** precise user requirements  
2. **Search** across platforms for matching products  
3. **Filter** by understanding **images**, **reviews**, and **relevance**  
4. **Assist** with follow-up questions and feedback  

Rather than relying on users to craft perfect queries (like with Perplexity or Google's AI search), Doraemon guides users through conversation and curates results intelligently.

---

## 🛠️ Key Features

### 🧾 1. Request Gatherer  
An agent that chats with the user to:
- Understand their actual need
- Extract use-case, context, and preferences
- Generate a structured memo for search agents

### 🔍 2. Product Finder  
An agent that:
- Uses Amazon & Flipkart scrapers  
- Collects ~15 candidate products (5 per page, across 3 pages)  
- Gathers metadata, images, prices, links

### 🧠 3. Product Filterer  
An agent that:
- Emulates a human evaluating products  
- Reads through product **reviews**, **ratings**, and **images**  
- Filters out irrelevant or low-quality items  
- Returns the top 3–5 options tailored to user needs

### 💬 4. Doubt Solver  
Once products are shown:
- User can ask follow-up questions (e.g., comparisons, doubts)  
- Agent handles responses intelligently  
- If unsatisfied, the Doubt Solver updates user requirements and **restarts search** seamlessly

---

## 🌍 Region-Specific Results

Unlike global search engines, Doraemon respects your geography:
- Only shows **region-relevant product pages**
- Prioritizes availability and pricing for your market

---

## 📌 Why This Matters

With AI search everywhere, it still feels like we’re stuck doing all the work —  
crafting queries, comparing specs, reading reviews.

**Doraemon flips the model.**  
You tell it what you need — it does the rest.

---

## 🧪 Status

- ✔️ MVP built with FastAPI, NiceGUI, and Autogen
- 🔧 Modular agent structure — easily extendable
- 🚧 Currently desktop-focused (mobile view in progress)

---

## 🧰 How to Use

1. Clone the repository:  
   ```bash
   git clone https://github.com/RogueVolf/doraemon
   cd doraemon
````

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up your `.env` file:

   * If using **Cerebras**, add your key like:

     ```env
     CEREBRAS_API_KEY=your_cerebras_key_here
     ```
   * Otherwise, modify `llm_utils.py` to plug in any other LLM provider (OpenAI, Together, Groq, etc.).

5. Open two terminals:

   * In the first one, run the frontend:

     ```bash
     python frontend.py
     ```
   * In the second one, run the backend:

     ```bash
     python backend.py
     ```

6. Open your browser and start shopping smarter with Doraemon.

---

## 🤝 Contributions & Feedback

* Feedback welcome!
* Ideas for agents, improvements, new marketplaces, UI updates — open to all!

---

Built with ❤️ by [@RogueVolf](https://github.com/RogueVolf)

```
```
