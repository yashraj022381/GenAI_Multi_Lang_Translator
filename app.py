import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from streamlit_mic_recorder import mic_recorder
from groq import Groq

# Page config
st.set_page_config(page_title="भारत हेल्पर AI\nBharat Helper AI", page_icon="🇮🇳")
st.title("🇮🇳 भारत हेल्पर AI - अपनी भाषा में मदद\nBharat Helper AI - Help in your language")

# Sidebar
st.sidebar.markdown("**# 🇮🇳 भारत हेल्पर AI\nBharat Helper AI**")
st.sidebar.markdown("**🌟 बनाया\Created by:** Yashraj")
st.sidebar.markdown("**⚡ Powered by:** Groq + Llama 3.1")
st.sidebar.markdown("**🌍 भाषाएँ:** अंग्रेज़ी, हिंदी, मराठी, বাংলা, ਪੰਜਾਬੀ, தமிழ், తెలుగు और अधिक\nLanguages: English, Hindi, Marathi, Bengali, Punjabi, Tamil, Telugu and more")

# Clear chat
if st.sidebar.button("🗑️ चैट हिस्ट्री साफ़ करें\Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

# Initialize
if "messages" not in st.session_state:
    st.session_state.messages = []

# Groq key
try:
    groq_api_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("⚠️ GROQ_API_KEY नहीं मिला। Secrets में जोड़ें।\nGROQ_API_KEY not found. Please add it to Secrets")
    st.stop()

# Super multilingual system prompt
system_prompt = """You are "Bharat Helper" - a friendly AI assistant for people across India.

CRITICAL LANGUAGE RULE:
- Detect the language of the user's message carefully
- Reply STRICTLY in the SAME language the user used
- If user writes in English → reply in English
- If user writes in Hindi → reply in Hindi
- If user writes in Marathi → reply in Marathi
- If user writes in Bengali → reply in Bengali
- If user writes in Punjabi → reply in Punjabi
- If user writes in Tamil → reply in Tamil
- If user writes in Telugu → reply in Telugu
- If user writes in Gujarati → reply in Gujarati
- If user writes in Kannada → reply in Kannada
- If user writes in Malayalam → reply in Malayalam
- If user writes in mixed language (Hinglish, Marathi+Hindi) → reply in same mix
- NEVER switch to Hindi if the user did not write in Hindi
- NEVER translate the user's language into another language

Topics you help with: jobs, education, farming, government schemes, health, family, money, daily life.
Keep responses simple, warm, concise and encouraging."""

# Welcome message in multiple languages
if not st.session_state.messages:
    welcome = """नमस्ते! 🙏  
নমস্কার! | नमस्कार! | ਸਤ ਸ੍ਰੀ ਅਕਾਲ! | નમસ્તે!  
வணக்கம்! | నమస్కారం! | नमस्कार!

मैं भारत हेल्पर हूँ।  
आप अपनी मातृभाषा में कोई भी समस्या पूछ सकते हैं।  
नौकरी, पढ़ाई, खेती, सरकारी योजना, स्वास्थ्य - सबके लिए मदद करता हूँ।

आज आपकी क्या मदद करूँ? 😊\n\nHello! 🙏
Namaskar! | Sat Sri Akal! | Namaste!
Vanakkam! | Namaskaram! | Namaskar!

I am India Helper.
You can ask me any question in your mother tongue.
I provide help with jobs, education, farming, government schemes, health – and much more.

How can I help you today?"""
    
    
    st.session_state.messages.append(AIMessage(content=welcome))

# Show history
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)

# ... (after display history)
def get_ai_response(prompt):
    try:
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",  # Better at Indian languages than 8b
            # model="llama-3.1-8b-instant",  # Use this if you want max speed
            api_key=groq_api_key,
            temperature=0.7,
        )
        template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])
        chain = template | llm | StrOutputParser()
        history = st.session_state.messages[:-1]
        result = chain.invoke({
            "chat_history": history,
            "input": prompt
        })
        return result if result else "माफ़ करें, जवाब नहीं मिला। / Sorry, no response received."
    except:
        return f"Error: {str(e)}"

