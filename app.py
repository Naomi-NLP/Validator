import streamlit as st
import pandas as pd
import os

# -----------------------------
# CONFIG
# -----------------------------
USERNAME = "admin"
PASSWORD = "143admin78"
GITHUB_URL = "https://raw.githubusercontent.com/Naomi-NLP/Validator/refs/heads/main/hiv_aids_glossary.csv"
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
    if "original_df" not in st.session_state:
        st.session_state.original_df = pd.read_csv(GITHUB_URL)
    original_df = st.session_state.original_df

    # Validated container
    if os.path.exists(VALIDATED_FILE):
        validated_df = pd.read_csv(VALIDATED_FILE)
    else:
        validated_df = pd.DataFrame(columns=original_df.columns)
    st.session_state.validated_df = validated_df

    # -----------------------------
    # 3️⃣ Track current row index
    # -----------------------------
    if "current_index" not in st.session_state:
        validated_indices = validated_df['S/N'].astype(str).tolist()
        unvalidated_df = original_df[~original_df['S/N'].astype(str).isin(validated_indices)]
        if len(unvalidated_df) > 0:
            st.session_state.current_index = unvalidated_df.index[0]
        else:
            st.session_state.current_index = None

    # -----------------------------
    # 4️⃣ Show current row
    # -----------------------------
    if st.session_state.current_index is None:
        st.success("🎉 All rows validated!")
    else:
        # Load saved edits if available
        sn_current = str(original_df.loc[st.session_state.current_index, "S/N"])
        existing_row = st.session_state.validated_df[
            st.session_state.validated_df['S/N'].astype(str) == sn_current
        ]

        if not existing_row.empty:
            row = existing_row.iloc[0]  # use saved edits
        else:
            row = original_df.loc[st.session_state.current_index]  # use original

        col1, col2 = st.columns(2)
        with col1:
            sn = st.text_input("S/N", row.get("S/N", ""))
            source = st.text_input("SOURCE", row.get("SOURCE", ""))
            definition = st.text_area("DEFINITION", row.get("DEFINITION", ""), height=150)
        with col2:
            yoruba = st.text_input("YORÙBÁ", row.get("YORÙBÁ", ""))
            translation = st.text_area("TRANSLATION", row.get("TRANSLATION", ""), height=150)

        # -----------------------------
        # 5️⃣ Save validated row
        # -----------------------------
        if st.button("💾 Save this row"):
            new_row = pd.DataFrame([{
                "S/N": sn,
                "SOURCE": source,
                "DEFINITION": definition,
                "YORÙBÁ": yoruba,
                "TRANSLATION": translation
            }])

            # Replace if S/N exists, else append
            existing_index = st.session_state.validated_df.index[
                st.session_state.validated_df['S/N'].astype(str) == str(sn)
            ].tolist()

            if existing_index:
                st.session_state.validated_df.loc[existing_index[0]] = new_row.iloc[0]
            else:
                st.session_state.validated_df = pd.concat([st.session_state.validated_df, new_row], ignore_index=True)

            st.session_state.validated_df.to_csv(VALIDATED_FILE, index=False)
            st.success(f"Row {sn} saved/updated in validated container ✅")

            # Move to next unvalidated row
            validated_indices = st.session_state.validated_df['S/N'].astype(str).tolist()
            unvalidated_df = original_df[~original_df['S/N'].astype(str).isin(validated_indices)]
            if len(unvalidated_df) > 0:
                st.session_state.current_index = unvalidated_df.index[0]
            else:
                st.session_state.current_index = None

        # -----------------------------
        # 6️⃣ Navigation buttons
        # -----------------------------
        col_prev, col_next = st.columns(2)
        with col_prev:
            if st.button("⬅ Previous") and st.session_state.current_index is not None:
                prev_indices = original_df.index[original_df.index < st.session_state.current_index].tolist()
                if prev_indices:
                    st.session_state.current_index = prev_indices[-1]
        with col_next:
            if st.button("Next ➡") and st.session_state.current_index is not None:
                next_indices = original_df.index[original_df.index > st.session_state.current_index].tolist()
                if next_indices:
                    st.session_state.current_index = next_indices[0]

    # -----------------------------
    # 7️⃣ Admin-only download
    # -----------------------------
    st.subheader("🔒 Admin Download")
    password = st.text_input("Enter admin password for download", type="password")
    if password == PASSWORD:
        if os.path.exists(VALIDATED_FILE):
            csv_bytes = open(VALIDATED_FILE, "rb").read()
            st.download_button(
                "📥 Download Validated Container",
                csv_bytes,
                VALIDATED_FILE,
                "text/csv"
            )
            st.success("✅ You are authenticated as admin")
        else:
            st.warning("No validated CSV exists yet.")
    elif password:
        st.error("❌ Wrong password")
