import streamlit as st                           # UI
from rag_generate import answer_question         # riktig import av adapteren

st.set_page_config(page_title="Tennis-Bot", page_icon="🎾")

st.title("Tennis BOT")
q = st.text_input("Skriv spørsmålet ditt:")      # input fra bruker

if st.button("Søk 🎾") and q.strip():            # kjør bare hvis knapp + ikke tom streng
    r = answer_question(q, top_k=3)              # kall RAG; returnerer dict
    st.write(r.get("answer", "(ingen svar)"))    # vis svaret
