
import os
import json
import requests
import pandas as pd
import streamlit as st

from dotenv import load_dotenv
from google import genai
from google.genai import types


# =====================================
# 1. PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="AI Shopping Assistant",
    page_icon="🛍️",
    layout="wide"
)

load_dotenv()


# =====================================
# 2. API KEY MANAGEMENT
# =====================================

def get_api_key(key_name):

    # Streamlit Cloud Secrets
    try:
        value = st.secrets.get(key_name)

        if value:
            return str(value)

    except Exception:
        pass

    # Local environment variables
    return os.getenv(key_name)


# =====================================
# 3. GEMINI AI INTEGRATION
# =====================================

def understand_query(user_query):

    api_key = get_api_key("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "Gemini API key is missing. "
            "Please configure GEMINI_API_KEY in Streamlit Secrets."
        )

    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are an intelligent AI shopping assistant.

    Analyze the user's shopping query.

    Extract the following information:

    1. product_name
    2. specifications
    3. search_query

    Return valid JSON with exactly these fields.

    Rules:
    - Do not invent missing specifications.
    - Use an empty object if specifications are unavailable.
    - Use a clear product name.
    - Create an optimized Google Shopping search query.
    - Preserve important details like RAM, storage,
      model number, size and color.
    - Return JSON only.

    User query:
    {user_query}
    """

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    if not response.text:
        raise ValueError(
            "Gemini returned an empty response."
        )

    try:
        result = json.loads(response.text)

    except json.JSONDecodeError:
        raise ValueError(
            "Gemini returned invalid JSON. Please try again."
        )

    return result


# =====================================
# 4. SERPAPI SHOPPING SEARCH
# =====================================

def search_products(search_query):

    api_key = get_api_key("SERPAPI_API_KEY")

    if not api_key:
        raise ValueError(
            "SerpAPI key is missing. "
            "Please configure SERPAPI_API_KEY in Streamlit Secrets."
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


# =====================================
# 5. PRICE COMPARISON
# =====================================

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
            "Product": product.get(
                "title", "Unknown"
            ),

            "Price": price,

            "Seller": product.get(
                "source", "Unknown"
            ),

            "Link": product.get(
                "link", ""
            )
        })

    df = pd.DataFrame(rows)

    if not df.empty:

        df = df.sort_values(
            by="Price",
            ascending=True
        ).reset_index(drop=True)

    return df


# =====================================
# 6. STREAMLIT USER INTERFACE
# =====================================

st.title("🛍️ AI Shopping Price Comparison Agent")

st.write(
    "Your AI-powered shopping assistant. "
    "Compare product prices across available online sellers."
)

st.divider()

user_query = st.text_input(
    "Enter product name",
    placeholder="Example: iPhone 17 Pro 256GB"
)

compare_button = st.button(
    "🔍 Compare Prices",
    type="primary"
)


# =====================================
# 7. MAIN APPLICATION
# =====================================

if compare_button:

    if not user_query.strip():

        st.warning(
            "Please enter a product name."
        )

    else:

        try:

            # AI PRODUCT UNDERSTANDING

            with st.spinner(
                "🤖 Gemini is understanding your search..."
            ):

                details = understand_query(
                    user_query
                )

            st.subheader(
                "🧠 AI Understood Your Request"
            )

            st.json(details)

            search_query = (
                details.get("search_query")
                or user_query
            )

            st.write(
                f"**Shopping search:** {search_query}"
            )

            # SHOPPING SEARCH

            with st.spinner(
                "🛒 Searching shopping listings..."
            ):

                products = search_products(
                    search_query
                )

            if not products:

                st.warning(
                    "No shopping results found. "
                    "Try a different product name."
                )

            else:

                # PRICE COMPARISON

                df = compare_prices(products)

                if df.empty:

                    st.warning(
                        "No usable numeric prices found."
                    )

                else:

                    st.subheader(
                        "💰 Price Comparison"
                    )

                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Price": st.column_config.NumberColumn(
                                "Price (INR)",
                                format="₹%.2f"
                            ),

                            "Link": st.column_config.LinkColumn(
                                "Product Link",
                                display_text="View Product"
                            )
                        }
                    )

                    # CHEAPEST PRODUCT

                    cheapest = df.iloc[0]

                    st.success(
                        f"🏆 Lowest listed price: "
                        f"₹{cheapest['Price']:,.2f}"
                    )

                    st.write(
                        f"**Seller:** {cheapest['Seller']}"
                    )

                    if cheapest["Link"]:

                        st.markdown(
                            f"[View Cheapest Product]({cheapest['Link']})"
                        )

                    st.caption(
                        "Prices are retrieved from shopping search listings. "
                        "Verify the final price, availability, shipping "
                        "and seller details at checkout."
                    )

        except Exception as error:

            st.error(
                f"Something went wrong: {error}"
            )

            st.info(
                "Check your API configuration and "
                "try again. Do not share your API keys."
            )


# =====================================
# 8. FOOTER
# =====================================

st.divider()

st.caption(
    "Powered by Google Gemini AI, SerpAPI and Streamlit."
)
