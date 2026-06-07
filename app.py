import streamlit as st
import pickle
import pandas as pd

# ==========================
# Load Model and Data
# ==========================

model = pickle.load(open("model.pkl", "rb"))
symptom_index = pickle.load(open("symptom_index.pkl", "rb"))

description_df = pd.read_csv("symptom_Description.csv")
precaution_df = pd.read_csv("symptom_precaution.csv")

# ==========================
# Page Title
# ==========================

st.set_page_config(
    page_title="Disease Prediction System",
    page_icon="🩺",
    layout="centered"
)

st.title("🩺 AI Disease Prediction System")
st.write(
    "Select symptoms and predict the most likely disease using Machine Learning."
)

# ==========================
# Symptoms Dropdown
# ==========================

all_symptoms = sorted(list(symptom_index.keys()))

selected_symptoms = st.multiselect(
    "Select Symptoms",
    all_symptoms
)

# ==========================
# Prediction Button
# ==========================

if st.button("Predict Disease"):

    if len(selected_symptoms) == 0:
        st.warning("Please select at least one symptom.")
    else:

        input_vector = [0] * len(symptom_index)

        for symptom in selected_symptoms:
            input_vector[symptom_index[symptom]] = 1

        prediction = model.predict([input_vector])

        disease = prediction[0]

        # ==========================
        # Disease Result
        # ==========================

        st.success(
            f"Predicted Disease: {disease}"
        )

        # ==========================
        # Disease Description
        # ==========================

        st.subheader("📖 Disease Description")

        description_row = description_df[
            description_df["Disease"] == disease
        ]

        if not description_row.empty:

            description_column = description_row.columns[1]

            st.info(
                description_row.iloc[0][description_column]
            )

        else:
            st.write("Description not available.")

        # ==========================
        # Precautions
        # ==========================

        st.subheader("🛡️ Recommended Precautions")

        precaution_row = precaution_df[
            precaution_df["Disease"] == disease
        ]

        if not precaution_row.empty:

            for col in precaution_row.columns[1:]:

                value = precaution_row.iloc[0][col]

                if pd.notna(value):
                    st.write(f"✅ {value}")

        else:
            st.write("Precautions not available.")