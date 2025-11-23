
import streamlit as st
from transformers import pipeline

# Cache the model loading – loads ONCE, never re-downloads
@st.cache_resource
def load_toxicity_model():
    return pipeline("text-classification", 
                    model="lxyuan/distilbert-base-multilingual-cased-toxic")

st.set_page_config(page_title="SafeGen", page_icon="🛡️")

st.title("🛡️ SafeGen – AI Output Safety Checker")
st.caption("Built for Indian freelancers & small teams | Free to try | ₹399/month later")

text = st.text_area("Paste any AI-generated text (ChatGPT, Gemini, etc.)", height=150)

if st.button("🔍 Check Safety", type="primary"):
    with st.spinner("Loading model & analyzing... (first time only)"):
        toxicity = load_toxicity_model()  # This caches it!
        result = toxicity(text)[0]
        score = result['score']
        label = result['label']

        if label == "toxic" and score > 0.7:
            st.error(f"🚨 High Risk – Toxic/Biased! (Score: {score:.2f})")
            st.write("⚠️ Warning: Don't send to clients – could lose trust!")
            st.write("💡 Fix: Add 'Respond politely, factually, and inclusively' to your prompt")
        elif label == "toxic":
            st.warning(f"⚠️ Medium Risk (Score: {score:.2f}) – Rephrase for safety")
        else:
            st.success("✅ Safe & Professional!")
            st.balloons()
st.markdown("---")
st.markdown("Solo Indian founder • Free for first 100 checks • [Follow on X](https://x.com/yourhandle)")
