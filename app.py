import streamlit as st  # grensesnitt

st.set_page_config(page_title="Tennis-Bot", page_icon="🎾")  # setter navn + ikon på fanen

# 1) Backend-funksjon (byttes ut med RAG senere)
def answer_question(question: str) -> str:   # OBS: du hadde feil her ("->:" i stedet for ") -> str:")
    return f"Du spurte: '{question}'. Når RAG er koblet på kommer et virkelig svar her."  
    # NB: "kommet" -> "kommer" (skrivfeil)

# 2) Tittel på siden
st.title("Tennis BOT")

# 3) Input-felt for spørsmålet
question = st.text_input("Skriv spørsmålet ditt:")

# 4) Knapp som utløser svaret
if st.button("Søk 🎾"):   # OBS: du manglet en avsluttende parentes her
    if question.strip():  # sjekker at feltet ikke bare er tomt
        answer = answer_question(question)
        st.write(answer)
    else:
        st.warning("Skriv et spørsmål først")
