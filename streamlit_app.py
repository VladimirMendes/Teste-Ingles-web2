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
import pandas as pd

# =============================
# Configuração da página
# =============================
st.set_page_config(page_title="Treino de Inglês - Almoxarifado", page_icon="📦", layout="centered")
st.title("📦 English Dialogue Trainer – Almoxarifado")
st.caption("Pratique perguntas e respostas em inglês com tradução em português conforme o nível.")

# =============================
# Banco de frases por nível
# =============================
nivel_facil = [
    ("Hi, how are you?", "I'm fine, thanks.", "Oi, como você está?", "Estou bem, obrigado."),
    ("What’s your name?", "My name is John.", "Qual é o seu nome?", "Meu nome é John."),
    ("Do you like coffee?", "Yes, I like coffee.", "Você gosta de café?", "Sim, eu gosto de café."),
]

nivel_medio = [
    ("Where is the box?", "The box is on the table.", "Onde está a caixa?", "A caixa está na mesa."),
    ("Can you help me?", "Yes, I can help you.", "Você pode me ajudar?", "Sim, eu posso te ajudar."),
]

nivel_dificil = [
    ("Do we have this item in stock?", "Yes, we have it.", "Temos este item em estoque?", "Sim, temos."),
    ("Please, sign the paper.", "Okay, I will sign.", "Por favor, assine o papel", "Ok, eu vou assinar."),
]

def escolher_banco(nivel):
    return nivel_facil if nivel=="Fácil" else nivel_medio if nivel=="Médio" else nivel_dificil