if "mic_key_counter" not in st.session_state:
    st.session_state.mic_key_counter = 0
# Mic input button
audio = mic_recorder(start_prompt="🎤 Start recording", stop_prompt="🛑 Stop", just_once = True, use_container_width = True, key=f'recorder_{st.session_state.mic_key_counter}')

if audio and audio.get('bytes'):
    try:
        # Detect real format from bytes header (mobile sends webm/ogg, desktop sends wav)
        audio_bytes = audio['bytes']
        
        if audio_bytes[:4] == b'OggS':
            ext = "ogg"
            mime = "audio/ogg"
        elif audio_bytes[0:4] == b'\x1aE\xdf\xa3' or audio_bytes[0:2] == b'\x1aE':
            ext = "audio/webm"
            mime = "audio/webm"
        else:
            ext = "wav"
            mime = "audio/wav"

        ext = ext.replace("/", " ").replace("audio", " ").strip(".")
        if ext not in ["wav", "ogg", "webm", "mp4", "m4a"]:
            ext = "wav"

        audio_filename = f"temp_audio.{ext}"

        with open(audio_filename, "wb") as f:
            f.write(audio_bytes)

        # Transcribe with Groq Whisper (add your Groq key if not already)
        client = Groq(api_key=groq_api_key)
        with open(audio_filename, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(audio_filename, file.read()),
                model="whisper-large-v3",
                response_format="verbose_json",
            )

        detected_lang = transcription.language
        raw_text = transcription.text.strip()

        speak_lang = st.selectbox(
            "🗣️ बोलने की भाषा / Speaking language:",
            options=["Auto", "Marathi", "Hindi", "English", "Bengali", 
                     "Punjabi", "Tamil", "Telugu", "Gujarati", "Kannada"],
            index=0
        )
        
        LANG_CODE_MAP = {
            "Auto": None, "Hindi": "hi", "Marathi": "mr",
            "English": "en", "Bengali": "bn", "Punjabi": "pa",
            "Tamil": "ta", "Telugu": "te", "Gujarati": "gu", "Kannada": "kn"
        }
            
        selected_lang_code = LANG_CODE_MAP[speak_lang]
        
        with open(audio_filename, "rb") as file:
            transcription2 = client.audio.transcriptions.create(
                file=(audio_filename, file.read()),
                model="whisper-large-v3",
                response_format="text",
                **({"language": selected_lang_code} if selected_lang_code else {})
            )
        prompt = transcription2.strip()  # Use transcribed text as inpu

        # Then proceed with adding to messages and generating response as before

        if prompt:
            st.session_state.messages.append(HumanMessage(content=prompt))
            with st.chat_message("user"):
                st.markdown(f"🎤 {prompt}")
            with st.chat_message("assistant"):
                with st.spinner("जवाब दे रहा हूँ... / Responding..."):
                    response = get_ai_response(prompt)
                    st.markdown(response)
            st.session_state.messages.append(AIMessage(content=response))
            st.session_state.mic_key_counter += 1
            st.rerun()
        else:
            st.warning("⚠️ आवाज़ नहीं सुनाई दी। फिर से बोलें। / Audio not detected. Please try again.")
    except Exception as e:
        st.error(f"🎤 माइक में गड़बड़ी / Mic error: {str(e)}")        

# User input
if prompt := st.chat_input("अपनी भाषा में लिखें... (अंग्रेज़ी, हिंदी, मराठी, বাংলা, ਪੰਜਾਬੀ, தமிழ் आदि)\Write in your own language... (English, Hindi, Marathi, Bengali, Punjabi, Tamil, etc.)"):
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("जवाब दे रहा हूँ...\n\nI am responding..."):
            # Use slightly smarter model for better language handling
            response = get_ai_response(prompt)
            if response:
                st.markdown(response)
                st.session_state.messages.append(AIMessage(content=str(response)))
                    
                        
        

