
import os
import json
import requests
import pandas as pd
import streamlit as st

from dotenv import load_dotenv
from openai import OpenAI


st.set_page_config(
    page_title="AI Shopping Assistant",
    page_icon="🛍️",
    layout="wide"
)

load_dotenv()


def get_api_key(key_name):

    # First check local .env file
    value = os.getenv(key_name)

    if value:
        return value

    # Then check Streamlit Cloud Secrets
    try:
        return st.secrets.get(key_name)

    except Exception:
        return None


def understand_query(user_query):

    api_key = get_api_key("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OpenAI API key is missing. "
            "Please configure it in Streamlit Secrets."
        )

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": """
                Extract shopping product information.

                Return JSON with:
                product_name,
                specifications,
                search_query.

                Do not invent missing specifications.
                """
            },
            {
                "role": "user",
                "content": user_query
            }
        ]
    )

    result = response.choices[0].message.content

    return json.loads(result)


def search_products(search_query):

    api_key = get_api_key("SERPAPI_API_KEY")

    if not api_key:
        raise ValueError(
            "SerpAPI key is missing. "
            "Please configure it in Streamlit Secrets."
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

    return data.get("shopping_results", [])



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



st.title("🛍️ AI Shopping Price Comparison Agent")

st.write(
    "Search for a product and compare "
    "available shopping prices across listings."
)

st.info(
    "Enter a product name to find available "
    "shopping listings and compare their prices."
)

user_query = st.text_input(
    "Enter product name",
    placeholder="Example: iPhone 17 Pro 256GB"
)

if st.button("🔍 Compare Prices", type="primary"):

    if not user_query.strip():

        st.warning("Please enter a product name.")

    else:

        try:

            with st.spinner("Understanding your search..."):

                details = understand_query(user_query)

            st.subheader("AI understood your request")
            st.json(details)

            search_query = details.get(
                "search_query",
                user_query
            )

            with st.spinner("Searching shopping listings..."):

                products = search_products(search_query)

            if not products:

                st.warning("No shopping results found.")

            else:

                df = compare_prices(products)

                if df.empty:

                    st.warning(
                        "No usable numeric prices were found."
                    )

                else:

                    st.subheader("Price Comparison")

                    display_df = df.drop(columns=["Link"])

                    st.dataframe(
                        display_df,
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
                        "Prices are retrieved shopping listings. "
                        "Verify the final price, availability, "
                        "shipping and seller details at checkout."
                    )

        except Exception as error:

            st.error(f"Something went wrong: {error}")



st.divider()

st.caption(
    "AI-Powered Shopping Price Comparison Agent | "
    "Product prices may change."
)
