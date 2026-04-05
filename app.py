import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from filelock import FileLock

# =========================
# CONFIG
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

# Para testar, defina uma senha padrão se não houver no st.secrets
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
# EXERCÍCIOS
# =========================
# =========================
# EXERCÍCIOS
# =========================
EXS = [
    {
        "id": "Ex 01",
        "title": "Criar função que mostra uma mensagem",
        "level": "Fundamentos",
        "function_hint": "void",
        "skills": ["função", "void", "organização"],
        "goal": "Entender que uma função pode executar uma ação sem retornar valor.",
        "prompt": "Crie uma função chamada mostrarMensagem() que exiba a frase 'Olá, Java!'.",
    },
    {
        "id": "Ex 02",
        "title": "Criar função que retorna o dobro",
        "level": "Fundamentos",
        "function_hint": "com retorno",
        "skills": ["retorno", "parâmetro", "cálculo simples"],
        "goal": "Praticar função com parâmetro e retorno.",
        "prompt": "Crie uma função que receba um número inteiro e retorne o seu dobro.",
    },
    {
        "id": "Ex 03",
        "title": "Função para calcular soma de dois números",
        "level": "Fundamentos",
        "function_hint": "com retorno",
        "skills": ["parâmetros", "retorno", "operações"],
        "goal": "Trabalhar múltiplos parâmetros em uma função.",
        "prompt": "Crie uma função que receba dois números inteiros e retorne a soma deles.",
    },
    {
        "id": "Ex 04",
        "title": "Função para calcular média de três notas",
        "level": "Fundamentos",
        "function_hint": "com retorno",
        "skills": ["média", "double", "retorno"],
        "goal": "Aplicar função em um problema escolar simples.",
        "prompt": "Crie uma função que receba três notas e retorne a média do aluno.",
    },
    {
        "id": "Ex 05",
        "title": "Função para calcular área de um retângulo",
        "level": "Fundamentos",
        "function_hint": "com parâmetro",
        "skills": ["multiplicação", "parâmetros", "retorno"],
        "goal": "Usar função para resolver um problema geométrico simples.",
        "prompt": "Crie uma função que receba base e altura e retorne a área de um retângulo.",
    },
    {
        "id": "Ex 06",
        "title": "Função que verifica se número é par",
        "level": "Condicionais",
        "function_hint": "condicional",
        "skills": ["if", "módulo", "retorno"],
        "goal": "Introduzir decisão dentro de uma função.",
        "prompt": "Crie uma função que receba um número inteiro e retorne 'Par' ou 'Ímpar'.",
    },
    {
        "id": "Ex 07",
        "title": "Função que verifica aprovação",
        "level": "Condicionais",
        "function_hint": "condicional",
        "skills": ["if/else", "média", "retorno"],
        "goal": "Usar função para tomar decisão com base em regra de negócio simples.",
        "prompt": "Crie uma função que receba a média de um aluno e retorne 'Aprovado' se a média for maior ou igual a 7, ou 'Reprovado' caso contrário.",
    },
    {
        "id": "Ex 08",
        "title": "Função que retorna o maior entre dois números",
        "level": "Condicionais",
        "function_hint": "condicional",
        "skills": ["comparação", "if/else", "retorno"],
        "goal": "Praticar comparação dentro de função.",
        "prompt": "Crie uma função que receba dois números inteiros e retorne o maior deles.",
    },
    {
        "id": "Ex 09",
        "title": "Função para calcular desconto",
        "level": "Condicionais",
        "function_hint": "condicional",
        "skills": ["porcentagem", "if/else", "retorno"],
        "goal": "Aplicar função em cenário real de compras.",
        "prompt": "Crie uma função que receba o valor de uma compra. Se o valor for maior ou igual a 100, aplique 10% de desconto; caso contrário, aplique 5%. A função deve retornar o valor do desconto.",
    },
    {
        "id": "Ex 10",
        "title": "Função que verifica se número é positivo, negativo ou zero",
        "level": "Condicionais",
        "function_hint": "condicional",
        "skills": ["if/else if/else", "classificação", "retorno"],
        "goal": "Ampliar a complexidade da decisão dentro de uma função.",
        "prompt": "Crie uma função que receba um número e retorne 'Positivo', 'Negativo' ou 'Zero'.",
    },
    {
        "id": "Ex 11",
        "title": "Função que soma de 1 até N",
        "level": "Loops",
        "function_hint": "loop",
        "skills": ["for", "acumulador", "retorno"],
        "goal": "Introduzir repetição dentro de uma função.",
        "prompt": "Crie uma função que receba um número inteiro N e retorne a soma dos números de 1 até N.",
    },
    {
        "id": "Ex 12",
        "title": "Função que calcula fatorial",
        "level": "Loops",
        "function_hint": "loop",
        "skills": ["for", "multiplicação acumulada", "retorno"],
        "goal": "Praticar loop com multiplicação dentro de função.",
        "prompt": "Crie uma função que receba um número inteiro e retorne o seu fatorial.",
    },
    {
        "id": "Ex 13",
        "title": "Função que conta de 1 até N",
        "level": "Loops",
        "function_hint": "void",
        "skills": ["loop", "impressão", "void"],
        "goal": "Mostrar que uma função pode usar repetição e apenas exibir resultados.",
        "prompt": "Crie uma função void que receba um número inteiro N e mostre os números de 1 até N.",
    },
    {
        "id": "Ex 14",
        "title": "Função que soma apenas números pares até N",
        "level": "Loops",
        "function_hint": "loop",
        "skills": ["for", "if", "acumulador"],
        "goal": "Combinar filtro simples e repetição.",
        "prompt": "Crie uma função que receba um número inteiro N e retorne a soma de todos os números pares entre 1 e N.",
    },
    {
        "id": "Ex 15",
        "title": "Função que gera tabuada",
        "level": "Loops",
        "function_hint": "void",
        "skills": ["for", "multiplicação", "void"],
        "goal": "Usar loop dentro de função para gerar uma sequência útil.",
        "prompt": "Crie uma função void que receba um número e exiba a sua tabuada de 1 até 10.",
    },
    {
        "id": "Ex 16",
        "title": "Função que conta quantos pares existem até N",
        "level": "Funções com loop e condicional",
        "function_hint": "combinada",
        "skills": ["for", "if", "contador", "retorno"],
        "goal": "Combinar repetição e decisão dentro de uma função.",
        "prompt": "Crie uma função que receba um número inteiro N e retorne quantos números pares existem entre 1 e N.",
    },
    {
        "id": "Ex 17",
        "title": "Função que soma apenas ímpares até N",
        "level": "Funções com loop e condicional",
        "function_hint": "combinada",
        "skills": ["for", "if", "acumulador"],
        "goal": "Consolidar o uso de condição dentro de repetição.",
        "prompt": "Crie uma função que receba um número inteiro N e retorne a soma de todos os números ímpares entre 1 e N.",
    },
    {
        "id": "Ex 18",
        "title": "Função que verifica se um número é primo",
        "level": "Funções com loop e condicional",
        "function_hint": "combinada",
        "skills": ["divisibilidade", "for", "if", "boolean"],
        "goal": "Explorar lógica mais elaborada dentro de uma função.",
        "prompt": "Crie uma função que receba um número inteiro e retorne se ele é primo ou não.",
    },
    {
        "id": "Ex 19",
        "title": "Função que calcula média de N notas",
        "level": "Funções com loop e condicional",
        "function_hint": "combinada",
        "skills": ["loop", "acumulador", "média"],
        "goal": "Usar repetição para processar vários valores e retornar resultado final.",
        "prompt": "Crie uma função que receba a quantidade de notas e, com auxílio do JOptionPane, leia essas notas e retorne a média final.",
    },
    {
        "id": "Ex 20",
        "title": "Função que informa situação da turma",
        "level": "Funções com loop e condicional",
        "function_hint": "combinada",
        "skills": ["média", "if/else", "organização"],
        "goal": "Dividir um problema maior em funções menores.",
        "prompt": "Crie uma função para calcular a média de um aluno e outra função para informar se ele foi aprovado, em recuperação ou reprovado.",
    },
    {
        "id": "Ex 21",
        "title": "[Desafiador] Calculadora com funções",
        "level": "Desafiador",
        "function_hint": "combinada",
        "skills": ["menu", "funções", "operações"],
        "goal": "Usar várias funções em um único programa.",
        "prompt": "Crie uma calculadora com funções separadas para somar, subtrair, multiplicar e dividir. O usuário escolhe a operação e informa dois números.",
    },
    {
        "id": "Ex 22",
        "title": "[Desafiador] Sistema de notas modular",
        "level": "Desafiador",
        "function_hint": "combinada",
        "skills": ["funções", "média", "decisão", "organização"],
        "goal": "Modularizar um problema completo usando várias funções.",
        "prompt": "Crie um programa com funções separadas para ler notas, calcular média, verificar aprovação e exibir o resultado final.",
    },
    {
        "id": "Ex 23",
        "title": "[Desafiador] Sequência de Fibonacci",
        "level": "Desafiador",
        "function_hint": "loop",
        "skills": ["loop", "sequência", "void ou retorno"],
        "goal": "Trabalhar lógica sequencial mais desafiadora dentro de função.",
        "prompt": "Crie uma função que receba um número N e exiba os N primeiros termos da sequência de Fibonacci.",
    },
    {
        "id": "Ex 24",
        "title": "[Desafiador] Soma dos dígitos",
        "level": "Desafiador",
        "function_hint": "loop",
        "skills": ["while", "divisão inteira", "módulo"],
        "goal": "Aplicar repetição em manipulação numérica.",
        "prompt": "Crie uma função que receba um número inteiro e retorne a soma dos seus dígitos.",
    },
    {
        "id": "Ex 25",
        "title": "[Desafiador] Caixa eletrônico simples",
        "level": "Desafiador",
        "function_hint": "combinada",
        "skills": ["menu", "saldo", "funções", "regras"],
        "goal": "Integrar várias funções em uma situação do mundo real.",
        "prompt": "Crie um sistema simples de caixa eletrônico com funções para ver saldo, depositar e sacar. O programa deve validar se há saldo suficiente para o saque.",
    },
]

