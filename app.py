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
    # Usando o flash por ser extremamente rápido para feedbacks textuais
    model = genai.GenerativeModel('gemini-2.5-flash') 
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
    {"id": "Ex 01", "title": "Mostrar mensagem", "level": "Fundamentos", "function_hint": "void", "skills": ["função", "void"], "goal": "Entender função sem retorno.", "prompt": "Crie uma função chamada mostrarMensagem() que exiba a frase 'Olá, Java!'."},
    {"id": "Ex 02", "title": "Retornar o dobro", "level": "Fundamentos", "function_hint": "com retorno", "skills": ["retorno", "parâmetro"], "goal": "Praticar parâmetro e retorno.", "prompt": "Crie uma função chamada calcularDobro(int numero) que retorne o dobro do valor."},
    {"id": "Ex 03", "title": "Soma de dois números", "level": "Fundamentos", "function_hint": "com retorno", "skills": ["parâmetros", "operações"], "goal": "Trabalhar múltiplos parâmetros.", "prompt": "Crie uma função chamada somarNumeros(int a, int b) que retorne a soma deles."},
    {"id": "Ex 04", "title": "Média de três notas", "level": "Fundamentos", "function_hint": "com retorno", "skills": ["média", "double"], "goal": "Aplicar função em cenário escolar.", "prompt": "Crie uma função chamada calcularMedia(double n1, double n2, double n3) que retorne a média."},
    {"id": "Ex 05", "title": "Área de um retângulo", "level": "Fundamentos", "function_hint": "com parâmetro", "skills": ["multiplicação", "retorno"], "goal": "Resolver problema geométrico.", "prompt": "Crie uma função chamada calcularAreaRetangulo(double base, double altura) que retorne a área."},
    {"id": "Ex 26", "title": "Tamanho do Texto", "level": "Fundamentos", "function_hint": "com retorno", "skills": ["String", "length"], "goal": "Manipular informações de textos.", "prompt": "Crie uma função chamada obterTamanho(String texto) que retorne a quantidade de caracteres da palavra."},
    
    {"id": "Ex 06", "title": "Verifica número par", "level": "Condicionais", "function_hint": "condicional", "skills": ["if", "módulo"], "goal": "Introduzir decisão dentro de função.", "prompt": "Crie uma função chamada verificarPar(int numero) que retorne 'Par' ou 'Ímpar'."},
    {"id": "Ex 07", "title": "Verifica aprovação", "level": "Condicionais", "function_hint": "condicional", "skills": ["if/else", "média"], "goal": "Tomar decisão com base em regra.", "prompt": "Crie uma função chamada verificarAprovacao(double media) que retorne 'Aprovado' (>= 7) ou 'Reprovado'."},
    {"id": "Ex 08", "title": "Maior entre dois números", "level": "Condicionais", "function_hint": "condicional", "skills": ["comparação", "if/else"], "goal": "Praticar comparação em função.", "prompt": "Crie uma função chamada encontrarMaior(int a, int b) que retorne o maior valor."},
    {"id": "Ex 09", "title": "Calcular desconto", "level": "Condicionais", "function_hint": "condicional", "skills": ["porcentagem", "if/else"], "goal": "Aplicar função em compras.", "prompt": "Crie uma função chamada calcularDesconto(double valorCompra). Se >= 100, aplique 10%; senão, 5%. Retorne o valor do desconto."},
    {"id": "Ex 10", "title": "Positivo, negativo ou zero", "level": "Condicionais", "function_hint": "condicional", "skills": ["if/else if", "classificação"], "goal": "Ampliar complexidade de decisão.", "prompt": "Crie uma função chamada classificarNumero(int numero) que retorne 'Positivo', 'Negativo' ou 'Zero'."},
    {"id": "Ex 27", "title": "Inicia com Letra", "level": "Condicionais", "function_hint": "condicional", "skills": ["String", "startsWith"], "goal": "Condições com métodos de String.", "prompt": "Crie uma função verificarInicial(String texto, char letra) que retorne true se começar com a letra, ou false caso contrário."},

    {"id": "Ex 11", "title": "Soma de 1 até N", "level": "Loops", "function_hint": "loop", "skills": ["for", "acumulador"], "goal": "Introduzir repetição em função.", "prompt": "Crie uma função chamada somarAteN(int n) que retorne a soma de 1 até N."},
    {"id": "Ex 12", "title": "Calcula fatorial", "level": "Loops", "function_hint": "loop", "skills": ["for", "multiplicação"], "goal": "Praticar loop com multiplicação.", "prompt": "Crie uma função chamada calcularFatorial(int n) que retorne seu fatorial."},
    {"id": "Ex 13", "title": "Conta de 1 até N", "level": "Loops", "function_hint": "void", "skills": ["loop", "impressão"], "goal": "Usar repetição sem retorno.", "prompt": "Crie uma função void chamada contarAteN(int n) que imprima de 1 até N."},
    {"id": "Ex 14", "title": "Soma pares até N", "level": "Loops", "function_hint": "loop", "skills": ["for", "if"], "goal": "Combinar filtro e repetição.", "prompt": "Crie uma função chamada somarParesAteN(int n) que retorne a soma dos pares de 1 até N."},
    {"id": "Ex 15", "title": "Gera tabuada", "level": "Loops", "function_hint": "void", "skills": ["for", "multiplicação"], "goal": "Gerar sequência útil.", "prompt": "Crie uma função void chamada gerarTabuada(int n) que exiba a tabuada (1 a 10) do número."},
    {"id": "Ex 28", "title": "Inverter Texto", "level": "Loops", "function_hint": "loop", "skills": ["String", "for"], "goal": "Percorrer String de trás para frente.", "prompt": "Crie uma função chamada inverterTexto(String texto) que retorne a palavra escrita de trás para frente."},

    {"id": "Ex 16", "title": "Conta pares até N", "level": "Funções com loop e condicional", "function_hint": "combinada", "skills": ["for", "if", "contador"], "goal": "Combinar repetição e decisão.", "prompt": "Crie uma função chamada contarParesAteN(int n) que retorne QUANTOS pares existem entre 1 e N."},
    {"id": "Ex 17", "title": "Soma ímpares até N", "level": "Funções com loop e condicional", "function_hint": "combinada", "skills": ["for", "if", "acumulador"], "goal": "Consolidar condição na repetição.", "prompt": "Crie uma função chamada somarImparesAteN(int n) que retorne a SOMA dos ímpares entre 1 e N."},
    {"id": "Ex 18", "title": "Verifica se é primo", "level": "Funções com loop e condicional", "function_hint": "combinada", "skills": ["for", "if", "boolean"], "goal": "Lógica elaborada com divisão.", "prompt": "Crie uma função chamada verificarPrimo(int n) que retorne true se for primo, ou false caso contrário."},
    {"id": "Ex 19", "title": "Média de N notas", "level": "Funções com loop e condicional", "function_hint": "combinada", "skills": ["loop", "acumulador"], "goal": "Processar valores lidos em loop.", "prompt": "Crie uma função chamada calcularMediaMultipla(int qtdNotas) que leia as notas e retorne a média final."},
    {"id": "Ex 20", "title": "Situação da turma", "level": "Funções com loop e condicional", "function_hint": "combinada", "skills": ["média", "if/else"], "goal": "Dividir problema em funções.", "prompt": "Crie calcularMedia(n1,n2) e verificarSituacao(media). Use a primeira dentro da segunda para informar o status."},
    {"id": "Ex 29", "title": "Contar Vogais", "level": "Funções com loop e condicional", "function_hint": "combinada", "skills": ["String", "for", "if"], "goal": "Inspecionar caracteres iterativamente.", "prompt": "Crie uma função chamada contarVogais(String texto) que retorne a quantidade de vogais presentes na palavra."},

    {"id": "Ex 21", "title": "[Desafio] Calculadora", "level": "Desafiador", "function_hint": "combinada", "skills": ["menu", "funções"], "goal": "Várias funções em um programa.", "prompt": "Crie uma calculadora com funções separadas: somar(), subtrair(), multiplicar(), dividir(). Use um menu para escolha."},
    {"id": "Ex 22", "title": "[Desafio] Sistema de Notas", "level": "Desafiador", "function_hint": "combinada", "skills": ["funções", "média"], "goal": "Modularizar problema completo.", "prompt": "Crie um programa com funções separadas para: ler notas, calcular média, verificar aprovação e exibir boletim."},
    {"id": "Ex 23", "title": "[Desafio] Fibonacci", "level": "Desafiador", "function_hint": "loop", "skills": ["loop", "sequência"], "goal": "Lógica sequencial complexa.", "prompt": "Crie uma função chamada exibirFibonacci(int n) que imprima os N primeiros termos da sequência."},
    {"id": "Ex 24", "title": "[Desafio] Soma dos dígitos", "level": "Desafiador", "function_hint": "loop", "skills": ["while", "módulo"], "goal": "Manipulação numérica.", "prompt": "Crie uma função chamada somarDigitos(int numero) que retorne a soma dos algarismos do número (ex: 123 -> 6)."},
    {"id": "Ex 25", "title": "[Desafio] Caixa Eletrônico", "level": "Desafiador", "function_hint": "combinada", "skills": ["menu", "regras"], "goal": "Integrar funções reais.", "prompt": "Crie funções globais: verSaldo(), depositar(valor), sacar(valor). Impeça o saque se o saldo for insuficiente."},
    {"id": "Ex 30", "title": "[Desafio] Palíndromo", "level": "Desafiador", "function_hint": "combinada", "skills": ["String", "lógica reversa"], "goal": "Lógica avançada de texto.", "prompt": "Crie uma função verificarPalindromo(String texto) que retorne true se a palavra for um palíndromo (ex: 'arara')."},
]
EXS = sorted(EXS, key=lambda x: x["id"])

