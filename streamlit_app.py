import streamlit as st
import random
import base64
import os
import re
import unicodedata
import difflib
from tempfile import NamedTemporaryFile
from gtts import gTTS
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder

# ----------------------------
# Banco de frases por nível
# ----------------------------
nivel_facil = [
    ("Hi, how are you?", "I'm fine, thanks.", "Oi, como você está?", "Estou bem, obrigado."),
    ("What’s your name?", "My name is John.", "Qual é o seu nome?", "Meu nome é John."),
    ("Do you like coffee?", "Yes, I like coffee.", "Você gosta de café?", "Sim, eu gosto de café."),
    ("Good morning!", "Good morning!", "Bom dia!", "Bom dia!"),
    ("Thank you!", "You're welcome.", "Obrigado!", "De nada."),
    ("See you later!", "See you!", "Até mais!", "Até logo."),
    ("Excuse me", "Yes?", "Com licença", "Sim?"),
    ("I need help", "I can help you.", "Preciso de ajuda", "Eu posso ajudar."),
    ("Where is the restroom?", "It is over there.", "Onde fica o banheiro?", "Fica ali."),
    ("I am ready", "Great! Let's start.", "Estou pronto", "Ótimo! Vamos começar."),
]

nivel_medio = [
    ("Where is the box?", "The box is on the table.", "Onde está a caixa?", "A caixa está na mesa."),
    ("Can you help me?", "Yes, I can help you.", "Você pode me ajudar?", "Sim, eu posso te ajudar."),
    ("Do you work here?", "Yes, I do.", "Você trabalha aqui?", "Sim, eu trabalho aqui."),
    ("I need this item", "I will get it for you.", "Preciso deste item", "Vou pegar para você."),
    ("Check the inventory", "I will check it now.", "Verifique o inventário", "Vou verificar agora."),
    ("When will it arrive?", "Tomorrow morning.", "Quando vai chegar?", "Amanhã de manhã."),
    ("Where can I find the supplies?", "They are in aisle 3.", "Onde posso encontrar os suprimentos?", "No corredor 3."),
    ("Please sign here", "Okay, I will sign.", "Por favor, assine aqui", "Ok, vou assinar."),
    ("The truck is here", "I will unload it.", "O caminhão chegou", "Vou descarregar."),
    ("We need more boxes", "I will order them.", "Precisamos de mais caixas", "Vou pedir."),
]

nivel_dificil = [
    ("Do we have this item in stock?", "Yes, we have it.", "Temos este item em estoque?", "Sim, temos."),
    ("Please, sign the paper.", "Okay, I will sign.", "Por favor, assine o papel", "Ok, eu vou assinar."),
    ("The truck just arrived.", "I will check it.", "O caminhão acabou de chegar", "Eu vou verificar."),
    ("Where can I find the new supplies?", "They are in aisle 3.", "Onde posso encontrar os novos suprimentos?", "Estão no corredor 3."),
    ("Check the inventory for today.", "I will check it now.", "Verifique o inventário de hoje", "Vou verificar agora."),
    ("Can you organize the shelf?", "Yes, I will organize it.", "Pode organizar a prateleira", "Sim, vou organizar."),
    ("We need to prepare the order", "I will prepare it.", "Precisamos preparar o pedido", "Vou preparar."),
    ("Is this item damaged?", "No, it is fine.", "Este item está danificado?", "Não, está ok."),
    ("Confirm the delivery", "I will confirm it.", "Confirme a entrega", "Vou confirmar."),
    ("Update the stock list", "I will update it.", "Atualize a lista de estoque", "Vou atualizar."),
]

