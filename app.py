import streamlit as st
import pandas as pd
import os

# -----------------------------
# CONFIG
# -----------------------------
USERNAME = "admin"
PASSWORD = "143admin78"
GITHUB_URL = "https://raw.githubusercontent.com/Naomi-NLP/Validator/refs/heads/main/hiv_aids_glossary.csv"  # replace
VALIDATED_FILE = "validated_container.csv"

st.set_page_config(layout="wide")
st.title("📘 English–Yorùbá Glossary Validator")

# -----------------------------
# 1️⃣ LOGIN
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("🔐 Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == USERNAME and pwd == PASSWORD:
            st.session_state.logged_in = True
            st.success("✅ Logged in!")
        else:
            st.error("❌ Wrong username or password")
else:
    st.success("✅ Logged in as admin")

    # -----------------------------
    # 2️⃣ Load datasets
    # -----------------------------
    # Original CSV (read-only)
    original_df = pd.read_csv(GITHUB_URL)

    # Validated container (new container)
    if os.path.exists(VALIDATED_FILE):
        validated_df = pd.read_csv(VALIDATED_FILE)
    else:
        validated_df = pd.DataFrame(columns=original_df.columns)

    # Determine next row to validate
    validated_indices = validated_df['S/N'].astype(int).tolist()
    unvalidated_df = original_df[~original_df['S/N'].astype(int).isin(validated_indices)]
    st.write(f"Rows remaining to validate: {len(unvalidated_df)}")

    if len(unvalidated_df) == 0:
        st.success("🎉 All rows validated!")
    else:
        # Pick the first unvalidated row
        row = unvalidated_df.iloc[0]
        idx = row.name  # original index

        col1, col2 = st.columns(2)
        with col1:
            sn = st.text_input("S/N", row.get("S/N", ""))
            source = st.text_input("SOURCE", row.get("SOURCE", ""))
            definition = st.text_area("DEFINITION", row.get("DEFINITION", ""), height=150)
        with col2:
            yoruba = st.text_input("YORÙBÁ", row.get("YORÙBÁ", ""))
            translation = st.text_area("TRANSLATION", row.get("TRANSLATION", ""), height=150)

        # -----------------------------
        # Save validated row
        # -----------------------------
        if st.button("💾 Save this row"):
            new_row = pd.DataFrame([{
                "S/N": sn,
                "SOURCE": source,
                "DEFINITION": definition,
                "YORÙBÁ": yoruba,
                "TRANSLATION": translation
            }])
            # Append to validated container
            validated_df = pd.concat([validated_df, new_row], ignore_index=True)
            validated_df.to_csv(VALIDATED_FILE, index=False)
            st.success(f"Row {sn} saved to validated container ✅")
            st.experimental_rerun()  # refresh and load next row

        # -----------------------------
        # Admin-only download
        # -----------------------------
        st.subheader("🔒 Admin Download")
        if st.button("📥 Download Validated Container"):
            csv_bytes = validated_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download CSV",
                csv_bytes,
                VALIDATED_FILE,
                "text/csv"
            )