# Total de exercícios por nível (útil para calcular Badges)
LEVEL_COUNTS = {lvl: len([e for e in EXS if e['level'] == lvl]) for lvl in LEVEL_ORDER}

# =========================
# ESTILO E ANIMAÇÕES
# =========================
st.markdown(
    """
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1000px; }
    .hero { border-radius: 16px; padding: 24px; color: white; margin-bottom: 1.5rem; background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%); box-shadow: 0 8px 16px rgba(0,0,0,0.1); text-align: center; }
    .hero h1 { margin: 0 0 10px 0; font-size: 2.2rem; font-weight: 800; }
    .hero p { margin: 0; opacity: 0.9; font-size: 1.1rem; }
    .exercise-card { border-radius: 12px; padding: 24px; margin-top: 1rem; margin-bottom: 1rem; box-shadow: 0 4px 10px rgba(0,0,0,0.08); background: #ffffff; }
    .exercise-title { font-weight: 800; font-size: 1.4rem; margin-bottom: 12px; color: #1e293b;}
    .exercise-chip { display: inline-block; padding: 6px 12px; margin-right: 8px; margin-bottom: 8px; border-radius: 20px; font-size: 0.85rem; background: #f1f5f9; border: 1px solid #e2e8f0; color: #334155; font-weight: 600; }
    .tip-box { background: #f8fafc; border: 2px dashed #94a3b8; border-radius: 10px; padding: 16px; font-family: 'Courier New', monospace; font-size: 1.05rem; color: #0f172a; font-weight: 600; }
    .ai-box { background-color: #f0fdf4; border-left: 6px solid #22c55e; padding: 16px; border-radius: 8px; margin-top: 10px; color: #166534; }
    .badge-card { background: #fffbeb; border: 2px solid #fbbf24; border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 10px;}
    </style>
    """, unsafe_allow_html=True
)

