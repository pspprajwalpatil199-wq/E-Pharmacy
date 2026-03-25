import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Pharmacy App", page_icon="💊", layout="wide")

st.title("💊 E-Pharmacy Price Comparison")

col1, col2 = st.columns([1, 3])

# LEFT PANEL
with col1:
    st.subheader("🔍 Search Medicine")

    medicine = st.text_input("Enter Medicine Name")
    num = st.number_input("Number of Results", min_value=1, max_value=10, value=5)

    search = st.button("Search")

# RIGHT PANEL
with col2:
    if search:

        if medicine.strip() == "":
            st.warning("⚠️ Please enter medicine name")
        else:
            api_key = os.getenv("SERP_API_KEY") or "59588c989650e9665b4cfceeaf08f5227369f189ce71d245b10c146c7468c7d4"

            params = {
                "engine": "google_shopping",
                "q": medicine + " tablet medicine",
                "api_key": api_key,
                "gl": "in",
                "hl": "en",
                "location": "India"
            }

            response = requests.get("https://serpapi.com/search.json", params=params)
            data = response.json()

            results = data.get("shopping_results", [])

            products = []

            for item in results[:num]:
                products.append({
                    "Title": item.get("title"),
                    "RawPrice": item.get("price"),
                    "Link": item.get("product_link"),
                    "Image": item.get("thumbnail")
                })

            df = pd.DataFrame(products)

            if df.empty:
                st.error("❌ No results found")
            else:
                # Clean price
                df["Price"] = df["RawPrice"].str.replace(r"[^\d.]", "", regex=True)
                df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

                # Detect currency
                df["Currency"] = df["RawPrice"].apply(lambda x: "USD" if "$" in str(x) else "INR")

                # Convert USD → INR
                df.loc[df["Currency"] == "USD", "Price"] *= 83

                df = df.dropna(subset=["Price"])
                df = df.sort_values(by="Price")

                st.subheader("💰 Price Comparison")

                # -------- CARDS --------
                for i, row in df.iterrows():
                    st.markdown(f"""
                    <div style="
                        border:1px solid #ddd;
                        border-radius:12px;
                        padding:15px;
                        margin-bottom:15px;
                        box-shadow: 2px 2px 10px rgba(0,0,0,0.15);
                    ">
                        <h4>🧾 Option {i+1}</h4>
                        <p><b>💊 {row['Title']}</b></p>
                        <p>💰 Price: ₹{round(row['Price'],2)}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    st.link_button("🛒 Buy Now", row["Link"])

                    if row["Image"]:
                        st.image(row["Image"], width=150)

                # Cheapest
                st.success(f"🏆 Cheapest: {df.iloc[0]['Title']} → ₹{round(df.iloc[0]['Price'],2)}")

                # -------- BAR CHART --------
                st.subheader("📊 Price Comparison (Bar Chart)")

                bar_df = df.set_index("Title")["Price"]
                st.bar_chart(bar_df)

                # -------- PIE CHART (IMPROVED) --------
                st.subheader("🥧 Price Distribution")

                labels = df["Title"].str.slice(0, 20)

                explode = [0.1 if i == 0 else 0 for i in range(len(df))]  # highlight cheapest

                fig, ax = plt.subplots()

                ax.pie(
                    df["Price"],
                    labels=labels,
                    autopct="%1.1f%%",
                    explode=explode,
                    shadow=True,
                    startangle=140
                )

                ax.set_title("Price Share of Medicines")

                st.pyplot(fig)
