import streamlit as st
import random
from gtts import gTTS
import base64
import os

# ----------------------------
# Banco de frases por nível
# ----------------------------
nivel_facil = [
    ("Hi, how are you?", "I'm fine, thanks.", "Oi, como você está? → Estou bem, obrigado."),
    ("What’s your name?", "My name is John.", "Qual é o seu nome? → Meu nome é John."),
    ("Do you like coffee?", "Yes, I like coffee.", "Você gosta de café? → Sim, eu gosto de café."),
    ("Good morning!", "Good morning!", "Bom dia!"),
    ("Thank you!", "You're welcome.", "Obrigado! → De nada."),
    ("See you later!", "See you!", "Até mais! → Até logo."),
    ("Excuse me", "Yes?", "Com licença → Sim?"),
    ("I need help", "I can help you.", "Preciso de ajuda → Eu posso ajudar."),
    ("Where is the restroom?", "It is over there.", "Onde fica o banheiro? → Fica ali."),
    ("I am ready", "Great! Let's start.", "Estou pronto → Ótimo! Vamos começar."),
]

nivel_medio = [
    ("Where is the box?", "The box is on the table.", "Onde está a caixa? → A caixa está na mesa."),
    ("Can you help me?", "Yes, I can help you.", "Você pode me ajudar? → Sim, eu posso te ajudar."),
    ("Do you work here?", "Yes, I do.", "Você trabalha aqui? → Sim, eu trabalho aqui."),
    ("I need this item", "I will get it for you.", "Preciso deste item → Vou pegar para você."),
    ("Check the inventory", "I will check it now.", "Verifique o inventário → Vou verificar agora."),
    ("When will it arrive?", "Tomorrow morning.", "Quando vai chegar? → Amanhã de manhã."),
    ("Where can I find the supplies?", "They are in aisle 3.", "Onde posso encontrar os suprimentos? → No corredor 3."),
    ("Please sign here", "Okay, I will sign.", "Por favor, assine aqui → Ok, vou assinar."),
    ("The truck is here", "I will unload it.", "O caminhão chegou → Vou descarregar."),
    ("We need more boxes", "I will order them.", "Precisamos de mais caixas → Vou pedir."),
]

nivel_dificil = [
    ("Do we have this item in stock?", "Yes, we have it.", "Temos este item em estoque? → Sim, temos."),
    ("Please, sign the paper.", "Okay, I will sign.", "Por favor, assine o papel → Ok, eu vou assinar."),
    ("The truck just arrived.", "I will check it.", "O caminhão acabou de chegar → Eu vou verificar."),
    ("Where can I find the new supplies?", "They are in aisle 3.", "Onde posso encontrar os novos suprimentos? → Estão no corredor 3."),
    ("Check the inventory for today.", "I will check it now.", "Verifique o inventário de hoje → Vou verificar agora."),
    ("Can you organize the shelf?", "Yes, I will organize it.", "Pode organizar a prateleira → Sim, vou organizar."),
    ("We need to prepare the order", "I will prepare it.", "Precisamos preparar o pedido → Vou preparar."),
    ("Is this item damaged?", "No, it is fine.", "Este item está danificado? → Não, está ok."),
    ("Confirm the delivery", "I will confirm it.", "Confirme a entrega → Vou confirmar."),
    ("Update the stock list", "I will update it.", "Atualize a lista de estoque → Vou atualizar."),
]

# ----------------------------
# Função para gerar áudio
# ----------------------------
def gerar_audio(texto, lang="en"):
    tts = gTTS(text=texto, lang=lang)
    filename = "voz.mp3"
    tts.save(filename)
    with open(filename, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    os.remove(filename)
    return f'<audio autoplay controls src="data:audio/mp3;base64,{b64}"></audio>'

# ----------------------------
# Configurações Streamlit
# ----------------------------
st.set_page_config(page_title="Treino de Inglês - Almoxarifado", page_icon="📦")
st.title("📦 English Dialogue Trainer - Almoxarifado")

# Seleção de nível
nivel = st.selectbox("Selecione o nível:", ["Fácil", "Médio", "Difícil"])
banco = nivel_facil if nivel == "Fácil" else nivel_medio if nivel == "Médio" else nivel_dificil

# Sessão de estado
if "frase_atual" not in st.session_state:
    st.session_state.frase_atual = random.choice(banco)
    st.session_state.score = 0
    st.session_state.total = 0

pergunta, resposta_correta, traducao = st.session_state.frase_atual

st.subheader("Frase para treinar:")

# 👉 Exibição diferente dependendo do nível
if nivel == "Fácil":
    st.markdown(f"**{pergunta}**  \n*({traducao})*")
else:
    st.markdown(f"**{pergunta}**")

# Botão para ouvir a frase
if st.button("🔊 Ouvir frase em inglês"):
    st.markdown(gerar_audio(pergunta), unsafe_allow_html=True)

# Entrada de resposta
resposta_usuario = st.text_input("Digite sua resposta em inglês:")

if st.button("✅ Verificar resposta"):
    st.session_state.total += 1
    if resposta_usuario.strip().lower() == resposta_correta.lower():
        st.success("✅ Correto!")
        st.session_state.score += 1
        st.markdown(gerar_audio("Correct! Well done!", "en"), unsafe_allow_html=True)
    else:
        st.error(f"❌ Errado. Resposta correta: {resposta_correta}")
        st.markdown(gerar_audio("Not quite. Try again!", "en"), unsafe_allow_html=True)

    # 👉 Tradução aparece só depois da verificação nos níveis Médio/Difícil
    if nivel != "Fácil":
        st.info(f"Tradução: {traducao}")

# Botão para próxima frase
if st.button("➡ Próxima frase"):
    st.session_state.frase_atual = random.choice(banco)
    st.rerun()  # substitui experimental_rerun()

# Mostrar score
st.info(f"Pontuação: {st.session_state.score}/{st.session_state.total}")