def exibir_animacao_alienigena(nivel):
    configs = {
        "Fundamentos": ("🛸 Contato estabelecido! Missão base concluída!", "🛸", "fly-horizontal"),
        "Condicionais": ("👽 Escolha inteligente! Nossos radares aprovam!", "👽", "pop-up"),
        "Loops": ("☄️ Órbita perfeita! Você dominou o loop estelar!", "☄️", "spin-orbit"),
        "Funções com loop e condicional": ("👾 Lógica ativada! Invasão contida!", "👾", "zig-zag"),
        "Desafiador": ("🌌 Abdução de conhecimento! Você dominou a galáxia!", "🛸", "abduction")
    }
    msg, emoji, anim_type = configs.get(nivel, ("🛸 Sucesso estelar!", "🛸", "pop-up"))
    st.toast(msg, icon=emoji)
    css_animation = f"""<style>.alien-container {{position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 150px; z-index: 99999; pointer-events: none;}} .fly-horizontal {{animation: flyH 3.5s forwards ease-in-out;}} .pop-up {{animation: popU 3s forwards;}} .spin-orbit {{animation: spinO 3s forwards linear;}} .zig-zag {{animation: zigZ 3.5s forwards;}} .abduction {{animation: abduct 4s forwards;}} @keyframes flyH {{0% {{ transform: translate(-150vw, -50%) rotate(15deg); opacity: 0; }} 20% {{ opacity: 1; transform: translate(-50vw, -40%) rotate(-10deg); }} 80% {{ opacity: 1; transform: translate(50vw, -60%) rotate(10deg); }} 100% {{ transform: translate(150vw, -50%); opacity: 0; }}}} @keyframes popU {{0% {{ transform: translate(-50%, 100vh) scale(0.1); opacity: 0; }} 30% {{ transform: translate(-50%, -50%) scale(1.2); opacity: 1; }} 70% {{ transform: translate(-50%, -50%) scale(1); opacity: 1; }} 100% {{ transform: translate(-50%, -100vh) scale(0.1); opacity: 0; }}}} @keyframes spinO {{0% {{ transform: translate(-50%, -50%) rotate(0deg) translateX(200px) rotate(0deg); opacity: 0; }} 20% {{ opacity: 1; }} 80% {{ opacity: 1; }} 100% {{ transform: translate(-50%, -50%) rotate(720deg) translateX(200px) rotate(-720deg); opacity: 0; }}}} @keyframes zigZ {{0% {{ transform: translate(-50%, 100vh); opacity: 0; }} 25% {{ transform: translate(-80%, 25vh); opacity: 1; }} 50% {{ transform: translate(-20%, -25vh); opacity: 1; }} 75% {{ transform: translate(-80%, -75vh); opacity: 1; }} 100% {{ transform: translate(-50%, -150vh); opacity: 0; }}}} @keyframes abduct {{0% {{ transform: translate(-50%, -50%) scale(0.1); filter: drop-shadow(0 0 0px #39ff14); opacity: 0; }} 50% {{ transform: translate(-50%, -50%) scale(1.5); filter: drop-shadow(0 150px 50px #39ff14); opacity: 1; }} 100% {{ transform: translate(-50%, -150vh) scale(0.1); opacity: 0; }}}}</style><div class="alien-container {anim_type}">{emoji}</div>"""
    st.markdown(css_animation, unsafe_allow_html=True)