# =========================
# ESTILO (CSS)
# =========================
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1000px;
    }
    .hero {
        border-radius: 20px;
        padding: 24px 28px;
        background: linear-gradient(135deg, #111827 0%, #1d4ed8 45%, #06b6d4 100%);
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 20px rgba(15, 23, 42, 0.15);
    }
    .hero h1 { margin: 0 0 8px 0; font-size: 2.2rem; font-weight: 800; }
    .hero p { margin: 0; opacity: 0.9; font-size: 1.1rem; }
    
    .exercise-card {
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 5px; /* Reduzido para aproximar do botão de expandir */
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .exercise-title { font-weight: 800; font-size: 1.25rem; margin-bottom: 10px; color: #1e293b;}
    .exercise-chip {
        display: inline-block; padding: 4px 10px; margin-right: 6px; margin-bottom: 6px;
        border-radius: 20px; font-size: 0.82rem; background: rgba(255,255,255,0.7);
        border: 1px solid rgba(15,23,42,0.1); color: #334155; font-weight: 500;
    }
    .section-label { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; font-weight: 700; }
    .small-note { font-size: 0.95rem; color: #475569; margin-bottom: 12px; }
    .tip-box { background: rgba(255,255,255,0.6); border: 1px dashed #94a3b8; border-radius: 10px; padding: 14px; font-family: monospace; font-size: 1rem; color: #0f172a;}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# PERSISTÊNCIA
# =========================
def append_submission(row: dict):
    """Salva a submissão no JSONL e atualiza o arquivo CSV de forma segura."""
    with FileLock(str(LOCK_PATH)):
        # 1. Salva linha a linha no JSONL (mais seguro para concorrência)
        with open(JSONL_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

        # 2. Atualiza o CSV
        df_new = pd.DataFrame([row])
        if CSV_PATH.exists():
            df_old = pd.read_csv(CSV_PATH)
            df_final = pd.concat([df_old, df_new], ignore_index=True)
        else:
            df_final = df_new
        
        df_final.to_csv(CSV_PATH, index=False)

def load_data():
    """Carrega os dados para o painel do professor."""
    if CSV_PATH.exists():
        return pd.read_csv(CSV_PATH)
    return pd.DataFrame()

# =========================
# INTERFACE PRINCIPAL
# =========================
def main():
    # Menu lateral
    with st.sidebar:
        st.title("🧩 Navegação")
        page = st.radio("Selecione a visualização:", ["📚 Área do Aluno", "📊 Painel do Professor"])
        
        st.markdown("---")
        st.caption("Desenvolvido para consolidar o aprendizado em Java.")

    # Roteamento
    if page == "📚 Área do Aluno":
        render_student_area()
    else:
        render_teacher_area()

def render_student_area():
    # Cabeçalho da página
    st.markdown(
        """
        <div class="hero">
            <h1>Java — Funções na Prática ☕</h1>
            <p>Escolha um exercício, programe na sua IDE e registre seu progresso aqui!</p>
        </div>
        """, unsafe_allow_html=True
    )

    # Filtros para melhorar UX
    col1, col2 = st.columns([2, 1])
    with col1:
        search_term = st.text_input("🔍 Buscar exercício por palavra-chave...", placeholder="Ex: tabuada, soma, media...")
    with col2:
        selected_level = st.selectbox("🎚️ Filtrar por Dificuldade", ["Todos"] + LEVEL_ORDER)

    st.write("") # Espaço em branco

    # Filtragem da lista
    filtered_exs = [
        ex for ex in EXS 
        if (selected_level == "Todos" or ex["level"] == selected_level) and 
           (search_term.lower() in ex["title"].lower() or search_term.lower() in ex["prompt"].lower())
    ]

    if not filtered_exs:
        st.info("Nenhum exercício encontrado com esses filtros.")
        return

    # Renderizar exercícios
    for ex in filtered_exs:
        bg_color, text_color = LEVEL_COLORS.get(ex["level"], ("#FFFFFF", "#000000"))
        badge = FUNC_BADGE.get(ex["function_hint"], "")
        skills_html = "".join([f'<span class="exercise-chip">🎯 {s}</span>' for s in ex["skills"]])

        # HTML do Card
        html_card = f"""
        <div class="exercise-card" style="background-color: {bg_color}; border-left: 6px solid {text_color};">
            <div class="section-label" style="color: {text_color};">{ex['level']}</div>
            <div class="exercise-title">{ex['id']} - {ex['title']}</div>
            <div style="margin-bottom: 12px;">
                <span class="exercise-chip">{badge}</span>
                {skills_html}
            </div>
            <div class="small-note"><strong>🎯 Objetivo:</strong> {ex['goal']}</div>
            <div class="tip-box">💻 {ex['prompt']}</div>
        </div>
        """
        st.markdown(html_card, unsafe_allow_html=True)

        # Formulário retrátil (Expander) anexado embaixo do card
        with st.expander(f"🚀 Enviar resultado do {ex['id']}", expanded=False):
            with st.form(key=f"form_{ex['id']}"):
                st.write("**Registre sua experiência:**")
                
                c1, c2 = st.columns(2)
                with c1:
                    nome = st.text_input("Seu Nome ou RA *")
                    status = st.radio("Como você se saiu?", STATUS_OPTS, horizontal=True)
                with c2:
                    dificuldade = st.select_slider("Nível de Dificuldade que sentiu", options=DIF_OPTS, value="Médio")
                    ajuda = st.radio("Precisou de ajuda? (Colegas ou IA)", HELP_OPTS, horizontal=True)
                
                comentarios = st.text_area("Dúvidas ou comentários (Opcional)", placeholder="Sua dúvida pode ajudar a melhorar a aula!")
                
                submit_btn = st.form_submit_button("Submeter Exercício", type="primary", use_container_width=True)

                if submit_btn:
                    if not nome.strip():
                        st.error("⚠️ O campo Nome/RA é obrigatório.")
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
                        st.success(f"Feedback do {ex['id']} registrado com sucesso!")
                        
                        # Gatilho de gamificação
                        if status == "✅ Consegui":
                            st.balloons()

def render_teacher_area():
    st.title("📊 Painel do Professor")
    
    # Proteção simples por senha
    pwd = st.text_input("Senha de acesso", type="password")
    
    if pwd != TEACHER_PASS:
        if pwd:
            st.error("Senha incorreta.")
        st.warning("Insira a senha para visualizar os resultados.")
        return

    st.success("Acesso autorizado.")
    df = load_data()

    if df.empty:
        st.info("Ainda não há submissões registradas pelos alunos.")
        return

    # Métricas Globais
    st.subheader("Métricas Rápidas")
    col1, col2, col3 = st.columns(3)
    
    total_subs = len(df)
    sucessos = len(df[df["status"] == "✅ Consegui"])
    tx_sucesso = (sucessos / total_subs) * 100 if total_subs > 0 else 0

    col1.metric("Total de Submissões", total_subs)
    col2.metric("Concluídos com Sucesso", sucessos)
    col3.metric("Taxa de Sucesso", f"{tx_sucesso:.1f}%")

    st.divider()

    # Visualização de Dados
    st.subheader("Últimas Submissões")
    st.dataframe(df.sort_values(by="timestamp", ascending=False), use_container_width=True)

    # Botão de Download
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Dados (CSV)",
        data=csv_data,
        file_name='resultado_alunos_java.csv',
        mime='text/csv',
    )

if __name__ == "__main__":
    main()
