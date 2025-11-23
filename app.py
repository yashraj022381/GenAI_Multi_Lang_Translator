
import streamlit as st
from transformers import pipeline

# BEST tiny model for toxicity that actually works
toxicity = pipeline("text-classification", 
                    model="lxyuan/distilbert-base-multilingual-cased-toxic")

st.set_page_config(page_title="SafeGen", page_icon="Shield")

st.title("SafeGen – AI Output Safety Checker")
st.caption("Built for Indian freelancers | Free trial | ₹399/month later")

text = st.text_area("Paste any AI-generated text here", height=150)

if st.button("Check Safety", type="primary"):
    with st.spinner("Analyzing..."):
        result = toxicity(text)[0]
        score = result['score']
        label = result['label']

        # This model uses "toxic" and "non-toxic"
        if label == "toxic" and score > 0.7:
            st.error(f"High Risk – Toxic/Biased Output! (Confidence: {score:.2f})")
            st.write("Warning: Do NOT send this to clients")
            st.write("Fix: Add 'Answer politely and professionally' to your prompt")
        elif label == "toxic":
            st.warning(f"Medium Risk (Confidence: {score:.2f}) – Consider rephrasing")
        else:
            st.success("Safe & Professional!")
            st.balloons()

st.markdown("---")
st.markdown("Solo Indian founder • Free for first 100 users • ₹399/month after")