# =========================
# INTEGRAÇÕES DE DADOS E IA
# =========================
@st.cache_resource(ttl=60)
def get_google_sheet():
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        skey = dict(st.secrets["gcp_service_account"])
        credentials = Credentials.from_service_account_info(skey, scopes=scopes)
        client = gspread.authorize(credentials)
        sheet_url = st.secrets["app"]["sheet_url"]
        return client.open_by_url(sheet_url).sheet1
    except Exception as e:
        st.error("⚠️ Erro ao conectar com o Google Sheets. Verifique seus Secrets.")
        return None

def append_submission(row: dict):
    sheet = get_google_sheet()
    if sheet is None: return
    st.cache_resource.clear()
    linha = [row["timestamp"], row["aluno"], row["id_exercicio"], row["nivel"], row["status"], row["dificuldade"], row["ajuda"], row["codigo"], row["comentarios"]]
    sheet.append_row(linha)

def load_data():
    sheet = get_google_sheet()
    if sheet is None: return pd.DataFrame()
    records = sheet.get_all_records()
    if records:
        df = pd.DataFrame(records)
        df.columns = [c.lower().strip() for c in df.columns]
        return df
    return pd.DataFrame()

def tutor_ia(codigo, prompt_exercicio):
    if not model:
        return "⚠️ A API do Gemini não está configurada nos Secrets. Fale com o professor!"
    
    sys_prompt = f"""
    Você é um tutor amigável de Java ajudando um estudante iniciante. 
    O aluno tentou resolver o seguinte exercício: "{prompt_exercicio}".
    
    Código do aluno:
    {codigo}
    
    Sua missão:
    1. Elogie o que está correto ou o esforço demonstrado.
    2. Se houver erro de lógica, sintaxe ou padrão Clean Code (ex: camelCase), dê UMA DICA sutil.
    3. NUNCA DEVOLVA O CÓDIGO CORRIGIDO. Faça o aluno pensar.
    4. Verifique se o estudante usar a biblioteca JOptionPane, quando cabível.
    5. Seja super breve e didático (máximo 2 parágrafos curtos).
    """
    try:
        response = model.generate_content(sys_prompt)
        return response.text
    except Exception as e:
        return f"Erro ao contatar o tutor IA: {e}"

