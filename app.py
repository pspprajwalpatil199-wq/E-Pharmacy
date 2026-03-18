import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# MUST BE FIRST
st.set_page_config(page_title="Pharmacy App", page_icon="💊", layout="wide")

st.title("💊 E-Pharmacy Price Comparison")

medicine = st.text_input("Enter Medicine Name")
num = st.number_input("Number of Results", min_value=1, max_value=10, value=5)

if st.button("Search"):

    if medicine == "":
        st.warning("⚠️ Please enter medicine name")
    else:
        api_key = "59588c989650e9665b4cfceeaf08f5227369f189ce71d245b10c146c7468c7d4"

        params = {
            "engine": "google_shopping",
            "q": medicine + " tablet medicine",
            "api_key": api_key
        }

        response = requests.get("https://serpapi.com/search.json", params=params)
        data = response.json()

        results = data.get("shopping_results", [])

        products = []

        for item in results[:num]:
            products.append({
                "Title": item.get("title"),
                "Price": item.get("price"),
                "Link": item.get("product_link")
            })

        df = pd.DataFrame(products)

        # Clean price
        df["Price"] = df["Price"].str.replace(r"[^\d.]", "", regex=True).astype(float)

        # Sort
        df = df.sort_values(by="Price")

        # Show results
        st.subheader("💰 Price Comparison")

        for i, row in df.iterrows():
            st.markdown(f"""
            ### 🧾 Option {i+1}
            **💊 Medicine:** {row['Title']}  
            **💰 Price:** ₹{row['Price']}  
            **🔗 [Buy Now]({row['Link']})**
            """)

        # Highlight cheapest
        st.success(f"🏆 Cheapest: {df.iloc[0]['Title']} → ₹{df.iloc[0]['Price']}")

        # Bar chart
        st.subheader("📊 Price Chart")
        st.bar_chart(df.set_index("Title")["Price"])

        # Pie chart
        st.subheader("🥧 Price Distribution")
        fig, ax = plt.subplots()
        ax.pie(df["Price"], labels=df["Title"], autopct="%1.1f%%")
        st.pyplot(fig)