# =============================
# Funções auxiliares
# =============================
def gerar_audio(texto, lang="en"):
    tts = gTTS(text=texto, lang=lang)
    filename = "voz.mp3"
    tts.save(filename)
    with open(filename, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    os.remove(filename)
    return f'<audio controls src="data:audio/mp3;base64,{b64}"></audio>'

def normalizar(txt: str) -> str:
    txt = txt.strip().lower()
    txt = "".join(c for c in unicodedata.normalize("NFKD", txt) if not unicodedata.combining(c))
    txt = re.sub(r"[^a-z0-9']+", " ", txt)
    return " ".join(txt.split())

def similaridade(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, normalizar(a), normalizar(b)).ratio()

def classificar_erro(user: str, correct: str) -> str:
    sim = similaridade(user, correct)
    if sim >= 0.9: return f"Quase perfeito ({sim*100:.0f}%)"
    if sim >= 0.75: return f"Pequeno erro ({sim*100:.0f}%)"
    if sim >= 0.6: return f"Erro moderado ({sim*100:.0f}%)"
    return f"Muito diferente ({sim*100:.0f}%)"

def verificar_texto(resposta_usuario: str, resposta_correta: str):
    if not resposta_usuario.strip():
        return ("warn", "Digite algo ou use o microfone.", 0, 0.0)
    if normalizar(resposta_usuario) == normalizar(resposta_correta):
        return ("success", "✅ Correto!", 1, 1.0)
    sim = similaridade(resposta_usuario, resposta_correta)
    if sim >= 0.75:
        return ("info", classificar_erro(resposta_usuario, resposta_correta), 0, sim)
    return ("error", classificar_erro(resposta_usuario, resposta_correta), 0, sim)

def transcrever_wav_bytes(wav_bytes: bytes, language="en-US") -> str | None:
    r = sr.Recognizer()
    with NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(wav_bytes)
        tmp_path = tmp.name
    try:
        with sr.AudioFile(tmp_path) as source:
            audio = r.record(source)
        return r.recognize_google(audio, language=language)
    except:
        return None
    finally:
        os.remove(tmp_path)

# =============================
# Estado da sessão
# =============================
if "nivel" not in st.session_state: st.session_state.nivel = "Fácil"
if "frase_atual" not in st.session_state: st.session_state.frase_atual = random.choice(nivel_facil)
if "score" not in st.session_state: st.session_state.score = 0
if "streak" not in st.session_state: st.session_state.streak = 0
if "history" not in st.session_state: st.session_state.history = []
if "difficult_words" not in st.session_state: st.session_state.difficult_words = {}

# =============================
# Seleção de nível
# =============================
nivel = st.radio("Nível:", ["Fácil", "Médio", "Difícil"], index=["Fácil","Médio","Difícil"].index(st.session_state.nivel))
if nivel != st.session_state.nivel:
    st.session_state.nivel = nivel
    st.session_state.frase_atual = random.choice(escolher_banco(nivel))

pergunta_en, resposta_en, pergunta_pt, resposta_pt = st.session_state.frase_atual

# =============================
# Barra de progresso
# =============================
st.progress(st.session_state.score/10 if st.session_state.score>0 else 0)
st.write(f"✅ Pontos: {st.session_state.score} | 🔥 Streak: {st.session_state.streak}")

# =============================
# Exibição da frase
# =============================
st.subheader("Frase para treinar:")
if nivel=="Fácil":
    st.markdown(f"**EN:** {pergunta_en}\n*PT:* {pergunta_pt}")
else:
    st.markdown(f"**EN:** {pergunta_en}")
    if st.checkbox("👁️ Mostrar tradução"):
        st.markdown(f"*PT:* {pergunta_pt}")

with st.expander("💡 Resposta sugerida"):
    if nivel=="Difícil":
        st.markdown(f"**EN:** {resposta_en}")
    else:
        st.markdown(f"**EN:** {resposta_en}\n*PT:* {resposta_pt}")

# =============================
# Ouvir pergunta e resposta
# =============================
col1, col2 = st.columns(2)
with col1:
    if st.button("🔊 Ouvir pergunta (EN)"):
        st.markdown(gerar_audio(pergunta_en), unsafe_allow_html=True)
with col2:
    if st.button("🔊 Ouvir resposta (EN)"):
        st.markdown(gerar_audio(resposta_en), unsafe_allow_html=True)

# =============================
# Resposta por texto
# =============================
resposta_usuario = st.text_input("Digite sua resposta em inglês:")
if st.button("✅ Verificar resposta (texto)"):
    status, msg, inc, sim = verificar_texto(resposta_usuario, resposta_en)
    st.session_state.score += inc
    st.session_state.streak = st.session_state.streak+1 if inc else 0
    if status=="success": st.success(msg)
    elif status=="info": st.info(msg)
    elif status=="warn": st.warning(msg)
    else: st.error(msg)
    
    st.session_state.history.append({
        "nivel": nivel,
        "pergunta": pergunta_en,
        "resposta_correta": resposta_en,
        "resposta_usuario": resposta_usuario,
        "resultado": status,
        "similaridade": round(sim,2)
    })
    
    if status!="success":
        st.session_state.difficult_words[resposta_en] = st.session_state.difficult_words.get(resposta_en,0)+1

# =============================
# Resposta por áudio
# =============================
st.divider()
st.markdown("### 🎙️ Responder falando")
audio_bytes = audio_recorder(sample_rate=44100, text="🎤 Gravar / Parar")
if audio_bytes and st.button("🗣️ Transcrever e verificar"):
    transcrito = transcrever_wav_bytes(audio_bytes)
    if not transcrito:
        st.warning("Não entendi o áudio, tente novamente.")
    else:
        st.write(f"Você disse: **{transcrito}**")
        status, msg, inc, sim = verificar_texto(transcrito, resposta_en)
        st.session_state.score += inc
        st.session_state.streak = st.session_state.streak+1 if inc else 0
        if status=="success": st.success(msg)
        elif status=="info": st.info(msg)
        else: st.error(msg)
        
        st.session_state.history.append({
            "nivel": nivel,
            "pergunta": pergunta_en,
            "resposta_correta": resposta_en,
            "resposta_usuario": transcrito,
            "resultado": status,
            "similaridade": round(sim,2)
        })
        
        if status!="success":
            st.session_state.difficult_words[resposta_en] = st.session_state.difficult_words.get(resposta_en,0)+1

# =============================
# Próxima frase
# =============================
if st.button("➡ Próxima"):
    if st.session_state.difficult_words and random.random()<0.3:
        alvo = random.choice(list(st.session_state.difficult_words.keys()))
        for f in escolher_banco(nivel):
            if f[1]==alvo: st.session_state.frase_atual = f
    else:
        st.session_state.frase_atual = random.choice(escolher_banco(nivel))
    st.rerun()

# =============================
# Histórico e vocabulário
# =============================
st.divider()
st.markdown("## 🧾 Histórico de respostas")
if not st.session_state.history:
    st.write("Nenhum registro ainda.")
else:
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.write("📌 Palavras difíceis:")
    if st.session_state.difficult_words:
        for w,c in st.session_state.difficult_words.items():
            st.write(f"- {w} (erros: {c})")
    else:
        st.write("Nenhuma por enquanto 🚀")
