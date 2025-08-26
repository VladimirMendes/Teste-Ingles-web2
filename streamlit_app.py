import streamlit as st
import random
import speech_recognition as sr

# ==============================
# Frases de treino
# ==============================
frases = {
    "fácil": [
        ("I like apples", "Eu gosto de maçãs"),
        ("She is happy", "Ela está feliz"),
        ("We are friends", "Nós somos amigos"),
        ("He has a dog", "Ele tem um cachorro"),
        ("The sky is blue", "O céu é azul"),
    ],
    "médio": [
        ("I will travel tomorrow", "Eu viajarei amanhã"),
        ("She is reading a book", "Ela está lendo um livro"),
        ("They are playing football", "Eles estão jogando futebol"),
        ("He is cooking dinner", "Ele está cozinhando o jantar"),
        ("We are studying English", "Nós estamos estudando inglês"),
    ],
    "difícil": [
        ("If I had known, I would have helped you", "Se eu soubesse, teria ajudado você"),
        ("She might have finished the work by now", "Ela pode já ter terminado o trabalho agora"),
        ("They should have arrived earlier", "Eles deveriam ter chegado mais cedo"),
        ("Had I studied harder, I would have passed the test", "Se eu tivesse estudado mais, teria passado na prova"),
        ("We could have won if we had tried", "Nós poderíamos ter vencido se tivéssemos tentado"),
    ],
}

# ==============================
# Inicialização de estado
# ==============================
if "nivel" not in st.session_state:
    st.session_state.nivel = None
if "frase_atual" not in st.session_state:
    st.session_state.frase_atual = None
if "mostrar_resposta" not in st.session_state:
    st.session_state.mostrar_resposta = False
if "resposta_usuario" not in st.session_state:
    st.session_state.resposta_usuario = ""
if "modo_audio" not in st.session_state:
    st.session_state.modo_audio = False

# ==============================
# Funções
# ==============================
def escolher_frase(nivel):
    st.session_state.frase_atual = random.choice(frases[nivel])
    st.session_state.mostrar_resposta = False
    st.session_state.resposta_usuario = ""

def reconhecer_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Fale agora...")
        audio = r.listen(source)
        try:
            texto = r.recognize_google(audio, language="en-US")
            st.success(f"Você disse: {texto}")
            return texto
        except sr.UnknownValueError:
            st.error("Não entendi o que você disse.")
        except sr.RequestError:
            st.error("Erro no serviço de reconhecimento de voz.")
    return ""

# ==============================
# Layout principal
# ==============================
st.title("🇺🇸 Treinamento de Inglês")

# Escolher nível
st.sidebar.header("Configuração")
nivel = st.sidebar.radio("Escolha o nível:", ["fácil", "médio", "difícil"])

if st.session_state.nivel != nivel or st.session_state.frase_atual is None:
    st.session_state.nivel = nivel
    escolher_frase(nivel)

frase_en, frase_pt = st.session_state.frase_atual

st.subheader("Traduza a frase:")

# Mostrar frase de acordo com nível
if nivel == "fácil":
    st.write(f"**Inglês:** {frase_en}")
    st.write(f"**Português:** {frase_pt}")
else:
    st.write(f"**Inglês:** {frase_en}")

# Opção de resposta
modo = st.radio("Como você quer responder?", ["✍️ Texto", "🎤 Áudio"])

if modo == "✍️ Texto":
    resposta = st.text_input("Digite sua resposta em inglês ou português:", value=st.session_state.resposta_usuario)
    st.session_state.resposta_usuario = resposta
elif modo == "🎤 Áudio":
    if st.button("🎙️ Gravar resposta"):
        resposta_audio = reconhecer_audio()
        if resposta_audio:
            st.session_state.resposta_usuario = resposta_audio

# Botão para verificar
if st.button("Verificar resposta"):
    st.session_state.mostrar_resposta = True

# Mostrar resultado
if st.session_state.mostrar_resposta:
    st.write("### ✅ Resposta correta:")
    st.write(f"- Inglês: **{frase_en}**")
    st.write(f"- Português: **{frase_pt}**")

    if st.session_state.resposta_usuario:
        st.write("### 📌 Sua resposta:")
        st.write(st.session_state.resposta_usuario)

    if st.button("Próxima frase"):
        escolher_frase(nivel)
