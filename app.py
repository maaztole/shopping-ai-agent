import os
import json
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def understand_query(user_query):

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

import requests

def search_products(search_query):

    url = "https://serpapi.com/search.json"

    params = {
        "engine": "google_shopping",
        "q": search_query,
        "api_key": os.getenv("SERPAPI_API_KEY"),
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

import pandas as pd

def compare_prices(products):

    rows = []

    for product in products:

        price = product.get("extracted_price")

        if price is None:
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

st.set_page_config(
    page_title="AI Shopping Assistant",
    page_icon="🛍️",
    layout="wide"
)

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

        with st.spinner("Understanding your search..."):

            try:
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

