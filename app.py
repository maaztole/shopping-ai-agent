
import os
import json
import requests
import pandas as pd
import streamlit as st

from dotenv import load_dotenv
from google import genai
from google.genai import types

# -------------------------------
# 1. Page configuration
# -------------------------------

st.set_page_config(
    page_title="AI Shopping Assistant",
    page_icon="🛍️",
    layout="wide"
)

load_dotenv()


# -------------------------------
# 2. Read API keys safely
# -------------------------------

def get_api_key(key_name):

    # Check Streamlit Cloud Secrets first
    try:
        value = st.secrets.get(key_name)
        if value:
            return str(value)
    except Exception:
        pass

    # Check local .env file
    return os.getenv(key_name)


# -------------------------------
# 3. Gemini AI integration
# -------------------------------

def understand_query(user_query):

    api_key = get_api_key("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "Gemini API key is missing. "
            "Add GEMINI_API_KEY to Streamlit Secrets."
        )

    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are an AI shopping assistant.

    Extract shopping product information from this query.

    Return valid JSON containing exactly these fields:
    - product_name
    - specifications
    - search_query

    Rules:
    - Do not invent missing specifications.
    - Use an empty string or empty object
      when information is unavailable.
    - Make search_query suitable for Google Shopping.
    - Return JSON only.

    User query: {user_query}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    return json.loads(response.text)


# -------------------------------
# 4. SerpAPI shopping search
# -------------------------------

def search_products(search_query):

    api_key = get_api_key("SERPAPI_API_KEY")

    if not api_key:
        raise ValueError(
            "SerpAPI key is missing. "
            "Add SERPAPI_API_KEY to Streamlit Secrets."
        )

    url = "https://serpapi.com/search.json"

    params = {
        "engine": "google_shopping",
        "q": search_query,
        "api_key": api_key,
        "gl": "in",
        "hl": "en"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if "error" in data:
        raise ValueError(data["error"])

    return data.get("shopping_results", [])


# -------------------------------
# 5. Compare product prices
# -------------------------------

def compare_prices(products):

    rows = []

    for product in products:

        price = product.get("extracted_price")

        if price is None:
            continue

        try:
            price = float(price)
        except (ValueError, TypeError):
            continue

        rows.append({
            "Product": product.get("title", "Unknown"),
            "Price": price,
            "Seller": product.get("source", "Unknown"),
            "Link": product.get("link", "")
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values(
            by="Price",
            ascending=True
        )

    return df


# -------------------------------
# 6. Streamlit interface
# -------------------------------

st.title("🛍️ AI Shopping Price Comparison Agent")

st.write(
    "Search for a product and compare "
    "available shopping prices."
)

user_query = st.text_input(
    "Enter product name",
    placeholder="Example: iPhone 17 Pro 256GB"
)

if st.button("Compare Prices"):

    if not user_query.strip():

        st.warning("Please enter a product name.")

    else:

        try:

            with st.spinner("Gemini is understanding your search..."):

                details = understand_query(user_query)

            st.subheader("AI understood your request")
            st.json(details)

            search_query = details.get(
                "search_query"
            ) or user_query

            with st.spinner("Searching shopping listings..."):

                products = search_products(search_query)

            if not products:

                st.warning("No shopping results found.")

            else:

                df = compare_prices(products)

                if df.empty:

                    st.warning(
                        "No usable numeric prices found."
                    )

                else:

                    st.subheader("Price Comparison")

                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True
                    )

                    cheapest = df.iloc[0]

                    st.success(
                        f"Lowest listed price: "
                        f"₹{cheapest['Price']:,.2f}"
                    )

                    if cheapest["Link"]:

                        st.markdown(
                            f"[View product on "
                            f"{cheapest['Seller']}]"
                            f"({cheapest['Link']})"
                        )

                    st.caption(
                        "Prices are retrieved search listings. "
                        "Verify the final price, availability, "
                        "shipping and seller details at checkout."
                    )

        except Exception as error:

            st.error(f"Something went wrong: {error}")
