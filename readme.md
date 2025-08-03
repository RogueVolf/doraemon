Problem Statement:
I want to find a product but even with all the chatbots out there I can't find any reliable way that would do the searching, sorting and sifting part for me.
All the chatbots can search but I need help with forming my search also. For example, I might need a new shower hangar for my bathroom. I need someone that can sit and understand what kind of shower hangar do I want, what am I gonna use it for, what's my budget and then start searching and give me the top 3 or top 5 most suitable choices for me. Also with this is the focus on region, dont give me a product page link that is not my region specific page.

Thinking:
I am thinking the task is a situation of gathering and curating data for the user. So I need to be able to gather data first, then filter it by considering the product images and reviews. But before that I need to gather information from the user on what they want exactly. So for that I will let the agent decide what is the exact details it will need from the user.

Difference:
Doing a search on Perplexity or Google's AI mode means I have to craft the search string myself, I want the user to be able to chat with the product finder and guide its product finding, ask queries within the chat interface itself
Second, these search engine chatbots don't look at review etc to do a second layer of filteration I will do that by understanding what exactly does the user require

Key Features:
- Request Gatherer: An agent designed to gather information from the user and create a detailed memo of what is it that the user wants
- Product Finder: An agent that will search Amazon and Flipkart pages to find the top 15 products across all pages (5 from each)
- Product Filterer: An agent that will emulate a human going through the images and reviews of each product to decide if its useful or not
- Doubt Solver: Once the top 5 products have come the user can either ask doubts about them like comparison or something, if the user is not satisfied the doubt solver will automatically retrigger the request product finder with updated notes from the user