def relatorio_ia_professor(df):
    if not model:
        return "API do Gemini não configurada."
    
    df_dificuldades = df[(df['status'].astype(str).str.contains("❌")) | (df['status'].astype(str).str.contains("🟡"))]
    if df_dificuldades.empty:
        return "Nenhum aluno registrou falhas graves recentemente. A turma está indo muito bem!"
    
    dados_resumo = df_dificuldades[['aluno', 'exercicio', 'comentarios', 'codigo']].tail(15).to_string()
    
    sys_prompt = f"""
    Você é o coordenador pedagógico assistindo um professor de programação Java.
    Abaixo estão os registros recentes de alunos que não conseguiram finalizar os exercícios ou relataram problemas:
    
    {dados_resumo}
    
    Sua missão: Gere um relatório executivo de 2 parágrafos.
    Parágrafo 1: Resuma as principais dificuldades (ex: erros de sintaxe comuns, confusão lógica generalizada).
    Parágrafo 2: Dê uma sugestão prática de como o professor deve iniciar a próxima aula para sanar esses erros (ex: uma analogia no quadro).
    """
    try:
        response = model.generate_content(sys_prompt)
        return response.text
    except Exception as e:
        return f"Erro ao gerar resumo: {e}"

# =========================
# INTERFACE PRINCIPAL
# =========================
def main():
    with st.sidebar:
        st.title("🧩 Navegação")
        page = st.radio("Acesse:", ["📚 Área do Aluno", "📊 Painel do Professor"])
        st.markdown("---")
        st.caption("Powered by Streamlit & Gemini AI")

    if page == "📚 Área do Aluno":
        render_student_area()
    else:
        render_teacher_area()

