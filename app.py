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
# BANCO DE EXERCÍCIOS COMPLETOS
# =========================
EXS = [
    # --- FUNDAMENTOS ---
    {"id": "Ex 01", "title": "Mostrar mensagem", "level": "Fundamentos", "function_hint": "void", "skills": ["função", "void"], "goal": "Entender função sem retorno.", "prompt": "Crie uma função chamada mostrarMensagem() que exiba a frase 'Olá, Java!' usando JOptionPane.showMessageDialog."},
    {"id": "Ex 02", "title": "Retornar o dobro", "level": "Fundamentos", "function_hint": "com retorno", "skills": ["retorno", "parâmetro"], "goal": "Praticar parâmetro e retorno.", "prompt": "Crie uma função chamada calcularDobro(int numero) que retorne o dobro do valor."},
    {"id": "Ex 03", "title": "Soma de dois números", "level": "Fundamentos", "function_hint": "com retorno", "skills": ["parâmetros", "operações"], "goal": "Trabalhar múltiplos parâmetros.", "prompt": "Crie uma função chamada somarNumeros(int a, int b) que retorne a soma deles."},
    {"id": "Ex 04", "title": "Média de três notas", "level": "Fundamentos", "function_hint": "com retorno", "skills": ["média", "double"], "goal": "Aplicar função em cenário escolar.", "prompt": "Crie uma função chamada calcularMedia(double n1, double n2, double n3) que retorne a média."},
    {"id": "Ex 05", "title": "Área de um retângulo", "level": "Fundamentos", "function_hint": "com parâmetro", "skills": ["multiplicação", "retorno"], "goal": "Resolver problema geométrico.", "prompt": "Crie uma função chamada calcularAreaRetangulo(double base, double altura) que retorne a área."},
    {"id": "Ex 26", "title": "Tamanho do Texto", "level": "Fundamentos", "function_hint": "com retorno", "skills": ["String", "length"], "goal": "Manipular informações de textos.", "prompt": "Crie uma função chamada obterTamanho(String texto) que retorne a quantidade de caracteres da palavra."},

    # --- CONDICIONAIS ---
    {"id": "Ex 06", "title": "Verifica número par", "level": "Condicionais", "function_hint": "condicional", "skills": ["if", "módulo"], "goal": "Introduzir decisão dentro de função.", "prompt": "Crie uma função chamada verificarPar(int numero) que retorne 'Par' ou 'Ímpar'."},
    {"id": "Ex 07", "title": "Verifica aprovação", "level": "Condicionais", "function_hint": "condicional", "skills": ["if/else", "média"], "goal": "Tomar decisão com base em regra.", "prompt": "Crie uma função chamada verificarAprovacao(double media) que retorne 'Aprovado' (>= 7) ou 'Reprovado'."},
    {"id": "Ex 08", "title": "Maior entre dois números", "level": "Condicionais", "function_hint": "condicional", "skills": ["comparação", "if/else"], "goal": "Praticar comparação em função.", "prompt": "Crie uma função chamada encontrarMaior(int a, int b) que retorne o maior valor."},
    {"id": "Ex 09", "title": "Calcular desconto", "level": "Condicionais", "function_hint": "condicional", "skills": ["porcentagem", "if/else"], "goal": "Aplicar função em compras.", "prompt": "Crie uma função chamada calcularDesconto(double valorCompra). Se >= 100, aplique 10%; senão, 5%. Retorne o valor do desconto."},
    {"id": "Ex 10", "title": "Positivo, negativo ou zero", "level": "Condicionais", "function_hint": "condicional", "skills": ["if/else if", "classificação"], "goal": "Ampliar complexidade de decisão.", "prompt": "Crie uma função chamada classificarNumero(int numero) que retorne 'Positivo', 'Negativo' ou 'Zero'."},
    {"id": "Ex 27", "title": "Inicia com Letra", "level": "Condicionais", "function_hint": "condicional", "skills": ["String", "startsWith"], "goal": "Condições com métodos de String.", "prompt": "Crie uma função verificarInicial(String texto, char letra) que retorne true se começar com a letra, ou false caso contrário."},

    # --- LOOPS ---
    {"id": "Ex 11", "title": "Soma de 1 até N", "level": "Loops", "function_hint": "loop", "skills": ["for", "acumulador"], "goal": "Introduzir repetição em função.", "prompt": "Crie uma função chamada somarAteN(int n) que retorne a soma de 1 até N."},
    {"id": "Ex 12", "title": "Calcula fatorial", "level": "Loops", "function_hint": "loop", "skills": ["for", "multiplicação"], "goal": "Praticar loop com multiplicação.", "prompt": "Crie uma função chamada calcularFatorial(int n) que retorne seu fatorial."},
    {"id": "Ex 13", "title": "Conta de 1 até N", "level": "Loops", "function_hint": "void", "skills": ["loop", "impressão"], "goal": "Usar repetição sem retorno.", "prompt": "Crie uma função void chamada contarAteN(int n) que imprima de 1 até N usando JOptionPane.showMessageDialog."},
    {"id": "Ex 14", "title": "Soma pares até N", "level": "Loops", "function_hint": "loop", "skills": ["for", "if"], "goal": "Combinar filtro e repetição.", "prompt": "Crie uma função chamada somarParesAteN(int n) que retorne a soma dos pares de 1 até N."},
    {"id": "Ex 15", "title": "Gera tabuada", "level": "Loops", "function_hint": "void", "skills": ["for", "multiplicação"], "goal": "Gerar sequência útil.", "prompt": "Crie uma função void chamada gerarTabuada(int n) que exiba a tabuada (1 a 10) do número."},
    {"id": "Ex 28", "title": "Inverter Texto", "level": "Loops", "function_hint": "loop", "skills": ["String", "for"], "goal": "Percorrer String de trás para frente.", "prompt": "Crie uma função chamada inverterTexto(String texto) que retorne a palavra escrita de trás para frente."},

    # --- LOOPS E CONDICIONAIS ---
    {"id": "Ex 16", "title": "Conta pares até N", "level": "Funções com loop e condicional", "function_hint": "combinada", "skills": ["for", "if", "contador"], "goal": "Combinar repetição e decisão.", "prompt": "Crie uma função chamada contarParesAteN(int n) que retorne QUANTOS pares existem entre 1 e N."},
    {"id": "Ex 17", "title": "Soma ímpares até N", "level": "Funções com loop e condicional", "function_hint": "combinada", "skills": ["for", "if", "acumulador"], "goal": "Consolidar condição na repetição.", "prompt": "Crie uma função chamada somarImparesAteN(int n) que retorne a SOMA dos ímpares entre 1 e N."},
    {"id": "Ex 18", "title": "Verifica se é primo", "level": "Funções com loop e condicional", "function_hint": "combinada", "skills": ["for", "if", "boolean"], "goal": "Lógica elaborada com divisão.", "prompt": "Crie uma função chamada verificarPrimo(int n) que retorne true se for primo, ou false caso contrário."},
    {"id": "Ex 19", "title": "Média de N notas", "level": "Funções com loop e condicional", "function_hint": "combinada", "skills": ["loop", "acumulador"], "goal": "Processar valores lidos em loop.", "prompt": "Crie uma função chamada calcularMediaMultipla(int qtdNotas) que leia as notas (via JOptionPane) e retorne a média final."},
    {"id": "Ex 20", "title": "Situação da turma", "level": "Funções com loop e condicional", "function_hint": "combinada", "skills": ["média", "if/else"], "goal": "Dividir problema em funções.", "prompt": "Crie calcularMedia(n1,n2) e verificarSituacao(media). Use a primeira dentro da segunda para informar o status."},
    {"id": "Ex 29", "title": "Contar Vogais", "level": "Funções com loop e condicional", "function_hint": "combinada", "skills": ["String", "for", "if"], "goal": "Inspecionar caracteres iterativamente.", "prompt": "Crie uma função chamada contarVogais(String texto) que retorne a quantidade de vogais presentes na palavra."},

    # --- DESAFIADOR ---
    {"id": "Ex 21", "title": "[Desafio] Calculadora", "level": "Desafiador", "function_hint": "combinada", "skills": ["menu", "funções"], "goal": "Várias funções em um programa.", "prompt": "Crie uma calculadora com funções separadas: somar(), subtrair(), multiplicar(), dividir(). Use um menu para escolha (via JOptionPane)."},
    {"id": "Ex 22", "title": "[Desafio] Sistema de Notas", "level": "Desafiador", "function_hint": "combinada", "skills": ["funções", "média"], "goal": "Modularizar problema completo.", "prompt": "Crie um programa com funções separadas para: ler notas, calcular média, verificar aprovação e exibir boletim."},
    {"id": "Ex 23", "title": "[Desafio] Fibonacci", "level": "Desafiador", "function_hint": "loop", "skills": ["loop", "sequência"], "goal": "Lógica sequencial complexa.", "prompt": "Crie uma função chamada exibirFibonacci(int n) que imprima os N primeiros termos da sequência."},
    {"id": "Ex 24", "title": "[Desafio] Soma dos dígitos", "level": "Desafiador", "function_hint": "loop", "skills": ["while", "módulo"], "goal": "Manipulação numérica.", "prompt": "Crie uma função chamada somarDigitos(int numero) que retorne a soma dos algarismos do número (ex: 123 -> 6)."},
    {"id": "Ex 25", "title": "[Desafio] Caixa Eletrônico", "level": "Desafiador", "function_hint": "combinada", "skills": ["menu", "regras"], "goal": "Integrar funções reais.", "prompt": "Crie funções globais: verSaldo(), depositar(valor), sacar(valor). Impeça o saque se o saldo for insuficiente."},
    {"id": "Ex 30", "title": "[Desafio] Palíndromo", "level": "Desafiador", "function_hint": "combinada", "skills": ["String", "lógica reversa"], "goal": "Lógica avançada de texto.", "prompt": "Crie uma função verificarPalindromo(String texto) que retorne true se a palavra for um palíndromo (ex: 'arara')."},
]
EXS = sorted(EXS, key=lambda x: x["id"])
LEVEL_COUNTS = {lvl: len([e for e in EXS if e['level'] == lvl]) for lvl in LEVEL_ORDER}

