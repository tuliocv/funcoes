import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from filelock import FileLock

# =========================
# CONFIGURAÇÕES INICIAIS
# =========================
st.set_page_config(
    page_title="Java — Funções na Prática",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

CSV_PATH = DATA_DIR / "feedback_java_funcoes.csv"
JSONL_PATH = DATA_DIR / "feedback_java_funcoes.jsonl"
LOCK_PATH = DATA_DIR / "feedback_java_funcoes.lock"

STATUS_OPTS = ["✅ Consegui", "🟡 Parcial", "❌ Não consegui"]
DIF_OPTS = ["Muito fácil", "Fácil", "Médio", "Difícil"]
HELP_OPTS = ["Não", "Sim"]

TEACHER_PASS = st.secrets.get("app", {}).get("teacher_password", "prof123")

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
    # --- FUNDAMENTOS ---
    {
        "id": "Ex 01", "title": "Mostrar mensagem", "level": "Fundamentos", "function_hint": "void",
        "skills": ["função", "void", "organização"], "goal": "Entender função sem retorno.",
        "prompt": "Crie uma função chamada mostrarMensagem() que exiba a frase 'Olá, Java!'.",
    },
    {
        "id": "Ex 02", "title": "Retornar o dobro", "level": "Fundamentos", "function_hint": "com retorno",
        "skills": ["retorno", "parâmetro", "cálculo simples"], "goal": "Praticar parâmetro e retorno.",
        "prompt": "Crie uma função chamada calcularDobro(int numero) que retorne o dobro do valor.",
    },
    {
        "id": "Ex 03", "title": "Soma de dois números", "level": "Fundamentos", "function_hint": "com retorno",
        "skills": ["parâmetros", "retorno", "operações"], "goal": "Trabalhar múltiplos parâmetros.",
        "prompt": "Crie uma função chamada somarNumeros(int a, int b) que retorne a soma deles.",
    },
    {
        "id": "Ex 04", "title": "Média de três notas", "level": "Fundamentos", "function_hint": "com retorno",
        "skills": ["média", "double", "retorno"], "goal": "Aplicar função em cenário escolar.",
        "prompt": "Crie uma função chamada calcularMedia(double n1, double n2, double n3) que retorne a média.",
    },
    {
        "id": "Ex 05", "title": "Área de um retângulo", "level": "Fundamentos", "function_hint": "com parâmetro",
        "skills": ["multiplicação", "parâmetros", "retorno"], "goal": "Resolver problema geométrico simples.",
        "prompt": "Crie uma função chamada calcularAreaRetangulo(double base, double altura) que retorne a área.",
    },
    {
        "id": "Ex 26", "title": "Tamanho do Texto", "level": "Fundamentos", "function_hint": "com retorno", 
        "skills": ["String", "length", "retorno"], "goal": "Aprender a manipular informações de textos.", 
        "prompt": "Crie uma função chamada obterTamanho(String texto) que retorne a quantidade de caracteres da palavra."
    },

    # --- CONDICIONAIS ---
    {
        "id": "Ex 06", "title": "Verifica número par", "level": "Condicionais", "function_hint": "condicional",
        "skills": ["if", "módulo", "retorno"], "goal": "Introduzir decisão dentro de função.",
        "prompt": "Crie uma função chamada verificarPar(int numero) que retorne 'Par' ou 'Ímpar'.",
    },
    {
        "id": "Ex 07", "title": "Verifica aprovação", "level": "Condicionais", "function_hint": "condicional",
        "skills": ["if/else", "média", "retorno"], "goal": "Tomar decisão com base em regra de negócio.",
        "prompt": "Crie uma função chamada verificarAprovacao(double media) que retorne 'Aprovado' (>= 7) ou 'Reprovado'.",
    },
    {
        "id": "Ex 08", "title": "Maior entre dois números", "level": "Condicionais", "function_hint": "condicional",
        "skills": ["comparação", "if/else", "retorno"], "goal": "Praticar comparação dentro de função.",
        "prompt": "Crie uma função chamada encontrarMaior(int a, int b) que retorne o maior valor.",
    },
    {
        "id": "Ex 09", "title": "Calcular desconto", "level": "Condicionais", "function_hint": "condicional",
        "skills": ["porcentagem", "if/else", "retorno"], "goal": "Aplicar função em compras.",
        "prompt": "Crie uma função chamada calcularDesconto(double valorCompra). Se >= 100, aplique 10%; senão, 5%. Retorne o valor do desconto.",
    },
    {
        "id": "Ex 10", "title": "Positivo, negativo ou zero", "level": "Condicionais", "function_hint": "condicional",
        "skills": ["if/else if", "classificação", "retorno"], "goal": "Ampliar complexidade de decisão.",
        "prompt": "Crie uma função chamada classificarNumero(int numero) que retorne 'Positivo', 'Negativo' ou 'Zero'.",
    },
    {
        "id": "Ex 27", "title": "Inicia com Letra Específica", "level": "Condicionais", "function_hint": "condicional", 
        "skills": ["String", "startsWith", "if/else"], "goal": "Usar condições com métodos de String.", 
        "prompt": "Crie uma função chamada verificarInicial(String texto, char letra) que retorne true se começar com a letra, ou false caso contrário."
    },

    # --- LOOPS ---
    {
        "id": "Ex 11", "title": "Soma de 1 até N", "level": "Loops", "function_hint": "loop",
        "skills": ["for", "acumulador", "retorno"], "goal": "Introduzir repetição dentro de função.",
        "prompt": "Crie uma função chamada somarAteN(int n) que retorne a soma de 1 até N.",
    },
    {
        "id": "Ex 12", "title": "Calcula fatorial", "level": "Loops", "function_hint": "loop",
        "skills": ["for", "multiplicação", "retorno"], "goal": "Praticar loop com multiplicação.",
        "prompt": "Crie uma função chamada calcularFatorial(int n) que retorne seu fatorial.",
    },
    {
        "id": "Ex 13", "title": "Conta de 1 até N", "level": "Loops", "function_hint": "void",
        "skills": ["loop", "impressão", "void"], "goal": "Usar repetição sem retorno.",
        "prompt": "Crie uma função void chamada contarAteN(int n) que imprima de 1 até N.",
    },
    {
        "id": "Ex 14", "title": "Soma pares até N", "level": "Loops", "function_hint": "loop",
        "skills": ["for", "if", "acumulador"], "goal": "Combinar filtro e repetição.",
        "prompt": "Crie uma função chamada somarParesAteN(int n) que retorne a soma dos pares de 1 até N.",
    },
    {
        "id": "Ex 15", "title": "Gera tabuada", "level": "Loops", "function_hint": "void",
        "skills": ["for", "multiplicação", "void"], "goal": "Gerar sequência útil.",
        "prompt": "Crie uma função void chamada gerarTabuada(int n) que exiba a tabuada (1 a 10) do número.",
    },
    {
        "id": "Ex 28", "title": "Inverter Texto", "level": "Loops", "function_hint": "loop", 
        "skills": ["String", "for", "concatenação"], "goal": "Percorrer uma String de trás para frente.", 
        "prompt": "Crie uma função chamada inverterTexto(String texto) que retorne a palavra escrita de trás para frente."
    },

    # --- LOOPS E CONDICIONAIS ---
    {
        "id": "Ex 16", "title": "Conta pares até N", "level": "Funções com loop e condicional", "function_hint": "combinada",
        "skills": ["for", "if", "contador", "retorno"], "goal": "Combinar repetição e decisão.",
        "prompt": "Crie uma função chamada contarParesAteN(int n) que retorne QUANTOS pares existem entre 1 e N.",
    },
    {
        "id": "Ex 17", "title": "Soma ímpares até N", "level": "Funções com loop e condicional", "function_hint": "combinada",
        "skills": ["for", "if", "acumulador"], "goal": "Consolidar condição na repetição.",
        "prompt": "Crie uma função chamada somarImparesAteN(int n) que retorne a SOMA dos ímpares entre 1 e N.",
    },
    {
        "id": "Ex 18", "title": "Verifica se é primo", "level": "Funções com loop e condicional", "function_hint": "combinada",
        "skills": ["for", "if", "boolean"], "goal": "Lógica elaborada com divisão.",
        "prompt": "Crie uma função chamada verificarPrimo(int n) que retorne true se for primo, ou false caso contrário.",
    },
    {
        "id": "Ex 19", "title": "Média de N notas", "level": "Funções com loop e condicional", "function_hint": "combinada",
        "skills": ["loop", "acumulador", "média"], "goal": "Processar vários valores lidos via Scanner/JOptionPane.",
        "prompt": "Crie uma função chamada calcularMediaMultipla(int quantidadeNotas) que leia as notas e retorne a média final.",
    },
    {
        "id": "Ex 20", "title": "Situação da turma", "level": "Funções com loop e condicional", "function_hint": "combinada",
        "skills": ["média", "if/else", "organização"], "goal": "Dividir problema em funções menores.",
        "prompt": "Crie calcularMedia(n1,n2) e verificarSituacao(media). Use a primeira dentro da segunda para informar o status do aluno.",
    },
    {
        "id": "Ex 29", "title": "Contar Vogais", "level": "Funções com loop e condicional", "function_hint": "combinada", 
        "skills": ["String", "for", "if", "charAt"], "goal": "Combinar laços e condições inspecionando caracteres.", 
        "prompt": "Crie uma função chamada contarVogais(String texto) que retorne a quantidade de vogais presentes na palavra."
    },

    # --- DESAFIADOR ---
    {
        "id": "Ex 21", "title": "[Desafio] Calculadora Modular", "level": "Desafiador", "function_hint": "combinada",
        "skills": ["menu", "funções separadas", "operações"], "goal": "Várias funções em um programa.",
        "prompt": "Crie uma calculadora com funções separadas: somar(), subtrair(), multiplicar(), dividir(). Use um menu para o usuário escolher.",
    },
    {
        "id": "Ex 22", "title": "[Desafio] Sistema de Notas", "level": "Desafiador", "function_hint": "combinada",
        "skills": ["funções", "média", "organização"], "goal": "Modularizar problema completo.",
        "prompt": "Crie um programa com funções separadas para: ler notas, calcular média, verificar aprovação e exibir boletim final.",
    },
    {
        "id": "Ex 23", "title": "[Desafio] Sequência de Fibonacci", "level": "Desafiador", "function_hint": "loop",
        "skills": ["loop", "sequência", "void"], "goal": "Lógica sequencial complexa.",
        "prompt": "Crie uma função chamada exibirFibonacci(int n) que imprima os N primeiros termos da sequência de Fibonacci.",
    },
    {
        "id": "Ex 24", "title": "[Desafio] Soma dos dígitos", "level": "Desafiador", "function_hint": "loop",
        "skills": ["while", "divisão", "módulo"], "goal": "Manipulação numérica avançada.",
        "prompt": "Crie uma função chamada somarDigitos(int numero) que retorne a soma dos algarismos do número (ex: 123 -> 6).",
    },
    {
        "id": "Ex 25", "title": "[Desafio] Caixa Eletrônico", "level": "Desafiador", "function_hint": "combinada",
        "skills": ["menu", "funções", "regras de negócio"], "goal": "Integrar funções no mundo real.",
        "prompt": "Crie funções globais (ou em uma classe separada): verSaldo(), depositar(valor), sacar(valor). Impessa o saque se o saldo for insuficiente.",
    },
    {
        "id": "Ex 30", "title": "[Desafio] Palíndromo", "level": "Desafiador", "function_hint": "combinada", 
        "skills": ["String", "for", "if/else", "lógica reversa"], "goal": "Aplicar lógica avançada de texto.", 
        "prompt": "Crie uma função chamada verificarPalindromo(String texto) que retorne true se a palavra for um palíndromo (ex: 'arara', 'osso')."
    },
]

