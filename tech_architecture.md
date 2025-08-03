Switch: 4 States -> Request Gatherer, Product Finder, Product Filterer, Doubt Solver

Working Scenario

Phase 1:
User enters a vague product query -> I want a bathroom hanger
Switch state = Request Gatherer 
Request Gatherer asks additional clarification, all yes/no questions
User replies all
Request Gatherer asks about budget
User replies with budget
Request Gathere asks about any specific thing to keep in mind
User replies with something
Request Gatherer creates memo of user requirements
Request Gatherer changes switch to Product Finder

Phase 2:
Memo arrives to Product Finder
(Product Finder does not need to be an agent can be a simple LLM call)
Triggers three tools with custom search queries based on the memo provided by the user
Search Websites: Amazon, Flipkart, Google Shopping
Search Methodology:
Amazon:
URL: https://www.amazon.in/s?k={search_string}

Search String Format: bag+with+blue+bottle

Extract from html:
Product Detail page Href: class = a-link-normal s-line-clamp-4 s-link-style a-text-normal and add amazon.in/ infront of href
Title: id =  productTitle
Price: span class = a-price-whole
Product Details: class = th class = a-color-secondary a-size-base prodDetSectionEntry and td class = a-size-base prodDetAttrValue
Product Summarised Review: id = product-summary

Flipkart:
URL: https://www.flipkart.com/search?q={search_string}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off

Search String Format: mobile%20phones

Extract From HTML
Product Detail Page Href: class = CGtC98 href value or href value that repeats more than once and flipkart.com/ infront of href to open 
Product Title: VU-ZEz in the class name
Product Price: Nx9bqj in the class name
Product Review: _8-rIO3 in the class name
Product Specs: _3Fm-hO in the class name may or may not be there


Extract all product details using HTML Heuristics
Result is filtered and top 7 is selected from each website

Product Finder changes switch to Product Filterer

Phase 3:
Use the data generated from previous step and the memo to filter out and select top 5 products to show to the user. Total pool is 14.
For each product generate detailed pros and cons, as well as recommend one out of the 5 and provide a clear reason for your recommendation

Product Filterer changes switch to Doubt Finder

Phase 4:
With data from Product Finder and recommendation results from Product Filterer, Double Solver will solve any query that the user has in terms of comparison of products, detailed info of a product etc. If the user wants to modify the search, correct the user memo and switch to Request Gatherer else close the chat


Tech Architecture:
- Request Gatherer will be a single agent that will take user input, and decide if enough information is recieved or not.
Can do this with an LLM call and maintain session ID, or do it using Autogen with Human in the loop.
I am gonna go for Autogen it will be a good demonstration of how Human in the loop works

- Product Finder will be a static call to an llm to generate search strings for amazon and flipkart based on the user memo. Then we will use selenium to make the searches, gather the top 7 product page links, open each page, gather the product details.

- Product Filterer will also be llm calls with one call for each product. The user memo, and the product details will go and the llm has to reply with a relevance score on a scale of 1 - 5, 5 being most relevant. Then the top 5 will be selected using a simple max sort and pick

- Doubt Solver will also be an agentic human in the loop conversation. We will give tools to the doubt solver to query exact details of a particular product, know all the 14 product names in the product pool, and to do a google search for reviews of a particular product in a given demographic

- We will control demographic using an environment variable

- We will use NiceGUI for frontend and FastAPI to be the backend