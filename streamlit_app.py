import streamlit as st
import random
import base64
import os
import re
import unicodedata
import difflib
import time
from tempfile import NamedTemporaryFile
from gtts import gTTS
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder
import pandas as pd
from streamlit_webrtc import webrtc_streamer

# =============================
# Configuração da página
# =============================
st.set_page_config(page_title="Treino de Inglês - Almoxarifado", page_icon="📦", layout="centered")

st.title("📦 English Dialogue Trainer – Almoxarifado")
st.caption("Perguntas e respostas aparecem em **inglês** com **tradução para português** (conforme o nível).")

# =============================
# Banco de frases por nível
# (EN pergunta, EN resposta, PT pergunta, PT resposta)
# =============================
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

# =============================
# Utilidades
# =============================
def gerar_audio(texto, lang="en"):
    """Gera um <audio> HTML com autoplay desativado (somente player) a partir de texto usando gTTS."""
    tts = gTTS(text=texto, lang=lang)
    filename = "voz.mp3"
    tts.save(filename)
    with open(filename, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    try:
        os.remove(filename)
    except Exception:
        pass
    # Sem autoplay!
    return f'<audio controls src="data:audio/mp3;base64,{b64}"></audio>'

def normalizar(txt: str) -> str:
    """Lowercase, remove acentos, pontuação e espaços extras para comparar."""
    txt = txt.strip().lower()
    txt = "".join(c for c in unicodedata.normalize("NFKD", txt) if not unicodedata.combining(c))
    txt = re.sub(r"[^a-z0-9']+", " ", txt)
    return " ".join(txt.split())

def similaridade(a: str, b: str) -> float:
    """0..1: quão parecidas são as strings normalizadas."""
    return difflib.SequenceMatcher(None, normalizar(a), normalizar(b)).ratio()

def classificar_erro(user: str, correct: str) -> str:
    """
    Heurística simples para detalhar feedback:
    - sim >= 0.90: bem próximo (talvez pontuação)
    - 0.80–0.89: pequeno erro de palavra/artigo/plural/ordem
    - 0.60–0.79: diferença moderada (possível problema de pronúncia na fala)
    - < 0.60: diferença grande (recomenda praticar novamente)
    """
    sim = similaridade(user, correct)
    if sim >= 0.90:
        return f"Quase perfeito (similaridade {sim*100:.0f}%). Revise pontuação/capot. mínimas."
    if sim >= 0.80:
        return f"Pequeno erro (similaridade {sim*100:.0f}%). Cheque artigos, plural ou ordem."
    if sim >= 0.60:
        return f"Diferença moderada (similaridade {sim*100:.0f}%). Se foi por voz, pode ter sido pronúncia."
    return f"Bem diferente (similaridade {sim*100:.0f}%). Refaça devagar e compare com o gabarito."

def verificar_texto(resposta_usuario: str, resposta_correta: str):
    """Retorna (status, msg, inc, sim)"""
    if not resposta_usuario.strip():
        return ("warn", "Digite sua resposta ou use o microfone.", 0, 0.0)
    if normalizar(resposta_usuario) == normalizar(resposta_correta):
        return ("success", "✅ Correto!", 1, 1.0)
    sim = similaridade(resposta_usuario, resposta_correta)
    if sim >= 0.80:
        return ("info", classificar_erro(resposta_usuario, resposta_correta), 0, sim)
    return ("error", classificar_erro(resposta_usuario, resposta_correta), 0, sim)

def transcrever_wav_bytes(wav_bytes: bytes, language="en-US") -> str | None:
    """Transcreve bytes WAV usando Google Web Speech (via SpeechRecognition)."""
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

def escolher_banco(nivel: str):
    return nivel_facil if nivel == "Fácil" else nivel_medio if nivel == "Médio" else nivel_dificil

# =============================
# Estado da Sessão
# =============================
if "nivel" not in st.session_state:
    st.session_state.nivel = "Fácil"

if "frase_atual" not in st.session_state:
    st.session_state.frase_atual = random.choice(nivel_facil)

if "score" not in st.session_state:
    st.session_state.score = 0
if "total" not in st.session_state:
    st.session_state.total = 0
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "best_streak" not in st.session_state:
    st.session_state.best_streak = 0
if "high_score" not in st.session_state:
    st.session_state.high_score = 0
if "history" not in st.session_state:
    st.session_state.history = []  # lista de dicts
if "goal" not in st.session_state:
    st.session_state.goal = 10  # meta de tentativas p/ progresso
if "mostrar_traducao" not in st.session_state:
    st.session_state.mostrar_traducao = True  # usado no Médio
if "timer_deadline" not in st.session_state:
    st.session_state.timer_deadline = None
if "timer_active" not in st.session_state:
    st.session_state.timer_active = False
if "ultimo_resultado" not in st.session_state:
    st.session_state.ultimo_resultado = None  # para o botão Refazer (re-exibir feedback)
if "autorefresh_key" not in st.session_state:
    st.session_state.autorefresh_key = "timer_refresh"

# =============================
# Barra superior de controle
# =============================
col_a, col_b, col_c = st.columns([1, 1, 1], vertical_alignment="center")
with col_a:
    nivel = st.selectbox("Selecione o nível:", ["Fácil", "Médio", "Difícil"], index=["Fácil","Médio","Difícil"].index(st.session_state.nivel))
with col_b:
    st.session_state.goal = st.number_input("Meta (tentativas):", min_value=5, max_value=100, value=st.session_state.goal, step=5)
with col_c:
    if st.button("🔄 Resetar sessão"):
        for k in ["score","total","streak","best_streak","history","high_score","ultimo_resultado"]:
            st.session_state[k] = 0 if k != "history" and k != "ultimo_resultado" else ([] if k=="history" else None)
        st.session_state.frase_atual = random.choice(escolher_banco(nivel))
        st.session_state.nivel = nivel
        st.session_state.timer_active = False
        st.session_state.timer_deadline = None
        st.rerun()

# Troca de nível -> nova frase + ajustes de tradução/temporizador
if nivel != st.session_state.nivel:
    st.session_state.nivel = nivel
    st.session_state.frase_atual = random.choice(escolher_banco(nivel))
    # Médio: tradução pode ser ocultada por botão
    st.session_state.mostrar_traducao = (nivel == "Fácil")
    # Difícil: inicia timer por frase
    st.session_state.timer_active = (nivel == "Difícil")
    st.session_state.timer_deadline = time.time() + 20 if st.session_state.timer_active else None
    st.session_state.ultimo_resultado = None
    st.rerun()

banco = escolher_banco(st.session_state.nivel)
pergunta_en, resposta_en, pergunta_pt, resposta_pt = st.session_state.frase_atual

# =============================
# Progresso & Estatísticas
# =============================
progress = min(1.0, st.session_state.total / st.session_state.goal) if st.session_state.goal > 0 else 0.0
st.progress(progress, text=f"Progresso: {int(progress*100)}% | Tentativas: {st.session_state.total}/{st.session_state.goal}")

stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
stats_col1.metric("✅ Pontos", st.session_state.score)
stats_col2.metric("🔥 Streak", st.session_state.streak)
stats_col3.metric("🏅 Melhor Streak", st.session_state.best_streak)
stats_col4.metric("🏆 Recorde", st.session_state.high_score)

# Badges simples
badges = []
if st.session_state.best_streak >= 3: badges.append("🔥 3 Streak")
if st.session_state.best_streak >= 5: badges.append("⚡ 5 Streak")
if st.session_state.score >= 10: badges.append("🎯 10 Pontos")
if badges:
    st.write("**Conquistas:** " + " | ".join(badges))

st.divider()

# =============================
# Exibição da frase e resposta (EN + PT conforme nível)
# =============================
st.subheader("Frase para treinar / Training prompt")
st.markdown(f"**EN:** {pergunta_en}  \n*PT:* {pergunta_pt}" if st.session_state.nivel == "Fácil"
            else f"**EN:** {pergunta_en}  \n" + (f"*PT:* {pergunta_pt}" if (st.session_state.nivel=="Médio" and st.session_state.mostrar_traducao) else "_PT oculto_"))

# Botão para mostrar/ocultar (apenas no nível Médio)
if st.session_state.nivel == "Médio":
    if st.button(("👁️ Ocultar tradução" if st.session_state.mostrar_traducao else "👁️ Mostrar tradução")):
        st.session_state.mostrar_traducao = not st.session_state.mostrar_traducao
        st.rerun()

# Resposta sugerida (sempre existe EN + PT, mas PT oculto no Difícil)
with st.expander("💡 Ver resposta sugerida / Suggested answer", expanded=(st.session_state.nivel=="Fácil")):
    if st.session_state.nivel == "Difícil":
        st.markdown(f"**EN:** {resposta_en}\n\n_PT oculto no nível Difícil_")
    elif st.session_state.nivel == "Médio" and not st.session_state.mostrar_traducao:
        st.markdown(f"**EN:** {resposta_en}\n\n_PT oculto_")
    else:
        st.markdown(f"**EN:** {resposta_en}  \n*PT:* {resposta_pt}")

# Players de áudio manuais (sem autoplay)
audio_col1, audio_col2 = st.columns(2)
with audio_col1:
    if st.button("🔊 Ouvir pergunta (EN)"):
        st.markdown(gerar_audio(pergunta_en, "en"), unsafe_allow_html=True)
with audio_col2:
    if st.button("🔊 Ouvir resposta (EN)"):
        st.markdown(gerar_audio(resposta_en, "en"), unsafe_allow_html=True)

# =============================
# Timer (somente nível Difícil)
# =============================
if st.session_state.nivel == "Difícil":
    if not st.session_state.timer_deadline:
        st.session_state.timer_deadline = time.time() + 20
        st.session_state.timer_active = True
    remaining = max(0, int(st.session_state.timer_deadline - time.time()))
    st.info(f"⏱️ Tempo restante: **{remaining}s**")
    # Atualiza a tela para contar
    st.autorefresh(interval=1000, key=st.session_state.autorefresh_key)
    if remaining == 0 and st.session_state.timer_active:
        # Tempo esgotado -> conta como erro (uma vez)
        st.session_state.timer_active = False
        st.session_state.total += 1
        st.session_state.streak = 0
        st.warning("⏳ Tempo esgotado! Veja a resposta correta no painel acima e tente novamente.")
        # registrar no histórico
        st.session_state.history.append({
            "timestamp": pd.Timestamp.now().strftime("%H:%M:%S"),
            "nivel": st.session_state.nivel,
            "pergunta_en": pergunta_en,
            "resposta_correta_en": resposta_en,
            "sua_resposta": "(tempo esgotado)",
            "resultado": "tempo",
            "similaridade": 0.0
        })

st.divider()

# =============================
# Resposta por TEXTO
# =============================
st.markdown("### ✍️ Responder digitando / Type your answer")
resposta_usuario = st.text_input("Digite sua resposta em inglês / Type your answer in English:")

text_cols = st.columns([1,1,1])
with text_cols[0]:
    verificar_texto_btn = st.button("✅ Verificar (texto)")
with text_cols[1]:
    refazer_btn = st.button("↩️ Refazer (mesma frase)")
with text_cols[2]:
    proxima_btn = st.button("➡ Próxima frase")

if verificar_texto_btn:
    status, msg, inc, sim = verificar_texto(resposta_usuario, resposta_en)
    st.session_state.total += 1
    st.session_state.score += inc
    if inc == 1:
        st.session_state.streak += 1
        st.session_state.best_streak = max(st.session_state.best_streak, st.session_state.streak)
    else:
        st.session_state.streak = 0
    st.session_state.high_score = max(st.session_state.high_score, st.session_state.score)

    if status == "success":
        st.success(msg)
    elif status == "info":
        st.info(msg)
    elif status == "warn":
        st.warning(msg)
    else:
        st.error(msg)

    # histórico
    st.session_state.history.append({
        "timestamp": pd.Timestamp.now().strftime("%H:%M:%S"),
        "nivel": st.session_state.nivel,
        "pergunta_en": pergunta_en,
        "resposta_correta_en": resposta_en,
        "sua_resposta": resposta_usuario,
        "resultado": status,
        "similaridade": round(sim, 3)
    })
    st.session_state.ultimo_resultado = (status, msg, inc, sim)

    # Reinicia timer no Difícil
    if st.session_state.nivel == "Difícil":
        st.session_state.timer_deadline = time.time() + 20
        st.session_state.timer_active = True

# =============================
# Resposta por ÁUDIO
# =============================
st.divider()
st.markdown("### 🎙️ Responder falando / Speak your answer")
st.caption("Clique em gravar, depois em **Transcrever e verificar**.")

audio_bytes = audio_recorder(sample_rate=44100, pause_threshold=2.0, text="🎙️ Gravar / Parar")

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    if st.button("🗣️ Transcrever e verificar (áudio)"):
        transcrito = transcrever_wav_bytes(audio_bytes, language="en-US")
        if not transcrito:
            st.warning("Não consegui entender o áudio. Tente falar mais perto do microfone.")
        else:
            st.write(f"**Você disse / You said:** _{transcrito}_")
            status, msg, inc, sim = verificar_texto(transcrito, resposta_en)
            st.session_state.total += 1
            st.session_state.score += inc
            if inc == 1:
                st.session_state.streak += 1
                st.session_state.best_streak = max(st.session_state.best_streak, st.session_state.streak)
            else:
                st.session_state.streak = 0
            st.session_state.high_score = max(st.session_state.high_score, st.session_state.score)

            if status == "success":
                st.success(msg)
            elif status == "info":
                st.info(msg)
            elif status == "warn":
                st.warning(msg)
            else:
                st.error(msg)

            # histórico
            st.session_state.history.append({
                "timestamp": pd.Timestamp.now().strftime("%H:%M:%S"),
                "nivel": st.session_state.nivel,
                "pergunta_en": pergunta_en,
                "resposta_correta_en": resposta_en,
                "sua_resposta": transcrito,
                "resultado": status,
                "similaridade": round(sim, 3)
            })
            st.session_state.ultimo_resultado = (status, msg, inc, sim)

            # Reinicia timer no Difícil
            if st.session_state.nivel == "Difícil":
                st.session_state.timer_deadline = time.time() + 20
                st.session_state.timer_active = True

# =============================
# Botões Refazer / Próxima
# =============================
if refazer_btn:
    # Mantém a mesma frase; zera só o resultado mostrado
    st.info("Refazendo a mesma frase. Tente novamente!")
    # Reinicia timer no Difícil
    if st.session_state.nivel == "Difícil":
        st.session_state.timer_deadline = time.time() + 20
        st.session_state.timer_active = True

if proxima_btn:
    st.session_state.frase_atual = random.choice(banco)
    # Ajusta visibilidade de tradução
    if st.session_state.nivel == "Fácil":
        st.session_state.mostrar_traducao = True
    elif st.session_state.nivel == "Médio":
        # mantém a preferência atual do usuário
        st.session_state.mostrar_traducao = st.session_state.mostrar_traducao
    else:
        st.session_state.mostrar_traducao = False
    # Reinicia timer no Difícil
    if st.session_state.nivel == "Difícil":
        st.session_state.timer_deadline = time.time() + 20
        st.session_state.timer_active = True
    st.session_state.ultimo_resultado = None
    st.rerun()

st.divider()

# =============================
# Histórico de respostas
# =============================
st.markdown("## 🧾 Histórico / History")
if len(st.session_state.history) == 0:
    st.write("Sem registros ainda. Faça uma tentativa! 😉")
else:
    df = pd.DataFrame(st.session_state.history)
    # Pequena formatação
    df_view = df[["timestamp","nivel","pergunta_en","sua_resposta","resposta_correta_en","resultado","similaridade"]]
    st.dataframe(df_view, use_container_width=True, hide_index=True)

    # Pequeno sumário
    acertos = sum(1 for h in st.session_state.history if h["resultado"] == "success")
    erros = sum(1 for h in st.session_state.history if h["resultado"] in ("error","tempo"))
    quase = sum(1 for h in st.session_state.history if h["resultado"] == "info")
    st.write(f"**Resumo:** ✅ {acertos} | ⚠️ {quase} | ❌ {erros}")

st.divider()

# =============================
# Rodapé
# =============================
st.success(f"Pontuação: {st.session_state.score}/{st.session_state.total} | 🔥 Streak: {st.session_state.streak} | 🏅 Melhor: {st.session_state.best_streak} | 🏆 Recorde: {st.session_state.high_score}")
st.caption("Dica: no **Médio**, use o botão para mostrar/ocultar a tradução. No **Difícil**, tente responder sem ajuda.")