# Ordenar exercícios pelo ID para o menu suspenso ficar correto
EXS = sorted(EXS, key=lambda x: x["id"])

# =========================
# ESTILO (CSS)
# =========================
st.markdown(
    """
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 900px; }
    .hero {
        border-radius: 16px; padding: 24px; color: white; margin-bottom: 1.5rem;
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1); text-align: center;
    }
    .hero h1 { margin: 0 0 10px 0; font-size: 2.2rem; font-weight: 800; }
    .hero p { margin: 0; opacity: 0.9; font-size: 1.1rem; }
    .exercise-card {
        border-radius: 12px; padding: 24px; margin-top: 1rem; margin-bottom: 1rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08); background: #ffffff;
    }
    .exercise-title { font-weight: 800; font-size: 1.4rem; margin-bottom: 12px; color: #1e293b;}
    .exercise-chip {
        display: inline-block; padding: 6px 12px; margin-right: 8px; margin-bottom: 8px;
        border-radius: 20px; font-size: 0.85rem; background: #f1f5f9;
        border: 1px solid #e2e8f0; color: #334155; font-weight: 600;
    }
    .section-label { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; font-weight: 800; }
    .small-note { font-size: 1rem; color: #475569; margin-bottom: 16px; }
    .tip-box { 
        background: #f8fafc; border: 2px dashed #94a3b8; border-radius: 10px; 
        padding: 16px; font-family: 'Courier New', monospace; font-size: 1.05rem; 
        color: #0f172a; font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# PERSISTÊNCIA DE DADOS
# =========================
def append_submission(row: dict):
    with FileLock(str(LOCK_PATH)):
        with open(JSONL_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

        df_new = pd.DataFrame([row])
        if CSV_PATH.exists():
            df_old = pd.read_csv(CSV_PATH)
            df_final = pd.concat([df_old, df_new], ignore_index=True)
        else:
            df_final = df_new
        
        df_final.to_csv(CSV_PATH, index=False)

def load_data():
    if CSV_PATH.exists():
        return pd.read_csv(CSV_PATH)
    return pd.DataFrame()

# =========================
# INTERFACE
# =========================
def main():
    with st.sidebar:
        st.title("🧩 Navegação")
        page = st.radio("Acesse:", ["📚 Área do Aluno", "📊 Painel do Professor"])
        st.markdown("---")
        st.caption("Java Methods & Clean Code Practice")

    if page == "📚 Área do Aluno":
        render_student_area()
    else:
        render_teacher_area()

def render_student_area():
    st.markdown(
        """
        <div class="hero">
            <h1>Laboratório de Funções Java ☕</h1>
            <p>Foco de tela: Selecione <b>um</b> exercício por vez, programe na IDE e registre seu progresso!</p>
        </div>
        """, unsafe_allow_html=True
    )

    # Passo 1: O aluno seleciona a dificuldade (Isso filtra a lista)
    st.markdown("### 1. Escolha a trilha")
    selected_level = st.selectbox("Nível de Dificuldade:", LEVEL_ORDER)
    
    # Filtrar exercícios pelo nível selecionado
    filtered_exs = [ex for ex in EXS if ex["level"] == selected_level]

    # Passo 2: O aluno seleciona o exercício específico
    st.markdown("### 2. Escolha o Desafio")
    
    # Criar um dicionário para mapear os títulos para os objetos do exercício
    ex_options = {f"{ex['id']} - {ex['title']}": ex for ex in filtered_exs}
    selected_ex_title = st.selectbox("Exercício Atual:", list(ex_options.keys()))
    
    # Recuperar o exercício selecionado
    ex = ex_options[selected_ex_title]

    st.markdown("---")

    # Renderizar APENAS o card selecionado
    bg_color, text_color = LEVEL_COLORS.get(ex["level"], ("#FFFFFF", "#000000"))
    badge = FUNC_BADGE.get(ex["function_hint"], "")
    skills_html = "".join([f'<span class="exercise-chip">🎯 {s}</span>' for s in ex["skills"]])

    html_card = f"""
    <div class="exercise-card" style="border-left: 8px solid {text_color};">
        <div class="section-label" style="color: {text_color};">{ex['level']}</div>
        <div class="exercise-title">{ex['id']} - {ex['title']}</div>
        <div style="margin-bottom: 16px;">
            <span class="exercise-chip" style="background: #e0f2fe; border-color: #bae6fd;">{badge}</span>
            {skills_html}
        </div>
        <div class="small-note"><strong>Propósito Pedagógico:</strong> {ex['goal']}</div>
        <div class="tip-box">💻 {ex['prompt']}</div>
    </div>
    """
    st.markdown(html_card, unsafe_allow_html=True)

    # Formulário de Submissão anexado ao Card Focado
    st.markdown("#### 📝 Formulário de Conclusão")
    with st.form(key=f"form_{ex['id']}"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Seu Nome ou RA *")
            status = st.radio("Status do Exercício:", STATUS_OPTS)
        with c2:
            dificuldade = st.select_slider("Como você avalia a dificuldade?", options=DIF_OPTS, value="Médio")
            ajuda = st.radio("Consultou IA ou Colegas?", HELP_OPTS, horizontal=True)
        
        comentarios = st.text_area("Anotações ou dúvidas? (Opcional)")
        submit_btn = st.form_submit_button("Registrar Avanço", type="primary", use_container_width=True)

        if submit_btn:
            if not nome.strip():
                st.error("⚠️ Identifique-se com o Nome/RA para registrar o progresso.")
            else:
                row = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "aluno": nome.strip(),
                    "id_exercicio": ex["id"],
                    "nivel": ex["level"],
                    "status": status,
                    "dificuldade": dificuldade,
                    "ajuda": ajuda,
                    "comentarios": comentarios
                }
                append_submission(row)
                st.success(f"Excelente! Progresso no {ex['id']} salvo com sucesso.")
                if status == "✅ Consegui":
                    st.balloons()


def render_teacher_area():
    st.title("📊 Painel do Professor")
    
    pwd = st.text_input("Senha de acesso", type="password")
    
    if pwd != TEACHER_PASS:
        if pwd: st.error("Senha incorreta.")
        st.warning("Área restrita. Insira a senha.")
        return

    st.success("Acesso autorizado.")
    df = load_data()

    if df.empty:
        st.info("O banco de dados está vazio no momento.")
        return

    st.subheader("Visão Geral da Turma")
    col1, col2, col3 = st.columns(3)
    
    total_subs = len(df)
    sucessos = len(df[df["status"] == "✅ Consegui"])
    tx_sucesso = (sucessos / total_subs) * 100 if total_subs > 0 else 0

    col1.metric("Submissões Totais", total_subs)
    col2.metric("Tarefas Concluídas", sucessos)
    col3.metric("Aproveitamento Médio", f"{tx_sucesso:.1f}%")

    st.divider()

    st.subheader("Registro em Tempo Real")
    st.dataframe(df.sort_values(by="timestamp", ascending=False), use_container_width=True)

    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Dados Completos (CSV)",
        data=csv_data,
        file_name='relatorio_funcoes_java.csv',
        mime='text/csv',
    )

if __name__ == "__main__":
    main()