# ----------------------------
# Utilidades
# ----------------------------
def gerar_audio(texto, lang="en"):
    tts = gTTS(text=texto, lang=lang)
    filename = "voz.mp3"
    tts.save(filename)
    with open(filename, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    try:
        os.remove(filename)
    except Exception:
        pass
    return f'<audio autoplay controls src="data:audio/mp3;base64,{b64}"></audio>'

def normalizar(txt: str) -> str:
    txt = txt.strip().lower()
    txt = "".join(c for c in unicodedata.normalize("NFKD", txt) if not unicodedata.combining(c))
    txt = re.sub(r"[^a-z0-9']+", " ", txt)
    return " ".join(txt.split())

def similaridade(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, normalizar(a), normalizar(b)).ratio()

def verificar_texto(resposta_usuario: str, resposta_correta: str):
    if not resposta_usuario.strip():
        return ("warn", "Digite sua resposta ou use o microfone.", 0)

    if normalizar(resposta_usuario) == normalizar(resposta_correta):
        return ("success", "✅ Correto!", 1)

    sim = similaridade(resposta_usuario, resposta_correta)

    if sim >= 0.9:
        return ("info", f"Quase perfeito! (similaridade {sim*100:.0f}%).", 0)
    elif sim >= 0.75:
        return ("error", f"Pequenos erros detectados (similaridade {sim*100:.0f}%).", 0)
    else:
        return ("error", f"❌ Errado (similaridade {sim*100:.0f}%).", 0)

def transcrever_wav_bytes(wav_bytes: bytes, language="en-US") -> str | None:
    r = sr.Recognizer()
    with NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(wav_bytes)
        tmp_path = tmp.name
    try:
        with sr.AudioFile(tmp_path) as source:
            audio = r.record(source)
        return r.recognize_google(audio, language=language)
    except sr.UnknownValueError:
        return None
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

# ----------------------------
# App Streamlit
# ----------------------------
st.set_page_config(page_title="Treino de Inglês - Almoxarifado", page_icon="📦")
st.title("📦 English Dialogue Trainer - Almoxarifado")

nivel = st.selectbox("Selecione o nível:", ["Fácil", "Médio", "Difícil"])
banco = nivel_facil if nivel == "Fácil" else nivel_medio if nivel == "Médio" else nivel_dificil

# Inicializar session_state
if "frase_atual" not in st.session_state:
    st.session_state.frase_atual = random.choice(banco)
    st.session_state.score = 0
    st.session_state.total = 0
    st.session_state.streak = 0
    st.session_state.historico = []

if "nivel_sel" not in st.session_state:
    st.session_state.nivel_sel = nivel
elif st.session_state.nivel_sel != nivel:
    st.session_state.nivel_sel = nivel
    st.session_state.frase_atual = random.choice(banco)
    st.session_state.streak = 0
    st.rerun()

pergunta_en, resposta_en, pergunta_pt, resposta_pt = st.session_state.frase_atual

# --- Exibição ---
st.subheader("Frase para treinar:")
st.markdown(f"**{pergunta_en}**")
if nivel == "Fácil":
    st.markdown(f"*({pergunta_pt})*")
else:
    if st.checkbox("Mostrar tradução", False):
        st.markdown(f"*({pergunta_pt})*")

st.subheader("Resposta sugerida:")
st.markdown(f"**{resposta_en}**")
if nivel == "Fácil":
    st.markdown(f"*({resposta_pt})*")
else:
    if st.checkbox("Mostrar tradução da resposta", False):
        st.markdown(f"*({resposta_pt})*")

# --- Ouvir ---
col1, col2 = st.columns(2)
with col1:
    if st.button("🔊 Ouvir frase em inglês"):
        st.markdown(gerar_audio(pergunta_en, "en"), unsafe_allow_html=True)
with col2:
    if st.button("🔊 Ouvir resposta correta"):
        st.markdown(gerar_audio(resposta_en, "en"), unsafe_allow_html=True)

st.divider()

# --- Resposta por TEXTO ---
st.markdown("**Responder digitando:**")
resposta_usuario = st.text_input("Digite sua resposta em inglês:")

if st.button("✅ Verificar resposta (texto)"):
    st.session_state.total += 1
    status, msg, inc = verificar_texto(resposta_usuario, resposta_en)
    st.session_state.score += inc
    st.session_state.streak = st.session_state.streak + 1 if inc == 1 else 0

    st.session_state.historico.append(
        {"modo": "Texto", "resposta": resposta_usuario, "esperado": resposta_en, "resultado": msg}
    )

    if status == "success":
        st.success(msg + f" 🔥 Streak: {st.session_state.streak}")
        st.markdown(gerar_audio("Correct! Well done!", "en"), unsafe_allow_html=True)
    elif status == "info":
        st.info(msg)
    elif status == "warn":
        st.warning(msg)
    else:
        st.error(msg)
        st.session_state.streak = 0

# --- Resposta por ÁUDIO ---
st.divider()
st.markdown("**Responder falando (microfone):**")
st.caption("Clique em gravar, depois em transcrever e verificar.")

audio_bytes = audio_recorder(sample_rate=44100, pause_threshold=2.0, text="🎙️ Gravar / Parar")

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")

    if st.button("🗣️ Transcrever e verificar (áudio)"):
        transcrito = transcrever_wav_bytes(audio_bytes, language="en-US")
        if not transcrito:
            st.warning("Não consegui entender o áudio.")
        else:
            st.write(f"**Você disse:** _{transcrito}_")
            st.session_state.total += 1
            status, msg, inc = verificar_texto(transcrito, resposta_en)
            st.session_state.score += inc
            st.session_state.streak = st.session_state.streak + 1 if inc == 1 else 0

            st.session_state.historico.append(
                {"modo": "Áudio", "resposta": transcrito, "esperado": resposta_en, "resultado": msg}
            )

            if status == "success":
                st.success(msg + f" 🔥 Streak: {st.session_state.streak}")
                st.markdown(gerar_audio("Great pronunciation!", "en"), unsafe_allow_html=True)
            elif status == "info":
                st.info(msg)
            else:
                st.error(msg)
                st.session_state.streak = 0

st.divider()

if st.button("➡ Próxima frase"):
    st.session_state.frase_atual = random.choice(banco)
    st.rerun()

st.success(f"Pontuação: {st.session_state.score}/{st.session_state.total} | 🔥 Streak atual: {st.session_state.streak}")

# Histórico de respostas
if st.session_state.historico:
    st.subheader("📜 Histórico de respostas")
    for h in st.session_state.historico[-10:][::-1]:
        st.markdown(f"- **{h['modo']}** → Você disse: _{h['resposta']}_ | Correto: **{h['esperado']}** → {h['resultado']}")
