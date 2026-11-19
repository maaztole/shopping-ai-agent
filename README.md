 AI-Powered Shopping Price Comparison Agent

AI-based shopping assistant that helps users find and compare prices of the desired product in online shopping stores. With the help of Google Gemini AI, the program will comprehend user requests, look up shopping listings, compare product prices, and help users find the best price offer.

📌 Project Summary

Online shoppers often spend a great amount of time going to several e-commerce webpages to compare prices of the identical product.

The AI-Powered Shopping Price Comparison Agent streamlines this process by helping users input a product name and get all relevant information including comparison of prices of the identical product.

The application employs Google Gemini AI to understand user requirements and SerpAPI to retrieve the shopping search results. Then it processes the gathered product information and shows the price comparison to help users make their purchase decisions.

✨ Features

AI-Based Product Search Understanding: The application utilizes Google Gemini AI to comprehend natural-language product searches.

Automated Shopping Search: Available product listings retrieval using SerpAPI.

Product Information Collection: Extraction of product names, prices, sellers, and product links.

Price Comparison: Product listing organization and sorting according to prices.

Best Offer Detection: Highlighting the lowest-priced product from the obtained offers.


🛠️ Technology Stack

Python - Backend development

Streamlit - Web application interface

Google Gemini API - AI-powered query understanding

SerpAPI - Google Shopping search results

Pandas - Product data processing and price comparison

System Architecture

The application follows this workflow:

          USER
            |
            v
    Product Search Query
            |
            v
    Google Gemini AI
     (Query Understanding)
            |
            v
       SerpAPI
    (Shopping Search Results)
            |
            v
    Product Data Extraction
            |
            v
    Price Comparison
            |
            v
    Best Deal Identification
            |
            v
      Streamlit UI
            |
            v
       USER RESULTS


⚙️ How It Works

User Input: The user enters a product name or describes the product they want to purchase.

AI Query Understanding: Google Gemini processes the query and identifies relevant product information and specifications.

Shopping Search: SerpAPI retrieves available product listings from Google Shopping.

Data Extraction: The application collects product titles, prices, merchant names, and product links.

Price Comparison: Python and Pandas process the collected information and sort products by price.

Best Deal Recommendation: The application highlights the lowest listed price.

Results Display: Streamlit displays the comparison results and product links.

