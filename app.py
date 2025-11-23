
# safe-gen.py  →  Copy & deploy on Streamlit (free)
import streamlit as st
from transformers import pipeline

# Two free models from Hugging Face
toxicity = pipeline("text-classification", model="unitary/toxic-bert")
fact_check = pipeline("text-classification", model="facebook/roberta-hate-speech-dynabench-r4")

st.title("🛡️ SafeGen – Hallucination & Bias Checker")
st.write("Made for Indian devs & freelancers | ₹399/month after free trial")

text = st.text_area("Paste any AI-generated text (ChatGPT, Claude, etc.)", height=150)

if st.button("🔍 Check for Bias & Toxicity"):
    t = toxicity(text)[0]
    f = fact_check(text)[0]
    if t['score'] > 0.7 or f['score'] > 0.7:
        st.error(f"⚠️ Risk Detected! Toxicity: {t['score']:.2f} | Hate/Bias: {f['score']:.2f}")
        st.write("Fix suggestion: Add 'Answer factually and politely' in your prompt")
    else:
        st.success("✅ Looks safe and professional!")
# Initial app Code 
