import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import google.generativeai as genai

# =========================
# CONFIGURAÇÕES INICIAIS
# =========================
st.set_page_config(
    page_title="Java — Funções na Prática",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuração da IA (Gemini)
GEMINI_KEY = st.secrets.get("app", {}).get("gemini_api_key")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash') 
else:
    model = None

STATUS_OPTS = ["✅ Consegui", "🟡 Parcial", "❌ Não consegui"]
DIF_OPTS = ["Muito fácil", "Fácil", "Médio", "Difícil"]
HELP_OPTS = ["Não", "Sim"]
TEACHER_PASS = st.secrets.get("app", {}).get("teacher_password")

LEVEL_ORDER = ["Fundamentos", "Condicionais", "Loops", "Funções com loop e condicional", "Desafiador"]
LEVEL_COLORS = {
    "Fundamentos": ("#E8F5E9", "#1B5E20"),
    "Condicionais": ("#E3F2FD", "#0D47A1"),
    "Loops": ("#FFF8E1", "#E65100"),
    "Funções com loop e condicional": ("#FCE4EC", "#880E4F"),
    "Desafiador": ("#F3E5F5", "#4A148C"),
}

FUNC_BADGE = {
    "sem parâmetro": "🟢 sem parâmetro",
    "com parâmetro": "🔹 com parâmetro",
    "com retorno": "🟣 com retorno",
    "void": "🟠 void",
    "condicional": "🔀 com condicional",
    "loop": "🔁 com loop",
    "combinada": "🧠 função combinada",
}

# =========================
# BANCO DE EXERCÍCIOS
# =========================
EXS = [
    {"id": "Ex 01", "title": "Mostrar mensagem", "level": "Fundamentos", "function_hint": "void", "skills": ["função", "void"], "goal": "Entender função sem retorno.", "prompt": "Crie uma função chamada mostrarMensagem() que exiba a frase 'Olá, Java!' usando JOptionPane.showMessageDialog."},
    {"id": "Ex 02", "title": "Retornar o dobro", "level": "Fundamentos", "function_hint": "com retorno", "skills": ["retorno", "parâmetro"], "goal": "Praticar parâmetro e retorno.", "prompt": "Crie uma função chamada calcularDobro(int numero) que retorne o dobro do valor."},
    {"id": "Ex 06", "title": "Verifica número par", "level": "Condicionais", "function_hint": "condicional", "skills": ["if", "módulo"], "goal": "Introduzir decisão.", "prompt": "Crie uma função chamada verificarPar(int numero) que retorne 'Par' ou 'Ímpar'."},
    {"id": "Ex 11", "title": "Soma de 1 até N", "level": "Loops", "function_hint": "loop", "skills": ["for", "acumulador"], "goal": "Introduzir repetição.", "prompt": "Crie uma função chamada somarAteN(int n) que retorne a soma de 1 até N."},
    {"id": "Ex 21", "title": "[Desafio] Calculadora", "level": "Desafiador", "function_hint": "combinada", "skills": ["menu", "funções"], "goal": "Várias funções.", "prompt": "Crie uma calculadora com funções separadas e menu via JOptionPane.showInputDialog."},
]
# ... Adicione os outros 25 exercícios aqui conforme a lista anterior ...
EXS = sorted(EXS, key=lambda x: x["id"])
LEVEL_COUNTS = {lvl: len([e for e in EXS if e['level'] == lvl]) for lvl in LEVEL_ORDER}

# =========================
# ESTILO E ANIMAÇÕES
# =========================
st.markdown("""<style>.block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1000px; } .hero { border-radius: 16px; padding: 24px; color: white; margin-bottom: 1.5rem; background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%); box-shadow: 0 8px 16px rgba(0,0,0,0.1); text-align: center; } .hero h1 { margin: 0 0 10px 0; font-size: 2.2rem; font-weight: 800; } .exercise-card { border-radius: 12px; padding: 24px; margin-top: 1rem; margin-bottom: 1rem; box-shadow: 0 4px 10px rgba(0,0,0,0.08); background: #ffffff; } .exercise-chip { display: inline-block; padding: 6px 12px; margin-right: 8px; margin-bottom: 8px; border-radius: 20px; font-size: 0.85rem; background: #f1f5f9; border: 1px solid #e2e8f0; color: #334155; font-weight: 600; } .ai-box { background-color: #f0fdf4; border-left: 6px solid #22c55e; padding: 16px; border-radius: 8px; margin-top: 10px; color: #166534; } .badge-card { background: #fffbeb; border: 2px solid #fbbf24; border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 10px;} .alert-box { background-color: #fee2e2; border-left: 6px solid #ef4444; color: #7f1d1d; padding: 12px 16px; border-radius: 8px; margin-bottom: 10px; font-weight: 500; }</style>""", unsafe_allow_html=True)

def exibir_animacao_alienigena(nivel):
    configs = {"Fundamentos": ("🛸 Missão base concluída!", "🛸", "fly-horizontal"), "Condicionais": ("👽 Nossos radares aprovam!", "👽", "pop-up"), "Loops": ("☄️ Loop estelar dominado!", "☄️", "spin-orbit"), "Funções com loop e condicional": ("👾 Invasão contida!", "👾", "zig-zag"), "Desafiador": ("🌌 Galáxia dominada!", "🚀", "abduction")}
    msg, emoji, anim_type = configs.get(nivel, ("🛸 Sucesso!", "🛸", "pop-up"))
    st.toast(msg, icon=emoji)
    css = f"""<style>.alien-container {{position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 150px; z-index: 99999; pointer-events: none;}} .fly-horizontal {{animation: flyH 3.5s forwards;}} .pop-up {{animation: popU 3s forwards;}} .spin-orbit {{animation: spinO 3s forwards;}} .zig-zag {{animation: zigZ 3.5s forwards;}} .abduction {{animation: abduct 4s forwards;}} @keyframes flyH {{0%{{transform:translate(-150vw,-50%); opacity:0;}} 50%{{opacity:1;}} 100%{{transform:translate(150vw,-50%); opacity:0;}}}} @keyframes popU {{0%{{transform:translate(-50%,100vh); opacity:0;}} 50%{{transform:translate(-50%,-50%); opacity:1;}} 100%{{transform:translate(-50%,-100vh); opacity:0;}}}} @keyframes spinO {{0%{{opacity:0; transform:translate(-50%,-50%) rotate(0deg) translateX(150px);}} 100%{{opacity:1; transform:translate(-50%,-50%) rotate(720deg) translateX(150px); opacity:0;}}}} @keyframes zigZ {{0%{{transform:translate(-50%,100vh); opacity:0;}} 50%{{transform:translate(50%,0); opacity:1;}} 100%{{transform:translate(-50%,-150vh); opacity:0;}}}} @keyframes abduct {{0%{{transform:translate(-50%,-50%) scale(0); opacity:0;}} 50%{{transform:translate(-50%,-50%) scale(1.5); filter:drop-shadow(0 0 50px #39ff14); opacity:1;}} 100%{{transform:translate(-50%,-150vh); opacity:0;}}}}</style><div class="alien-container {anim_type}">{emoji}</div>"""
    st.markdown(css, unsafe_allow_html=True)

# =========================
# DADOS E IA
# =========================
@st.cache_resource(ttl=60)
def get_google_sheet():
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        skey = dict(st.secrets["gcp_service_account"])
        credentials = Credentials.from_service_account_info(skey, scopes=scopes)
        client = gspread.authorize(credentials)
        return client.open_by_url(st.secrets["app"]["sheet_url"]).sheet1
    except: return None

def append_submission(row: dict):
    sheet = get_google_sheet()
    if sheet:
        st.cache_resource.clear()
        # Nova ordem de colunas
        linha = [row["timestamp"], row["ra_1"], row["nome_1"], row["ra_2"], row["nome_2"], row["exercicio"], row["nivel"], row["status"], row["dificuldade"], row["ajuda"], row["codigo"], row["comentarios"]]
        sheet.append_row(linha)

def load_data():
    sheet = get_google_sheet()
    if not sheet: return pd.DataFrame()
    records = sheet.get_all_records()
    df = pd.DataFrame(records)
    df.columns = [c.lower().strip().replace(' ', '_') for c in df.columns]
    return df

def tutor_ia(codigo, prompt):
    if not model: return "IA não configurada."
    sys = f"Tutor Java. Aluno resolve: {prompt}. Código: {codigo}. Regra: Usar JOptionPane. Elogie, dê uma dica sutil (ex: imports ou showMessageDialog), NUNCA dê a resposta pronta. Máx 2 parágrafos."
    try: return model.generate_content(sys).text
    except: return "Erro na IA."

# =========================
# INTERFACE
# =========================
def main():
    with st.sidebar:
        st.title("🧩 Navegação")
        page = st.radio("Acesse:", ["📚 Área do Aluno", "📊 Painel do Professor"])
    
    if page == "📚 Área do Aluno": render_student_area()
    else: render_teacher_area()

def render_student_area():
    st.markdown("""<div class="hero"><h1>Laboratório de Funções Java ☕</h1><p>Registre seus exercícios pelo RA. Medalhas agora valem para duplas!</p></div>""", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["💻 Desafios", "🏆 Conquistas"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            sel_lvl = st.selectbox("Dificuldade:", LEVEL_ORDER)
            filtrados = [e for e in EXS if e["level"] == sel_lvl]
        with c2:
            sel_ex_txt = st.selectbox("Exercício:", [f"{e['id']} - {e['title']}" for e in filtrados])
            ex = [e for e in filtrados if f"{e['id']} - {e['title']}" == sel_ex_txt][0]

        st.markdown(f"""<div class="exercise-card" style="border-left: 8px solid {LEVEL_COLORS[ex['level']][1]};"><div class="tip-box">💻 {ex['prompt']}</div></div>""", unsafe_allow_html=True)

        # Formulário
        with st.expander("📝 Enviar Resposta", expanded=True):
            col_a, col_b = st.columns(2)
            ra1 = col_a.text_input("Seu RA *")
            nome1 = col_b.text_input("Seu Nome *")
            
            with st.container():
                st.caption("Trabalho em Dupla? (Opcional)")
                col_c, col_d = st.columns(2)
                ra2 = col_c.text_input("RA do Colega")
                nome2 = col_d.text_input("Nome do Colega")

            st.divider()
            c3, c4 = st.columns(2)
            status = c3.radio("Concluiu?", STATUS_OPTS, horizontal=True)
            dif = c4.select_slider("Dificuldade:", DIF_OPTS, "Médio")
            
            codigo = st.text_area("Código Java (Use JOptionPane):", height=150)
            
            b1, b2 = st.columns(2)
            if b1.button("🤖 Tutor IA"):
                st.info(tutor_ia(codigo, ex['prompt']))
            
            if b2.button("🚀 Salvar no Sistema", type="primary"):
                if not (ra1 and nome1): st.error("RA e Nome são obrigatórios.")
                else:
                    append_submission({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"), "ra_1": ra1, "nome_1": nome1, "ra_2": ra2, "nome_2": nome2, "exercicio": ex["id"], "nivel": ex["level"], "status": status, "dificuldade": dif, "ajuda": "Não", "codigo": codigo, "comentarios": ""})
                    if "✅" in status: exibir_animacao_alienigena(ex["level"])
                    else: st.success("Enviado!")

    with tab2:
        df = load_data()
        if not df.empty:
            ra_busca = st.text_input("Digite seu RA para ver medalhas:").strip()
            if ra_busca:
                # Lógica de Dupla: Busca o RA em ra_1 OU ra_2
                # Note: Ajustamos para strings para evitar erros de tipos
                df['ra_1'] = df['ra_1'].astype(str)
                df['ra_2'] = df['ra_2'].astype(str)
                
                concluidos = df[(df['status'].str.contains("✅")) & ((df['ra_1'] == ra_busca) | (df['ra_2'] == ra_busca))]
                
                if concluidos.empty: st.warning("Nenhum exercício concluído com sucesso para este RA.")
                else:
                    st.success(f"Encontrados {concluidos['exercicio'].nunique()} exercícios únicos!")
                    cols = st.columns(5)
                    for i, lvl in enumerate(LEVEL_ORDER):
                        feitos = concluidos[concluidos['nivel'] == lvl]['exercicio'].nunique()
                        total = LEVEL_COUNTS[lvl]
                        with cols[i]:
                            if feitos >= total: st.markdown(f'<div class="badge-card">🎖️<br><b>{lvl}</b></div>', unsafe_allow_html=True)
                            else: st.markdown(f'<div class="badge-card" style="opacity:0.3">🔒<br>{lvl}<br>{feitos}/{total}</div>', unsafe_allow_html=True)

def render_teacher_area():
    st.title("📊 Painel do Professor")
    if not TEACHER_PASS: st.error("Senha não configurada."); return
    if st.text_input("Senha:", type="password") != TEACHER_PASS: return
    
    df = load_data()
    if df.empty: st.write("Sem dados."); return
    
    t1, t2, t3 = st.tabs(["Métricas", "Alertas", "IA"])
    with t1:
        st.metric("Total", len(df))
        st.dataframe(df)
    with t2:
        alertas = df[df['status'].str.contains("❌")]
        for _, r in alertas.iterrows(): st.error(f"🚨 {r['nome_1']} travou no {r['exercicio']}")
    with t3:
        if st.button("Gerar Resumo IA"):
            st.write("Análise da IA baseada nos erros recentes...") # Implemente igual ao anterior

if __name__ == "__main__": main()
