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
from datetime import datetime, timedelta
import time

# ============================================
# PREMIUM DESIGN SYSTEM - CSS INJECTION
# ============================================

def inject_custom_css():
    """Inject premium CSS styling into Streamlit"""
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        font-family: 'Inter', sans-serif;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0f172a; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #6366f1; }

    /* Premium Cards */
    .premium-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
    }
    .premium-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15);
        transform: translateY(-2px);
    }

    /* Typography */
    .premium-title {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 2.5rem;
        background: linear-gradient(135deg, #fff 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 8px;
        letter-spacing: -0.02em;
    }
    .premium-subtitle {
        font-family: 'Inter', sans-serif;
        font-weight: 400;
        font-size: 1.1rem;
        color: #94a3b8;
        margin-bottom: 32px;
    }
    .premium-heading {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.5rem;
        color: #f8fafc;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    /* Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .badge-primary {
        background: rgba(99, 102, 241, 0.2);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    .badge-success {
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .badge-warning {
        background: rgba(245, 158, 11, 0.2);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .badge-danger {
        background: rgba(239, 68, 68, 0.2);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    /* Buttons */
    .premium-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        padding: 12px 24px;
        border-radius: 12px;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.95rem;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
    }
    .premium-btn-primary {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4);
    }
    .premium-btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.6);
    }
    .premium-btn-secondary {
        background: rgba(255, 255, 255, 0.1);
        color: #f8fafc;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .premium-btn-success {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        box-shadow: 0 4px 16px rgba(16, 185, 129, 0.4);
    }

    /* Stats */
    .stat-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .stat-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        background: rgba(30, 41, 59, 0.7);
    }
    .stat-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2rem;
        font-weight: 700;
        color: #818cf8;
        line-height: 1;
    }
    .stat-label {
        font-size: 0.875rem;
        color: #64748b;
        margin-top: 8px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Progress */
    .progress-container {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 9999px;
        height: 8px;
        overflow: hidden;
        margin: 12px 0;
    }
    .progress-fill {
        height: 100%;
        border-radius: 9999px;
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        transition: width 0.6s ease;
    }

    /* XP Bar */
    .xp-container {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 16px 20px;
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .level-badge {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 1.25rem;
        color: white;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
        flex-shrink: 0;
    }

    /* Feedback */
    .feedback-success {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%);
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-radius: 12px;
        padding: 16px;
        color: #34d399;
    }
    .feedback-error {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.15) 100%);
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-radius: 12px;
        padding: 16px;
        color: #f87171;
    }
    .feedback-info {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(37, 99, 235, 0.15) 100%);
        border: 1px solid rgba(59, 130, 246, 0.4);
        border-radius: 12px;
        padding: 16px;
        color: #60a5fa;
    }

    /* Vocab Card */
    .vocab-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(51, 65, 85, 0.9) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 32px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .vocab-word {
        font-size: 2rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 8px;
    }
    .vocab-translation {
        font-size: 1.25rem;
        color: #94a3b8;
    }

    /* Animations */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    .animate-fade-in {
        animation: fadeInUp 0.6s ease forwards;
    }

    /* Streak */
    .streak-flame {
        font-size: 2rem;
        animation: flicker 1s ease-in-out infinite alternate;
    }
    @keyframes flicker {
        0% { transform: scale(1) rotate(-2deg); }
        100% { transform: scale(1.1) rotate(2deg); }
    }

    /* Divider */
    .premium-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.3), transparent);
        margin: 24px 0;
        border: none;
    }

    /* Streamlit overrides */
    .stTextInput > div > div > input {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
        padding: 14px 18px !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #818cf8 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
    }
    .stSelectbox > div > div > div {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
    }
    .stCheckbox > label {
        color: #94a3b8 !important;
    }
    .stRadio > div {
        background: transparent !important;
    }
    .stRadio > div > label {
        color: #f8fafc !important;
    }
    .stDataFrame {
        background: rgba(30, 41, 59, 0.5) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ============================================
# DATA & STATE MANAGEMENT
# ============================================

USER_DATA_FILE = "user_progress.json"

# Premium level system
LEVELS = {
    1: {"name": "Novice", "icon": "🌱", "xp_needed": 0},
    2: {"name": "Clerk", "icon": "📋", "xp_needed": 100},
    3: {"name": "Supervisor", "icon": "👔", "xp_needed": 300},
    4: {"name": "Manager", "icon": "💼", "xp_needed": 600},
    5: {"name": "Director", "icon": "👑", "xp_needed": 1000},
    6: {"name": "Executive", "icon": "🏆", "xp_needed": 1500},
}

ACHIEVEMENTS = {
    "first_blood": {"name": "First Steps", "desc": "Complete your first exercise", "icon": "🎯"},
    "perfect_streak_5": {"name": "On Fire", "desc": "5 correct answers in a row", "icon": "🔥"},
    "perfect_streak_10": {"name": "Unstoppable", "desc": "10 correct answers in a row", "icon": "⚡"},
    "vocab_50": {"name": "Word Collector", "desc": "Learn 50 vocabulary words", "icon": "📚"},
    "vocab_100": {"name": "Lexicon Master", "desc": "Learn 100 vocabulary words", "icon": "🎓"},
    "week_warrior": {"name": "Week Warrior", "desc": "7-day streak", "icon": "📅"},
    "audio_master": {"name": "Voice Master", "desc": "Use audio 10 times", "icon": "🎙️"},
}


def load_user_progress():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            data = {}
        
        # Ensure all premium fields exist with proper types
        data.setdefault("acertos", {})
        data.setdefault("erros", {})
        data.setdefault("xp", 0)
        data.setdefault("level", 1)
        data.setdefault("achievements", [])
        data.setdefault("streak", 0)
        data.setdefault("last_active", datetime.now().isoformat())
        data.setdefault("total_exercises", 0)
        data.setdefault("audio_used", 0)
        # BUG FIX: store vocab_seen as list (JSON-compatible) instead of set
        if "vocab_seen" not in data:
            data["vocab_seen"] = []
        elif isinstance(data["vocab_seen"], set):
            data["vocab_seen"] = list(data["vocab_seen"])
        return data
    
    return {
        "acertos": {}, "erros": {},
        "xp": 0, "level": 1, "achievements": [],
        "streak": 0, "last_active": datetime.now().isoformat(),
        "total_exercises": 0, "audio_used": 0, "vocab_seen": []
    }


def save_user_progress(data):
    data["last_active"] = datetime.now().isoformat()
    # Ensure vocab_seen is always a list before saving
    if isinstance(data.get("vocab_seen"), set):
        data["vocab_seen"] = list(data["vocab_seen"])
    try:
        with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except IOError as e:
        st.error(f"Erro ao salvar progresso: {e}")


def get_level_info(xp):
    current_level = 1
    for lvl, info in sorted(LEVELS.items(), reverse=True):
        if xp >= info["xp_needed"]:
            current_level = lvl
            break
    next_level = current_level + 1 if current_level < max(LEVELS.keys()) else current_level
    xp_for_next = LEVELS.get(next_level, {}).get("xp_needed", LEVELS[current_level]["xp_needed"] + 500)
    xp_current = LEVELS[current_level]["xp_needed"]
    progress = (xp - xp_current) / (xp_for_next - xp_current) if xp_for_next > xp_current else 1.0
    return current_level, next_level, xp_current, xp_for_next, progress


def check_achievements(progress, session_state):
    new_achievements = []
    total_correct = sum(progress["acertos"].values())

    if total_correct >= 1 and "first_blood" not in progress["achievements"]:
        new_achievements.append("first_blood")
    if session_state.get("streak", 0) >= 5 and "perfect_streak_5" not in progress["achievements"]:
        new_achievements.append("perfect_streak_5")
    if session_state.get("streak", 0) >= 10 and "perfect_streak_10" not in progress["achievements"]:
        new_achievements.append("perfect_streak_10")
    vocab_seen_count = len(progress.get("vocab_seen", []))
    if vocab_seen_count >= 50 and "vocab_50" not in progress["achievements"]:
        new_achievements.append("vocab_50")
    if vocab_seen_count >= 100 and "vocab_100" not in progress["achievements"]:
        new_achievements.append("vocab_100")
    if progress.get("audio_used", 0) >= 10 and "audio_master" not in progress["achievements"]:
        new_achievements.append("audio_master")

    for ach in new_achievements:
        progress["achievements"].append(ach)

    return new_achievements


# ============================================
# SAMPLE DATA (for demo purposes)
# ============================================

SAMPLE_FRASES = {
    "Fácil": [
        {"pergunta_en": "Where is the packing list?", "resposta_en": "It is on the desk.", 
         "pergunta_pt": "Onde está a lista de embalagem?", "resposta_pt": "Está na mesa."},
        {"pergunta_en": "Can I help you?", "resposta_en": "Yes, I need the inventory report.", 
         "pergunta_pt": "Posso ajudar?", "resposta_pt": "Sim, preciso do relatório de inventário."},
        {"pergunta_en": "What time does the shift start?", "resposta_en": "It starts at 8 AM.", 
         "pergunta_pt": "Que horas começa o turno?", "resposta_pt": "Começa às 8h."},
        {"pergunta_en": "Is the shipment ready?", "resposta_en": "Yes, it is ready for dispatch.", 
         "pergunta_pt": "A remessa está pronta?", "resposta_pt": "Sim, está pronta para despacho."},
    ],
    "Médio": [
        {"pergunta_en": "Could you verify the quantity against the purchase order?", 
         "resposta_en": "I will check the items and update the system.", 
         "pergunta_pt": "Pode verificar a quantidade contra a ordem de compra?", 
         "resposta_pt": "Vou conferir os itens e atualizar o sistema."},
        {"pergunta_en": "How do we handle damaged goods in receiving?", 
         "resposta_en": "We document the damage and notify the supplier immediately.", 
         "pergunta_pt": "Como lidamos com mercadorias danificadas no recebimento?", 
         "resposta_pt": "Documentamos o dano e notificamos o fornecedor imediatamente."},
        {"pergunta_en": "What is the procedure for cycle counting?", 
         "resposta_en": "We count a portion of inventory daily and reconcile discrepancies.", 
         "pergunta_pt": "Qual é o procedimento para contagem cíclica?", 
         "resposta_pt": "Contamos uma parte do inventário diariamente e reconciliamos discrepâncias."},
    ],
    "Difícil": [
        {"pergunta_en": "The FIFO method requires us to rotate stock based on receipt dates. Can you explain the process?", 
         "resposta_en": "First In, First Out means we ship the oldest inventory first to prevent obsolescence and ensure product freshness.", 
         "pergunta_pt": "O método PEPS exige que rotacionemos o estoque com base nas datas de recebimento. Pode explicar o processo?", 
         "resposta_pt": "Primeiro a Entrar, Primeiro a Sair significa que enviamos o estoque mais antigo primeiro para evitar obsolescência."},
        {"pergunta_en": "We have a discrepancy between the physical count and the WMS. How should we investigate?", 
         "resposta_en": "We should check for unprocessed transactions, misplaced items, and recent adjustments before conducting a recount.", 
         "pergunta_pt": "Temos uma discrepância entre a contagem física e o WMS. Como devemos investigar?", 
         "resposta_pt": "Devemos verificar transações não processadas, itens deslocados e ajustes recentes antes de refazer a contagem."},
    ]
}

SAMPLE_VOCAB = {
    "Warehouse Basics": [
        {"pt": "Prateleira", "en": "Shelf"},
        {"pt": "Empilhadeira", "en": "Forklift"},
        {"pt": "Inventário", "en": "Inventory"},
        {"pt": "Recebimento", "en": "Receiving"},
        {"pt": "Despacho", "en": "Dispatch"},
    ],
    "Shipping & Logistics": [
        {"pt": "Nota fiscal", "en": "Invoice"},
        {"pt": "Rastreamento", "en": "Tracking"},
        {"pt": "Frete", "en": "Freight"},
        {"pt": "Entrega", "en": "Delivery"},
        {"pt": "Transportadora", "en": "Carrier"},
    ],
    "Safety & Compliance": [
        {"pt": "Equipamento de proteção", "en": "PPE (Personal Protective Equipment)"},
        {"pt": "Risco", "en": "Hazard"},
        {"pt": "Inspeção", "en": "Inspection"},
        {"pt": "Conformidade", "en": "Compliance"},
        {"pt": "Acidente", "en": "Accident"},
    ],
    "Inventory Management": [
        {"pt": "Contagem cíclica", "en": "Cycle counting"},
        {"pt": "Ponto de pedido", "en": "Reorder point"},
        {"pt": "Estoque de segurança", "en": "Safety stock"},
        {"pt": "Obsolescência", "en": "Obsolescence"},
        {"pt": "SKU", "en": "Stock Keeping Unit"},
    ]
}

# ============================================
# UTILITY FUNCTIONS
# ============================================

def gerar_audio(texto, lang="en"):
    """Generate audio with error handling for network issues"""
    try:
        tts = gTTS(text=texto, lang=lang)
        filename = f"audio_{hash(texto)}.mp3"
        tts.save(filename)
        with open(filename, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        os.remove(filename)
        return f'<audio controls src="data:audio/mp3;base64,{b64}" style="width:100%;border-radius:8px;"></audio>'
    except Exception as e:
        return f'<div style="color:#f87171;padding:12px;border:1px solid rgba(239,68,68,0.4);border-radius:8px;">🔇 Erro ao gerar áudio: verifique sua conexão.</div>'


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
        return ("success", "Correto! Excelente trabalho!", 1, 1.0)
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
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        return None
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


# ============================================
# PREMIUM UI COMPONENTS
# ============================================

def render_header():
    """Render premium header with logo and navigation"""
    st.markdown("""
    <div style="display:flex;align-items:center;gap:16px;margin-bottom:32px;">
        <div style="width:56px;height:56px;border-radius:16px;background:linear-gradient(135deg,#6366f1,#8b5cf6);
                    display:flex;align-items:center;justify-content:center;font-size:28px;box-shadow:0 4px 16px rgba(99,102,241,0.4);">
            📦
        </div>
        <div>
            <div class="premium-title" style="font-size:1.75rem;">English Dialogue Trainer</div>
            <div style="color:#94a3b8;font-size:0.9rem;">Almoxarifado Profissional</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_stats_bar(progress, session_state):
    """Render premium stats bar with XP, level, streak"""
    level, next_level, xp_current, xp_next, xp_progress = get_level_info(progress["xp"])
    level_info = LEVELS[level]
    next_info = LEVELS.get(next_level, level_info)

    col1, col2, col3, col4 = st.columns([1.5, 2, 1, 1])

    with col1:
        st.markdown(f"""
        <div class="xp-container">
            <div class="level-badge">{level_info['icon']}</div>
            <div class="xp-info">
                <div style="font-weight:700;color:#f8fafc;">{level_info['name']}</div>
                <div class="xp-text">Nível {level}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="margin-top:8px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="font-size:0.875rem;color:#94a3b8;">XP: {progress['xp']}</span>
                <span style="font-size:0.875rem;color:#64748b;">{xp_next - progress['xp']} para {next_info['name']}</span>
            </div>
            <div class="progress-container">
                <div class="progress-fill" style="width:{xp_progress*100}%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        streak = session_state.get("streak", 0)
        flame = "🔥" if streak > 0 else "⚪"
        st.markdown(f"""
        <div class="stat-card">
            <div class="streak-flame">{flame}</div>
            <div class="stat-value" style="font-size:1.5rem;">{streak}</div>
            <div class="stat-label">Streak</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        score = session_state.get("score", 0)
        st.markdown(f"""
        <div class="stat-card">
            <div style="font-size:1.5rem;">⭐</div>
            <div class="stat-value" style="font-size:1.5rem;">{score}</div>
            <div class="stat-label">Score</div>
        </div>
        """, unsafe_allow_html=True)


def render_difficulty_selector(current_level):
    """Render premium difficulty selector using selectbox for reliability"""
    st.markdown("<div class='premium-heading'>🎯 Nível de Dificuldade</div>", unsafe_allow_html=True)
    
    difficulties = ["Fácil", "Médio", "Difícil"]
    
    col1, col2, col3 = st.columns(3)
    diff_cols = [col1, col2, col3]
    diff_icons = {"Fácil": "🌱", "Médio": "📋", "Difícil": "💼"}
    diff_desc = {"Fácil": "Iniciante", "Médio": "Intermediário", "Difícil": "Avançado"}
    
    # Display difficulty cards
    for i, diff in enumerate(difficulties):
        with diff_cols[i]:
            is_active = current_level == diff
            border_color = "rgba(99, 102, 241, 0.6)" if is_active else "rgba(99, 102, 241, 0.2)"
            bg_color = "rgba(99, 102, 241, 0.15)" if is_active else "rgba(30, 41, 59, 0.5)"
            st.markdown(f"""
            <div style="background:{bg_color};border:1px solid {border_color};border-radius:12px;
                        padding:16px;text-align:center;transition:all 0.3s ease;">
                <div style="font-size:2rem;margin-bottom:8px;">{diff_icons[diff]}</div>
                <div style="font-weight:700;color:#f8fafc;">{diff}</div>
                <div style="font-size:0.875rem;color:#94a3b8;">{diff_desc[diff]}</div>
            </div>
            """, unsafe_allow_html=True)
    
    nivel = st.radio("", difficulties, 
                     index=difficulties.index(current_level),
                     label_visibility="collapsed", key="difficulty_radio",
                     horizontal=True)
    return nivel


def render_phrase_card(frase, nivel):
    """Render premium phrase training card"""
    pergunta_en = frase["pergunta_en"]
    resposta_en = frase["resposta_en"]
    pergunta_pt = frase.get("pergunta_pt", "")
    resposta_pt = frase.get("resposta_pt", "")

    st.markdown("<div class='premium-heading'>💬 Diálogo para Treinar</div>", unsafe_allow_html=True)

    # Question card
    st.markdown(f"""
    <div class="premium-card premium-card-glow animate-fade-in">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
            <span class="badge badge-primary">🇺🇸 EN</span>
            <span style="color:#94a3b8;font-size:0.875rem;">Pergunta</span>
        </div>
        <div style="font-size:1.25rem;font-weight:600;color:#f8fafc;line-height:1.5;">
            {pergunta_en}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Translation toggle for Easy/Medium
    if nivel in ["Fácil", "Médio"]:
        show_trans = st.checkbox("👁️ Mostrar tradução", key="show_translation")
        if show_trans or nivel == "Fácil":
            st.markdown(f"""
            <div class="premium-card" style="border-color:rgba(16,185,129,0.3);">
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
                    <span class="badge badge-success">🇧🇷 PT</span>
                </div>
                <div style="color:#94a3b8;font-size:1.1rem;">
                    {pergunta_pt}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Answer section
    with st.expander("💡 Ver Resposta Sugerida"):
        st.markdown(f"""
        <div class="premium-card" style="background:rgba(16,185,129,0.1);border-color:rgba(16,185,129,0.3);">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
                <span class="badge badge-success">✅ Resposta</span>
            </div>
            <div style="font-size:1.15rem;font-weight:600;color:#34d399;margin-bottom:8px;">
                {resposta_en}
            </div>
            <div style="color:#94a3b8;font-size:0.95rem;">
                {resposta_pt}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔊 Ouvir Resposta", key="audio_resposta", use_container_width=True):
            audio_html = gerar_audio(resposta_en)
            st.markdown(audio_html, unsafe_allow_html=True)

    # Listen to question button
    if st.button("🔊 Ouvir Pergunta", key="audio_pergunta", use_container_width=True):
        audio_html = gerar_audio(pergunta_en)
        st.markdown(audio_html, unsafe_allow_html=True)

    return pergunta_en, resposta_en, resposta_pt


def render_text_input_section(resposta_en):
    """Render premium text input with verification"""
    st.markdown("<div class='premium-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='premium-heading'>✍️ Sua Resposta</div>", unsafe_allow_html=True)

    resposta_usuario = st.text_input("", 
                                     placeholder="Digite sua resposta em inglês...",
                                     key="resposta_texto",
                                     label_visibility="collapsed")

    col1, col2 = st.columns([1, 1])
    with col1:
        verify_clicked = st.button("✅ Verificar Resposta", key="verificar_texto", 
                                   use_container_width=True, type="primary")
    with col2:
        skip_clicked = st.button("⏭️ Pular", key="skip_texto", 
                                  use_container_width=True)

    return resposta_usuario, verify_clicked, skip_clicked


def render_feedback(status, msg, sim):
    """Render premium feedback messages"""
    if status == "success":
        st.markdown(f"""
        <div class="feedback-success animate-fade-in">
            <div style="display:flex;align-items:center;gap:12px;">
                <span style="font-size:1.5rem;">🎉</span>
                <div>
                    <div style="font-weight:700;font-size:1.1rem;">{msg}</div>
                    <div style="font-size:0.875rem;opacity:0.8;">+10 XP ganho!</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif status == "info":
        st.markdown(f"""
        <div class="feedback-info animate-fade-in">
            <div style="display:flex;align-items:center;gap:12px;">
                <span style="font-size:1.5rem;">💡</span>
                <div>
                    <div style="font-weight:700;font-size:1.1rem;">{msg}</div>
                    <div style="font-size:0.875rem;opacity:0.8;">+5 XP por tentativa</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif status == "error":
        st.markdown(f"""
        <div class="feedback-error animate-fade-in">
            <div style="display:flex;align-items:center;gap:12px;">
                <span style="font-size:1.5rem;">❌</span>
                <div>
                    <div style="font-weight:700;font-size:1.1rem;">{msg}</div>
                    <div style="font-size:0.875rem;opacity:0.8;">Tente novamente ou veja a resposta</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif status == "warn":
        st.warning(msg)


def render_audio_section(resposta_en):
    """Render premium audio recording section"""
    st.markdown("<div class='premium-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='premium-heading'>🎙️ Responder por Áudio</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="premium-card" style="text-align:center;">
        <div style="font-size:3rem;margin-bottom:12px;">🎤</div>
        <div style="color:#94a3b8;margin-bottom:16px;">Clique no microfone para gravar sua resposta</div>
    </div>
    """, unsafe_allow_html=True)

    audio_bytes = audio_recorder(sample_rate=44100, text="🎤 Gravar / Parar")

    if audio_bytes:
        if st.button("🗣️ Transcrever e Verificar", key="verificar_audio", use_container_width=True):
            with st.spinner("🔄 Processando áudio..."):
                transcrito = transcrever_wav_bytes(audio_bytes)

            if not transcrito:
                st.markdown("""
                <div class="feedback-error">
                    <div style="display:flex;align-items:center;gap:12px;">
                        <span style="font-size:1.5rem;">🔇</span>
                        <div>
                            <div style="font-weight:700;">Não entendi o áudio</div>
                            <div style="font-size:0.875rem;opacity:0.8;">Tente falar mais claramente ou em um ambiente mais silencioso</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="premium-card" style="border-color:rgba(99,102,241,0.3);">
                    <div style="color:#94a3b8;font-size:0.875rem;margin-bottom:8px;">Você disse:</div>
                    <div style="font-size:1.1rem;color:#f8fafc;font-weight:500;">{transcrito}</div>
                </div>
                """, unsafe_allow_html=True)
                return transcrito
    return None


def render_vocabulary_section(vocab_data, progress):
    """Render premium vocabulary section"""
    st.markdown("<div class='premium-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='premium-heading'>📖 Vocabulário por Tópicos</div>", unsafe_allow_html=True)

    topics = list(vocab_data.keys())
    topico = st.selectbox("", topics, key="select_topico", label_visibility="collapsed")

    palavras = vocab_data[topico]

    if "voc_index" not in st.session_state:
        st.session_state.voc_index = 0

    # Ensure index is within bounds
    st.session_state.voc_index = max(0, min(st.session_state.voc_index, len(palavras) - 1))
    
    index = st.session_state.voc_index
    palavra_atual = palavras[index]

    # Track seen vocabulary (use list for JSON compatibility)
    vocab_seen = progress.get("vocab_seen", [])
    if palavra_atual["en"] not in vocab_seen:
        vocab_seen.append(palavra_atual["en"])
        progress["vocab_seen"] = vocab_seen

    # Vocabulary card
    st.markdown(f"""
    <div class="vocab-card animate-fade-in">
        <div style="display:flex;justify-content:center;gap:8px;margin-bottom:24px;">
            <span class="badge badge-primary">{topico}</span>
            <span class="badge badge-success">{index + 1} / {len(palavras)}</span>
        </div>
        <div class="vocab-word">{palavra_atual['en']}</div>
        <div class="vocab-translation">{palavra_atual['pt']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Audio and navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🔊 Ouvir", key="audio_palavra", use_container_width=True):
            audio_html = gerar_audio(palavra_atual['en'])
            st.markdown(audio_html, unsafe_allow_html=True)
    with col2:
        if st.button("⬅ Anterior", key="voc_ant", use_container_width=True):
            st.session_state.voc_index = max(0, st.session_state.voc_index - 1)
            st.rerun()
    with col3:
        if st.button("➡ Próxima", key="voc_prox", use_container_width=True):
            st.session_state.voc_index = min(len(palavras) - 1, st.session_state.voc_index + 1)
            st.rerun()


def render_achievements(progress):
    """Render achievements section"""
    if not progress["achievements"]:
        return

    st.markdown("<div class='premium-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='premium-heading'>🏆 Conquistas</div>", unsafe_allow_html=True)

    cols = st.columns(3)
    for i, ach_id in enumerate(progress["achievements"]):
        ach = ACHIEVEMENTS.get(ach_id, {})
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:rgba(30,41,59,0.5);border:1px solid rgba(245,158,11,0.3);
                        border-radius:12px;padding:16px;text-align:center;margin-bottom:12px;">
                <div style="font-size:2rem;margin-bottom:8px;">{ach.get('icon', '🏅')}</div>
                <div style="font-weight:700;color:#fbbf24;font-size:0.95rem;">{ach.get('name', 'Unknown')}</div>
                <div style="font-size:0.8rem;color:#94a3b8;">{ach.get('desc', '')}</div>
            </div>
            """, unsafe_allow_html=True)


def render_history(history_data):
    """Render premium history table"""
    st.markdown("<div class='premium-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='premium-heading'>📊 Histórico</div>", unsafe_allow_html=True)

    if not history_data:
        st.markdown("""
        <div class="premium-card" style="text-align:center;padding:40px;">
            <div style="font-size:3rem;margin-bottom:12px;">📋</div>
            <div style="color:#94a3b8;">Nenhum registro ainda. Comece a praticar!</div>
        </div>
        """, unsafe_allow_html=True)
        return

    try:
        df = pd.DataFrame(history_data)
        st.dataframe(df, use_container_width=True, hide_index=True,
                    column_config={
                        "nivel": st.column_config.TextColumn("Nível", width="small"),
                        "pergunta": st.column_config.TextColumn("Pergunta", width="large"),
                        "resposta_usuario": st.column_config.TextColumn("Sua Resposta", width="large"),
                        "resultado": st.column_config.TextColumn("Resultado", width="small"),
                        "similaridade": st.column_config.ProgressColumn("Similaridade", 
                                                                       min_value=0, max_value=1, 
                                                                       format="%.0f%%", width="medium")
                    })
    except Exception:
        st.write(history_data)


def render_new_achievements(new_achs):
    """Render new achievement notifications"""
    for ach_id in new_achs:
        ach = ACHIEVEMENTS.get(ach_id, {})
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(245,158,11,0.2),rgba(251,191,36,0.2));
                    border:2px solid rgba(245,158,11,0.5);border-radius:16px;padding:20px;
                    margin-bottom:16px;animation:fadeInUp 0.6s ease;">
            <div style="display:flex;align-items:center;gap:16px;">
                <div style="font-size:3rem;">{ach.get('icon', '🏅')}</div>
                <div>
                    <div style="font-size:0.875rem;color:#fbbf24;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;">
                        NOVA CONQUISTA!
                    </div>
                    <div style="font-size:1.25rem;font-weight:700;color:#f8fafc;">{ach.get('name', 'Unknown')}</div>
                    <div style="color:#94a3b8;">{ach.get('desc', '')}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ============================================
# MAIN APPLICATION
# ============================================

def main():
    # Page configuration
    st.set_page_config(
        page_title="English Dialogue Trainer Pro",
        page_icon="📦",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    # Inject custom CSS
    inject_custom_css()

    # Initialize session state
    if "nivel" not in st.session_state: 
        st.session_state.nivel = "Fácil"
    if "frase_atual" not in st.session_state: 
        st.session_state.frase_atual = random.choice(SAMPLE_FRASES["Fácil"])
    if "score" not in st.session_state: 
        st.session_state.score = 0
    if "streak" not in st.session_state: 
        st.session_state.streak = 0
    if "history" not in st.session_state: 
        st.session_state.history = []
    if "difficult_words" not in st.session_state: 
        st.session_state.difficult_words = {}
    if "voc_index" not in st.session_state: 
        st.session_state.voc_index = 0
    if "resposta_usuario" not in st.session_state: 
        st.session_state.resposta_usuario = ""
    if "new_achievements" not in st.session_state:
        st.session_state.new_achievements = []

    # Load progress
    progress = load_user_progress()

    # Render header
    render_header()

    # Render stats bar
    render_stats_bar(progress, st.session_state)

    st.markdown("<div class='premium-divider'></div>", unsafe_allow_html=True)

    # Difficulty selector
    nivel = render_difficulty_selector(st.session_state.nivel)
    if nivel != st.session_state.nivel:
        st.session_state.nivel = nivel
        st.session_state.frase_atual = random.choice(SAMPLE_FRASES[nivel])
        st.rerun()

    # Render new achievements if any
    if st.session_state.new_achievements:
        render_new_achievements(st.session_state.new_achievements)
        st.session_state.new_achievements = []

    # Render phrase card
    frase = st.session_state.frase_atual
    pergunta_en, resposta_en, resposta_pt = render_phrase_card(frase, nivel)

    # Text input section
    resposta_usuario, verify_clicked, skip_clicked = render_text_input_section(resposta_en)

    if verify_clicked:
        status, msg, inc, sim = verificar_texto(resposta_usuario, resposta_en)

        # Update score and streak
        st.session_state.score += inc
        if inc:
            st.session_state.streak += 1
            progress["xp"] += 10
            progress["total_exercises"] += 1
        else:
            st.session_state.streak = 0
            if sim >= 0.75:
                progress["xp"] += 5
            st.session_state.difficult_words[resposta_en] = st.session_state.difficult_words.get(resposta_en, 0) + 1

        # Update history
        st.session_state.history.append({
            "nivel": nivel,
            "pergunta": pergunta_en,
            "resposta_correta": resposta_en,
            "resposta_usuario": resposta_usuario,
            "resultado": "✅" if status == "success" else "⚠️" if status == "info" else "❌",
            "similaridade": round(sim, 2)
        })

        # Check achievements
        new_achs = check_achievements(progress, st.session_state)
        if new_achs:
            st.session_state.new_achievements = new_achs

        # Save progress
        save_user_progress(progress)

        # Render feedback
        render_feedback(status, msg, sim)

        # Rerun to show updated stats
        if new_achs:
            st.rerun()

    # Audio section
    transcrito = render_audio_section(resposta_en)
    if transcrito:
        status, msg, inc, sim = verificar_texto(transcrito, resposta_en)

        st.session_state.score += inc
        if inc:
            st.session_state.streak += 1
            progress["xp"] += 10
            progress["audio_used"] = progress.get("audio_used", 0) + 1
        else:
            st.session_state.streak = 0
            if sim >= 0.75:
                progress["xp"] += 5

        st.session_state.history.append({
            "nivel": nivel,
            "pergunta": pergunta_en,
            "resposta_correta": resposta_en,
            "resposta_usuario": transcrito,
            "resultado": "✅" if status == "success" else "⚠️" if status == "info" else "❌",
            "similaridade": round(sim, 2)
        })

        new_achs = check_achievements(progress, st.session_state)
        if new_achs:
            st.session_state.new_achievements = new_achs

        save_user_progress(progress)
        render_feedback(status, msg, sim)

        if new_achs:
            st.rerun()

    # Next phrase button
    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
    if st.button("➡ Próxima Frase", key="proxima_frase", use_container_width=True):
        if st.session_state.difficult_words and random.random() < 0.3:
            alvo = random.choice(list(st.session_state.difficult_words.keys()))
            for f in SAMPLE_FRASES[nivel]:
                if f.get("resposta_en") == alvo or f.get("en") == alvo:
                    st.session_state.frase_atual = f
                    break
            else:
                st.session_state.frase_atual = random.choice(SAMPLE_FRASES[nivel])
        else:
            st.session_state.frase_atual = random.choice(SAMPLE_FRASES[nivel])
        st.session_state.resposta_usuario = ""
        st.rerun()

    # Vocabulary section
    render_vocabulary_section(SAMPLE_VOCAB, progress)

    # Achievements
    render_achievements(progress)

    # History
    render_history(st.session_state.history)

    # Footer
    st.markdown("""
    <div style="text-align:center;padding:32px 0;color:#64748b;font-size:0.875rem;">
        <div style="margin-bottom:8px;">📦 English Dialogue Trainer Pro</div>
        <div>Almoxarifado Profissional — v2.0 Premium</div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