# =========================
# ESTILO E ANIMAÇÕES RICAS
# =========================
st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1050px; }
    .hero { border-radius: 20px; padding: 28px; color: white; margin-bottom: 2rem; background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%); box-shadow: 0 10px 20px rgba(0,0,0,0.15); text-align: center; }
    .hero h1 { margin: 0 0 10px 0; font-size: 2.4rem; font-weight: 800; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);}
    .hero p { margin: 0; opacity: 0.95; font-size: 1.15rem; }
    
    .exercise-card { border-radius: 16px; padding: 24px; margin-top: 1rem; margin-bottom: 1.5rem; box-shadow: 0 8px 16px rgba(15, 23, 42, 0.08); background: #ffffff; }
    .exercise-title { font-weight: 800; font-size: 1.5rem; margin-bottom: 12px; color: #0f172a;}
    .exercise-chip { display: inline-block; padding: 6px 14px; margin-right: 8px; margin-bottom: 8px; border-radius: 20px; font-size: 0.85rem; background: #f8fafc; border: 1px solid #cbd5e1; color: #334155; font-weight: 600; }
    .tip-box { background: #f8fafc; border: 2px dashed #94a3b8; border-radius: 12px; padding: 18px; font-family: 'Courier New', monospace; font-size: 1.1rem; color: #0f172a; font-weight: 600; }
    
    .ai-box { background-color: #f0fdf4; border-left: 6px solid #22c55e; padding: 16px; border-radius: 8px; margin-top: 15px; color: #166534; font-size: 1.05rem; line-height: 1.5;}
    
    .badge-card { background: linear-gradient(145deg, #ffffff, #fffbeb); border: 2px solid #f59e0b; border-radius: 16px; padding: 20px 10px; text-align: center; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(245, 158, 11, 0.15); transition: transform 0.2s;}
    .badge-card:hover { transform: translateY(-5px); }
    .badge-card h1 { font-size: 2.5rem; margin-bottom: 5px; }
    .badge-card b { color: #92400e; font-size: 1.1rem;}
    
    .locked-badge { background: #f1f5f9; border: 2px dashed #cbd5e1; filter: grayscale(100%); opacity: 0.6; box-shadow: none; }
    
    .alert-box { background-color: #fee2e2; border-left: 6px solid #ef4444; color: #7f1d1d; padding: 16px; border-radius: 8px; margin-bottom: 12px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

def exibir_animacao_alienigena(nivel):
    configs = {
        "Fundamentos": ("🛸 Missão base concluída!", "🛸", "fly-horizontal"), 
        "Condicionais": ("👽 Nossos radares aprovam!", "👽", "pop-up"), 
        "Loops": ("☄️ Loop estelar dominado!", "☄️", "spin-orbit"), 
        "Funções com loop e condicional": ("👾 Invasão contida!", "👾", "zig-zag"), 
        "Desafiador": ("🌌 Galáxia dominada!", "🚀", "abduction")
    }
    msg, emoji, anim_type = configs.get(nivel, ("🛸 Sucesso!", "🛸", "pop-up"))
    st.toast(msg, icon=emoji)
    css = f"""<style>.alien-container {{position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 180px; z-index: 99999; pointer-events: none;}} .fly-horizontal {{animation: flyH 3.5s forwards;}} .pop-up {{animation: popU 3s forwards;}} .spin-orbit {{animation: spinO 3s forwards;}} .zig-zag {{animation: zigZ 3.5s forwards;}} .abduction {{animation: abduct 4s forwards;}} @keyframes flyH {{0%{{transform:translate(-150vw,-50%) rotate(15deg); opacity:0;}} 50%{{opacity:1;}} 100%{{transform:translate(150vw,-50%) rotate(-15deg); opacity:0;}}}} @keyframes popU {{0%{{transform:translate(-50%,100vh) scale(0.5); opacity:0;}} 50%{{transform:translate(-50%,-50%) scale(1.2); opacity:1;}} 100%{{transform:translate(-50%,-150vh) scale(0.5); opacity:0;}}}} @keyframes spinO {{0%{{opacity:0; transform:translate(-50%,-50%) rotate(0deg) translateX(200px);}} 50%{{opacity:1;}} 100%{{opacity:0; transform:translate(-50%,-50%) rotate(720deg) translateX(200px);}}}} @keyframes zigZ {{0%{{transform:translate(-50%,100vh); opacity:0;}} 25%{{transform:translate(-80%,25vh); opacity:1;}} 50%{{transform:translate(-20%,-25vh); opacity:1;}} 75%{{transform:translate(-80%,-75vh); opacity:1;}} 100%{{transform:translate(-50%,-150vh); opacity:0;}}}} @keyframes abduct {{0%{{transform:translate(-50%,-50%) scale(0); filter:drop-shadow(0 0 0px #39ff14); opacity:0;}} 50%{{transform:translate(-50%,-50%) scale(1.5); filter:drop-shadow(0 150px 50px #39ff14); opacity:1;}} 100%{{transform:translate(-50%,-150vh) scale(0); opacity:0;}}}}</style><div class="alien-container {anim_type}">{emoji}</div>"""
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
    except: 
        return None

def append_submission(row: dict):
    sheet = get_google_sheet()
    if sheet:
        st.cache_resource.clear()
        linha = [row["timestamp"], row["ra_1"], row["nome_1"], row["ra_2"], row["nome_2"], row["exercicio"], row["nivel"], row["status"], row["dificuldade"], row["ajuda"], row["codigo"], row["comentarios"]]
        sheet.append_row(linha)

def load_data():
    sheet = get_google_sheet()
    if not sheet: return pd.DataFrame()
    records = sheet.get_all_records()
    df = pd.DataFrame(records)
    if not df.empty:
        df.columns = [c.lower().strip().replace(' ', '_') for c in df.columns]
    return df

def tutor_ia(codigo, prompt):
    if not model: return "⚠️ IA não configurada. Fale com o professor."
    sys = f"""
    Você é um tutor de Java. O aluno tenta resolver: "{prompt}".
    Código:
    {codigo}
    Regra: Usar JOptionPane.
    1. Elogie o esforço.
    2. Dê UMA dica sutil se houver erro (ex: importar javax.swing.JOptionPane, ou lógica).
    3. NUNCA DEVOLVA O CÓDIGO PRONTO.
    4. Seja super breve (máx 2 parágrafos).
    """
    try: 
        return model.generate_content(sys).text
    except Exception as e: 
        return f"Erro na IA: {e}"

def relatorio_ia_professor(df):
    if not model: return "API do Gemini não configurada."
    df_dif = df[(df['status'].astype(str).str.contains("❌")) | (df['status'].astype(str).str.contains("🟡"))]
    if df_dif.empty: return "Nenhum aluno registrou falhas graves recentemente. A turma está indo muito bem!"
    
    dados_resumo = df_dif[['nome_1', 'exercicio', 'comentarios', 'codigo']].tail(15).to_string()
    sys = f"""
    Você é o coordenador pedagógico. Analise os erros recentes da turma:
    {dados_resumo}
    Gere um relatório executivo de 2 parágrafos:
    1: Resuma as principais dificuldades técnicas.
    2: Sugira como o professor deve iniciar a próxima aula (uma analogia ou foco no quadro).
    """
    try: 
        return model.generate_content(sys).text
    except Exception as e: 
        return f"Erro ao gerar resumo: {e}"

# =========================
# INTERFACE
# =========================
def main():
    with st.sidebar:
        st.title("🧩 Navegação")
        page = st.radio("Acesse:", ["📚 Área do Aluno", "📊 Painel do Professor"])
        st.markdown("---")
        st.caption("Desenvolvido para consolidar Java & Clean Code.")
    
    if page == "📚 Área do Aluno": render_student_area()
    else: render_teacher_area()

def render_student_area():
    st.markdown("""<div class="hero"><h1>Laboratório de Funções Java ☕</h1><p>Pratique, use o Tutor IA e suba no ranking da turma. Válido também para duplas!</p></div>""", unsafe_allow_html=True)
    
    tab_lab, tab_rank = st.tabs(["💻 1. Fazer Exercícios", "🏆 2. Ranking e Conquistas"])

    # --- ABA DE LABORATÓRIO ---
    with tab_lab:
        st.subheader("Seleção de Desafio")
        c1, c2 = st.columns([1, 2])
        with c1:
            sel_lvl = st.selectbox("Escolha a Trilha:", LEVEL_ORDER)
            filtrados = [e for e in EXS if e["level"] == sel_lvl]
        with c2:
            sel_ex_txt = st.selectbox("Desafio Atual:", [f"{e['id']} - {e['title']}" for e in filtrados])
            ex = [e for e in filtrados if f"{e['id']} - {e['title']}" == sel_ex_txt][0]

        # Card do Exercício
        bg_color, text_color = LEVEL_COLORS.get(ex["level"], ("#FFFFFF", "#000000"))
        badge = FUNC_BADGE.get(ex["function_hint"], "")
        skills_html = "".join([f'<span class="exercise-chip">🎯 {s}</span>' for s in ex["skills"]])

        st.markdown(f"""
        <div class="exercise-card" style="border-left: 8px solid {text_color};">
            <div style="font-weight: 700; color: {text_color}; font-size: 0.9rem; text-transform: uppercase;">{ex['level']}</div>
            <div class="exercise-title">{ex['id']} - {ex['title']}</div>
            <div style="margin-bottom: 16px;">
                <span class="exercise-chip" style="background: #e0f2fe; border-color: #bae6fd;">{badge}</span>
                {skills_html}
            </div>
            <div class="tip-box">💻 {ex['prompt']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Formulário Elegante
        st.markdown("### 📝 Submissão e Verificação")
        with st.container(border=True):
            col_a, col_b = st.columns(2)
            ra1 = col_a.text_input("Seu RA *", placeholder="Ex: 123456")
            nome1 = col_b.text_input("Seu Nome *", placeholder="Ex: João Silva")
            
            with st.expander("🤝 Fez em Dupla? Clique aqui para adicionar o colega"):
                col_c, col_d = st.columns(2)
                ra2 = col_c.text_input("RA do Colega", placeholder="Ex: 654321")
                nome2 = col_d.text_input("Nome do Colega", placeholder="Ex: Maria Souza")

            st.markdown("<br>", unsafe_allow_html=True)
            c3, c4 = st.columns(2)
            status = c3.radio("Status do Exercício:", STATUS_OPTS, horizontal=True)
            dif = c4.select_slider("Nível de Dificuldade que sentiu:", DIF_OPTS, "Médio")
            
            codigo = st.text_area("Cole seu Código Java aqui 👇 (Para análise da IA e registro)", height=180)
            comentarios = st.text_input("Comentários (Dúvidas para o professor?):", placeholder="Opcional")
            
            b1, b2 = st.columns(2)
            if b1.button("🤖 Pedir Dica ao Tutor IA", use_container_width=True):
                if not codigo.strip(): 
                    st.warning("⚠️ Cole seu código acima para a IA poder analisar!")
                else:
                    with st.spinner("Analisando sua lógica..."):
                        feedback = tutor_ia(codigo, ex['prompt'])
                        st.markdown(f'<div class="ai-box"><strong>Tutor IA:</strong><br>{feedback}</div>', unsafe_allow_html=True)
            
            if b2.button("🚀 Enviar para o Sistema", type="primary", use_container_width=True):
                if not (ra1 and nome1): 
                    st.error("⚠️ O preenchimento do seu RA e Nome é obrigatório.")
                else:
                    append_submission({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                        "ra_1": ra1.strip(), "nome_1": nome1.strip().title(), 
                        "ra_2": ra2.strip(), "nome_2": nome2.strip().title(), 
                        "exercicio": ex["id"], "nivel": ex["level"], 
                        "status": status, "dificuldade": dif, "ajuda": "Não", 
                        "codigo": codigo.strip(), "comentarios": comentarios.strip()
                    })
                    if "✅" in status: 
                        exibir_animacao_alienigena(ex["level"])
                    else: 
                        st.success("Progresso salvo! Continue tentando, o espaço é o limite. 🚀")

    # --- ABA DE RANKING E CONQUISTAS ---
    with tab_rank:
        df = load_data()
        if df.empty:
            st.info("O ranking e as medalhas aparecerão assim que a primeira missão for concluída!")
            return

        # 1. LEADERBOARD GLOBAL
        st.subheader("🌎 Top Programadores (Global)")
        st.write("Quem resolveu mais desafios únicos com sucesso até agora:")
        
        # Filtra sucessos e agrupa por Nome_1 para o ranking de diversão
        df_suc = df[df['status'].astype(str).str.contains("✅")]
        if not df_suc.empty:
            ranking = df_suc.groupby('nome_1')['exercicio'].nunique().reset_index()
            ranking = ranking.sort_values(by='exercicio', ascending=False).head(10).reset_index(drop=True)
            ranking.columns = ["Estudante", "Missões Concluídas"]
            ranking.index = ranking.index + 1
            st.dataframe(ranking, use_container_width=True)
        else:
            st.write("Ainda não há vencedores. Seja o primeiro!")

        st.divider()

        # 2. MEDALHAS INDIVIDUAIS (Busca por RA)
        st.subheader("🎖️ Suas Conquistas (Badges)")
        ra_busca = st.text_input("🔍 Digite seu RA para ver as medalhas desbloqueadas:").strip()
        
        if ra_busca:
            df['ra_1'] = df['ra_1'].astype(str).str.strip()
            df['ra_2'] = df['ra_2'].astype(str).str.strip()
            
            concluidos = df[(df['status'].astype(str).str.contains("✅")) & ((df['ra_1'] == ra_busca) | (df['ra_2'] == ra_busca))]
            
            if concluidos.empty: 
                st.warning("Nenhum exercício concluído com sucesso foi encontrado para este RA.")
            else:
                total_unicos = concluidos['exercicio'].nunique()
                st.success(f"Excelente! Você participou de {total_unicos} missões bem-sucedidas.")
                
                cols = st.columns(5)
                for i, lvl in enumerate(LEVEL_ORDER):
                    feitos = concluidos[concluidos['nivel'] == lvl]['exercicio'].nunique()
                    total = LEVEL_COUNTS[lvl]
                    with cols[i]:
                        if feitos >= total: 
                            st.markdown(f'<div class="badge-card"><h1>🎖️</h1><b>Mestre em<br>{lvl}</b><br><small>{feitos}/{total}</small></div>', unsafe_allow_html=True)
                        else: 
                            st.markdown(f'<div class="badge-card locked-badge"><h1>🔒</h1><b>{lvl}</b><br><small>{feitos}/{total}</small></div>', unsafe_allow_html=True)

def render_teacher_area():
    st.title("📊 Painel de Controle Pedagógico")
    if not TEACHER_PASS: 
        st.error("⚠️ ERRO: Senha não configurada nos Secrets.")
        return
    
    pwd = st.text_input("Senha de acesso", type="password")
    if pwd != TEACHER_PASS: 
        if pwd: st.error("Senha incorreta.")
        return
    
    col_t, col_btn = st.columns([4, 1])
    with col_btn:
        if st.button("🔄 Atualizar Dados", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()

    df = load_data()
    if df.empty: 
        st.info("O banco de dados está vazio no momento.")
        return
    
    t1, t2, t3, t4 = st.tabs(["📈 Visão Geral", "🚨 Alertas", "🧠 Assistente IA", "📋 Tabela Bruta"])
    
    with t1:
        st.subheader("Termômetro da Aula")
        c1, c2, c3 = st.columns(3)
        total_subs = len(df)
        sucessos = len(df[df['status'].astype(str).str.contains("✅")])
        tx_sucesso = (sucessos / total_subs) * 100 if total_subs > 0 else 0
        
        c1.metric("Submissões Totais", total_subs)
        c2.metric("Concluídos com Sucesso", sucessos)
        c3.metric("Aproveitamento Médio", f"{tx_sucesso:.1f}%")

        st.markdown("**Desempenho por Exercício:**")
        try:
            df_stats = df.groupby(['exercicio', 'status']).size().unstack(fill_value=0)
            st.bar_chart(df_stats)
        except:
            st.write("Aguardando mais dados para gerar o gráfico.")

    with t2:
        st.subheader("⚠️ Alunos Travados (Atenção Imediata)")
        alertas = df[(df['status'].astype(str).str.contains("❌")) | (df['dificuldade'].astype(str) == "Difícil")]
        if alertas.empty:
            st.success("Tudo certo! Ninguém relatou problemas graves.")
        else:
            for _, r in alertas.iterrows(): 
                st.markdown(f"""
                <div class="alert-box">
                    <strong>{r['nome_1']}</strong> está com problemas no <strong>{r['exercicio']}</strong>.<br>
                    <small>Dificuldade: {r['dificuldade']} | Status: {r['status']}</small>
                </div>
                """, unsafe_allow_html=True)
                if len(str(r.get('codigo', ''))) > 3:
                    with st.expander(f"Ver código com erro de {r['nome_1']}"):
                        st.code(r['codigo'], language="java")

    with t3:
        st.subheader("🤖 Diagnóstico Automatizado da Turma")
        st.write("Deixe o Gemini ler todos os códigos com erro e comentários para resumir a situação da aula para você.")
        if st.button("🧠 Gerar Resumo com IA", type="primary"):
            with st.spinner("Analisando padrões de erro da turma..."):
                relatorio = relatorio_ia_professor(df)
                st.markdown(f'<div class="ai-box">{relatorio}</div>', unsafe_allow_html=True)

    with t4:
        st.subheader("Auditoria Completa")
        st.dataframe(df, use_container_width=True)
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Planilha (CSV)", data=csv_data, file_name='relatorio_aula_java.csv', mime='text/csv')

if __name__ == "__main__": 
    main()
