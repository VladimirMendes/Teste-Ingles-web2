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
import json

# =============================
# Arquivo para salvar progresso
# =============================
USER_DATA_FILE = "user_progress.json"

def load_user_progress():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"acertos": {}, "erros": {}}

def save_user_progress(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# =============================
# Carregar frases e vocabulário de arquivos JSON externos
# =============================
with open("frases.json", "r", encoding="utf-8") as f:
    frases_por_nivel = json.load(f)

with open("vocabulario.json", "r", encoding="utf-8") as f:
    Vocabulário = json.load(f)

def escolher_banco(nivel):
    return frases_por_nivel.get(nivel, [])

# =============================
# Funções utilitárias
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
# Estado da Sessão
# =============================
if "nivel" not in st.session_state: st.session_state.nivel = "Fácil"
if "frase_atual" not in st.session_state: st.session_state.frase_atual = random.choice(escolher_banco("Fácil"))
if "score" not in st.session_state: st.session_state.score = 0
if "streak" not in st.session_state: st.session_state.streak = 0
if "history" not in st.session_state: st.session_state.history = []
if "difficult_words" not in st.session_state: st.session_state.difficult_words = {}
if "voc_index" not in st.session_state: st.session_state.voc_index = 0
if "resposta_usuario" not in st.session_state: st.session_state.resposta_usuario = ""

progress = load_user_progress()

# =============================
# Configuração da página
# =============================
st.set_page_config(page_title="Treino de Inglês - Almoxarifado", page_icon="📦", layout="centered")
st.title("📦 English Dialogue Trainer – Almoxarifado")
st.caption("Perguntas e respostas aparecem em **inglês** com **tradução em português** (dependendo do nível).")

# =============================
# Escolha do nível
# =============================
nivel = st.radio("Nível:", ["Fácil", "Médio", "Difícil"], index=["Fácil","Médio","Difícil"].index(st.session_state.nivel))
if nivel != st.session_state.nivel:
    st.session_state.nivel = nivel
    st.session_state.frase_atual = random.choice(escolher_banco(nivel))

# =============================
# Exibir frase
# =============================
pergunta_en, resposta_en, pergunta_pt, resposta_pt = st.session_state.frase_atual
st.subheader("Frase para treinar:")
if nivel == "Fácil":
    st.markdown(f"**EN:** {pergunta_en}\n\n*PT:* {pergunta_pt}")
else:
    st.markdown(f"**EN:** {pergunta_en}")
    if nivel == "Médio":
        if st.checkbox("👁️ Mostrar tradução"):
            st.markdown(f"*PT:* {pergunta_pt}")

with st.expander("💡 Resposta sugerida"):
    st.markdown(f"**EN:** {resposta_en}\n\n*PT:* {resposta_pt}")
    if st.button("🔊 Ouvir resposta (EN)", key="audio_resposta"):
        st.markdown(gerar_audio(resposta_en), unsafe_allow_html=True)

# =============================
# Opção de áudio da pergunta
# =============================
if st.button("🔊 Ouvir pergunta (EN)", key="audio_pergunta"):
    st.markdown(gerar_audio(pergunta_en), unsafe_allow_html=True)

# =============================
# Responder por texto
# =============================
resposta_usuario = st.text_input("Digite sua resposta em inglês:", value=st.session_state.resposta_usuario, key="resposta_texto")
if st.button("✅ Verificar resposta (texto)", key="verificar_texto"):
    status, msg, inc, sim = verificar_texto(resposta_usuario, resposta_en)
    st.session_state.score += inc
    st.session_state.streak = st.session_state.streak+1 if inc else 0
    st.session_state.history.append({
        "nivel": nivel,
        "pergunta": pergunta_en,
        "resposta_correta": resposta_en,
        "resposta_usuario": resposta_usuario,
        "resultado": status,
        "similaridade": round(sim, 2)
    })
    if status != "success":
        st.session_state.difficult_words[resposta_en] = st.session_state.difficult_words.get(resposta_en, 0) + 1
    save_user_progress(progress)
    if status == "success": st.success(msg)
    elif status == "info": st.info(msg)
    elif status == "warn": st.warning(msg)
    else: st.error(msg)

# =============================
# Responder por áudio
# =============================
st.divider()
st.markdown("### 🎙️ Responder falando")
audio_bytes = audio_recorder(sample_rate=44100, text="🎤 Gravar / Parar")
if audio_bytes and st.button("🗣️ Transcrever e verificar", key="verificar_audio"):
    transcrito = transcrever_wav_bytes(audio_bytes)
    if not transcrito:
        st.warning("Não entendi o áudio, tente novamente.")
    else:
        st.write(f"Você disse: **{transcrito}**")
        status, msg, inc, sim = verificar_texto(transcrito, resposta_en)
        st.session_state.score += inc
        st.session_state.streak = st.session_state.streak+1 if inc else 0
        st.session_state.history.append({
            "nivel": nivel,
            "pergunta": pergunta_en,
            "resposta_correta": resposta_en,
            "resposta_usuario": transcrito,
            "resultado": status,
            "similaridade": round(sim, 2)
        })
        if status != "success":
            st.session_state.difficult_words[resposta_en] = st.session_state.difficult_words.get(resposta_en, 0) + 1
        save_user_progress(progress)
        if status == "success": st.success(msg)
        elif status == "info": st.info(msg)
        else: st.error(msg)

# =============================
# Próxima frase
# =============================
if st.button("➡ Próxima", key="proxima_frase"):
    if st.session_state.difficult_words and random.random() < 0.3:
        alvo = random.choice(list(st.session_state.difficult_words.keys()))
        for f in escolher_banco(nivel):
            if f[1] == alvo:
                st.session_state.frase_atual = f
                break
    else:
        st.session_state.frase_atual = random.choice(escolher_banco(nivel))
    st.session_state.resposta_usuario = ""  # limpa input

# =============================
# Vocabulário
# =============================
st.divider()
st.markdown("## 📖 Vocabulário por tópicos")
topico = st.selectbox("Escolha um tópico:", list(vocabulario.keys()), key="select_topico")
palavras = vocabulario[topico]

index = st.session_state.voc_index
palavra_atual = palavras[index]
st.markdown(f"PT: {palavra_atual['pt']}\nEN: {palavra_atual['en']}")
if st.button("🔊 Ouvir palavra", key="audio_palavra"):
    st.markdown(gerar_audio(palavra_atual['en']), unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    if st.button("⬅ Anterior", key="voc_ant"):
        st.session_state.voc_index = max(0, st.session_state.voc_index - 1)
with col2:
    if st.button("➡ Próxima", key="voc_prox"):
        st.session_state.voc_index = min(len(palavras)-1, st.session_state.voc_index + 1)

# =============================
# Histórico
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
        for w, c in st.session_state.difficult_words.items():
            st.write(f"- {w} (erros: {c})")
    else:
        st.write("Nenhuma por enquanto 🚀")

st.success(f"Pontuação: {st.session_state.score} | 🔥 Streak: {st.session_state.streak}")