def render_student_area():
    st.markdown("""<div class="hero"><h1>Laboratório de Funções Java ☕</h1><p>Pratique, verifique seu código com nosso Tutor IA e suba no ranking da turma!</p></div>""", unsafe_allow_html=True)

    tab_lab, tab_ranking = st.tabs(["💻 Fazer Exercícios", "🏆 Ranking & Conquistas"])

    # ABA 1: LABORATÓRIO E TUTOR IA
    with tab_lab:
        c1, c2 = st.columns([1, 2])
        with c1:
            selected_level = st.selectbox("1. Escolha a Trilha:", LEVEL_ORDER)
            filtered_exs = [ex for ex in EXS if ex["level"] == selected_level]
        with c2:
            ex_options = {f"{ex['id']} - {ex['title']}": ex for ex in filtered_exs}
            selected_ex_title = st.selectbox("2. Desafio Atual:", list(ex_options.keys()))
            ex = ex_options[selected_ex_title]

        bg_color, text_color = LEVEL_COLORS.get(ex["level"], ("#FFFFFF", "#000000"))
        badge = FUNC_BADGE.get(ex["function_hint"], "")
        skills_html = "".join([f'<span class="exercise-chip">🎯 {s}</span>' for s in ex["skills"]])

        st.markdown(f"""
        <div class="exercise-card" style="border-left: 8px solid {text_color};">
            <div class="section-label" style="color: {text_color};">{ex['level']}</div>
            <div class="exercise-title">{ex['id']} - {ex['title']}</div>
            <div style="margin-bottom: 16px;">
                <span class="exercise-chip" style="background: #e0f2fe; border-color: #bae6fd;">{badge}</span>
                {skills_html}
            </div>
            <div class="tip-box">💻 {ex['prompt']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 📝 Registro e Correção")
        
        # Como temos o Tutor IA e o Envio, não usamos st.form para evitar que o clique no Tutor resete a página enviando os dados.
        nome = st.text_input("Seu Nome (Para salvar progresso e ranking) *", key=f"nome_{ex['id']}")
        
        col1, col2 = st.columns(2)
        status = col1.radio("Status:", STATUS_OPTS, key=f"stat_{ex['id']}")
        dificuldade = col2.select_slider("Dificuldade:", options=DIF_OPTS, value="Médio", key=f"dif_{ex['id']}")
        
        codigo = st.text_area("Cole seu código Java aqui 👇", height=150, key=f"cod_{ex['id']}")
        ajuda = st.checkbox("Precisei de ajuda externa", key=f"ajd_{ex['id']}")
        comentarios = st.text_input("Comentários ou Dúvidas:", key=f"com_{ex['id']}")

        btn_ia, btn_submit = st.columns(2)
        
        with btn_ia:
            if st.button("🤖 Validar com Tutor IA", use_container_width=True):
                if not codigo.strip():
                    st.warning("Cole seu código na caixa acima primeiro!")
                else:
                    with st.spinner("Analisando sua lógica..."):
                        feedback = tutor_ia(codigo, ex['prompt'])
                        st.markdown(f'<div class="ai-box"><strong>Tutor IA diz:</strong><br>{feedback}</div>', unsafe_allow_html=True)

        with btn_submit:
            if st.button("💾 Enviar Exercício Definivo", type="primary", use_container_width=True):
                if not nome.strip():
                    st.error("⚠️ Preencha seu nome para registrar o avanço.")
                else:
                    row = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "aluno": nome.strip().upper(), # Upper para padronizar no ranking
                        "id_exercicio": ex["id"],
                        "nivel": ex["level"],
                        "status": status,
                        "dificuldade": dificuldade,
                        "ajuda": "Sim" if ajuda else "Não",
                        "codigo": codigo.strip(),
                        "comentarios": comentarios.strip()
                    }
                    append_submission(row)
                    if "✅" in status:
                        exibir_animacao_alienigena(ex["level"])
                    else:
                        st.success("Salvo com sucesso! O erro faz parte do aprendizado.")

    # ABA 2: RANKING E GAMIFICAÇÃO
    with tab_ranking:
        df = load_data()
        if df.empty:
            st.info("O ranking será exibido assim que o primeiro aluno enviar um exercício!")
            return

        col_aluno = 'aluno' if 'aluno' in df.columns else df.columns[1]
        col_status = 'status' if 'status' in df.columns else df.columns[4]
        col_ex = 'exercicio' if 'exercicio' in df.columns else ('id_exercicio' if 'id_exercicio' in df.columns else df.columns[2])
        col_nivel = 'nivel' if 'nivel' in df.columns else df.columns[3]

        st.subheader("🏆 Leaderboard Global")
        df_sucessos = df[df[col_status].astype(str).str.contains("✅")]
        
        if not df_sucessos.empty:
            # Conta exercícios únicos corretos por aluno
            ranking = df_sucessos.groupby(col_aluno)[col_ex].nunique().reset_index()
            ranking = ranking.sort_values(by=col_ex, ascending=False).reset_index(drop=True)
            ranking.columns = ["Top Programadores", "Exercícios Concluídos"]
            ranking.index = ranking.index + 1
            st.dataframe(ranking.head(10), use_container_width=True)
        else:
            st.write("Ninguém concluiu um exercício com sucesso ainda. Seja o primeiro!")

        st.divider()
        st.subheader("🏅 Seu Perfil de Conquistas (Badges)")
        pesquisa_nome = st.text_input("Digite seu nome (exatamente como você envia) para ver suas medalhas:")
        
        if pesquisa_nome:
            pesquisa_nome = pesquisa_nome.strip().upper()
            df_aluno = df_sucessos[df_sucessos[col_aluno] == pesquisa_nome]
            
            if df_aluno.empty:
                st.warning("Nenhum exercício concluído com sucesso encontrado para esse nome.")
            else:
                concluidos_por_nivel = df_aluno.groupby(col_nivel)[col_ex].nunique().to_dict()
                
                c1, c2, c3, c4, c5 = st.columns(5)
                cols = [c1, c2, c3, c4, c5]
                
                for idx, lvl in enumerate(LEVEL_ORDER):
                    feitos = concluidos_por_nivel.get(lvl, 0)
                    total = LEVEL_COUNTS.get(lvl, 1)
                    
                    with cols[idx]:
                        if feitos >= total:
                            st.markdown(f'<div class="badge-card"><h1>🎖️</h1><b>Mestre em<br>{lvl}</b><br><small>{feitos}/{total}</small></div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="badge-card" style="filter: grayscale(100%); opacity: 0.5;"><h1>🔒</h1><b>{lvl}</b><br><small>{feitos}/{total}</small></div>', unsafe_allow_html=True)


def render_teacher_area():
    st.title("📊 Painel Pedagógico de IA")
    
    if not TEACHER_PASS:
        st.error("⚠️ ERRO: Senha 'teacher_password' não configurada nos Secrets.")
        return

    pwd = st.text_input("Senha de acesso", type="password")
    if pwd != TEACHER_PASS:
        if pwd: st.error("Senha incorreta.")
        st.warning("Insira a senha do professor.")
        return

    col_t, col_btn = st.columns([4, 1])
    with col_btn:
        if st.button("🔄 Atualizar"):
            st.cache_resource.clear()
            st.rerun()

    df = load_data()
    if df.empty:
        st.info("Nenhum dado recebido ainda.")
        return

    col_status = 'status' if 'status' in df.columns else df.columns[4]
    col_aluno = 'aluno' if 'aluno' in df.columns else df.columns[1]
    col_ex = 'exercicio' if 'exercicio' in df.columns else ('id_exercicio' if 'id_exercicio' in df.columns else df.columns[2])
    col_data = 'data' if 'data' in df.columns else ('timestamp' if 'timestamp' in df.columns else df.columns[0])

    tab1, tab2, tab_ia = st.tabs(["📊 Visão Geral", "📋 Auditoria e Download", "🧠 Diagnóstico da IA"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        total_subs = len(df)
        sucessos = len(df[df[col_status].astype(str).str.contains("✅")])
        tx_sucesso = (sucessos / total_subs) * 100 if total_subs > 0 else 0
        c1.metric("Submissões", total_subs)
        c2.metric("Sucessos", sucessos)
        c3.metric("Aproveitamento", f"{tx_sucesso:.1f}%")

        st.subheader("Termômetro de Exercícios")
        try:
            df_stats = df.groupby([col_ex, col_status]).size().unstack(fill_value=0)
            st.bar_chart(df_stats)
        except Exception:
            st.write("Aguardando mais dados.")

    with tab2:
        st.dataframe(df.sort_values(by=col_data, ascending=False), use_container_width=True)
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Dados (CSV)", data=csv_data, file_name='relatorio_java.csv', mime='text/csv')

    # ABA 3: DIAGNÓSTICO DO GEMINI PARA O PROFESSOR
    with tab_ia:
        st.subheader("Assistente de Ensino (Gemini AI)")
        st.write("Clique no botão abaixo para gerar um resumo automático sobre onde a turma está travando hoje e receber sugestões pedagógicas.")
        
        if st.button("🧠 Gerar Diagnóstico da Turma", type="primary"):
            with st.spinner("Lendo códigos e falhas da turma..."):
                relatorio = relatorio_ia_professor(df)
                st.markdown(f"""
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 10px; border-left: 5px solid #3b82f6;">
                    <h4>Relatório do Coordenador IA:</h4>
                    {relatorio}
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
