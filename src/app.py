import sys
import json

# Dependências verificadas no runtime para mensagens claras se não estiverem instaladas
_missing = []
try:
    import pandas as pd
except Exception:
    _missing.append('pandas')
try:
    import streamlit as st
except Exception:
    _missing.append('streamlit')
try:
    import requests
except Exception:
    _missing.append('requests')

if _missing:
    print('Dependências faltando: ' + ', '.join(_missing))
    print('\nSugestão rápida (PowerShell):')
    print('python -m venv .venv')
    print('.\\.venv\\Scripts\\Activate.ps1')
    print('pip install --upgrade pip')
    print('pip install -r requirements.txt')
    sys.exit(1)

# ===== CONFIGURAÇÕES =====
OLLAMA_URL = "http://localhost:11434/api/generate"  # URL do Ollama
MODELO = "gpt-oss"  # Modelo a ser usado (ajuste conforme necessário)

# ===== CARREGAR DADOS =====
#CSVs
historico = pd.read_csv('data/historico_atendimento.csv')
transacoes = pd.read_csv('data/transacoes.csv')

#JSONs
with open('data/perfil_investidor.json', 'r', encoding='utf-8') as f:
    perfil = json.load(f)

with open('data/produtos_financeiros.json', 'r', encoding='utf-8') as f:
    produtos = json.load(f)

# ===== MONTAR CONTEXTO =====
contexto = f"""
CLIENTE: {perfil['nome']} - {perfil['idade']} anos, perfil {perfil['perfil_investidor']}
OBJETIVO: {perfil['objetivo_principal']}
PATRIMONIO: R${perfil['patrimonio_total']} | RESERVA: R${perfil['reserva_emergencia_atual']}

TRANSACOES RECENTES:
{transacoes.to_string(index=False)}

ATENDIMENTOS ANTERIORES:
{historico.to_string(index=False)}

PRODUTOS FINANCEIROS DISPONIVEIS:
{json.dumps(produtos, indent=2, ensure_ascii=False)}
"""

# ===== SYSTEM PROMPT =====
SYSTEM_PROMPT = """Você é o Agente Fin, um educador financeiro inteligente.
OBJETIVO:
Seu objetivo é ensinar conceitos de finanças pessoais de forma simples, usando dados do cliente como exemplos práticos.

REGRAS:
1. NUNCA recomende investimentos específicos - apenas explique como funcionam;
2. JAMAIS responda a perguntas fora do tema ensino de finanças pessoais;
    Quando ocorer, diga: "Essa pergunta é interessante, mas vamos focar em finanças pessoais por enquanto.";
3. Use os dados fornecidos para dar exemplos personalizados;
4. Linguagem simples, como se explicasse para um amigo;
5. Se não souber algo, admita:  "Não tenho essa informação, mas posso explicar...";
6. Sempre pergunte se o cliente entendeu;
"""

# ===== CHAMAR OLLAMA =====
def perguntar(msg):
    prompt = f"""
    {SYSTEM_PROMPT}

    CONTEXTO DO CLIENTE:
    {contexto}

    Pergunta: {msg}"""

    r = requests.post(
        OLLAMA_URL,
        json={
            "model": MODELO,
            "prompt": prompt,
            "stream": False
        })

    data = r.json()
    print(data)
    if 'response' in data:
        return data['response']
    raise RuntimeError(f"Erro na API Ollama: {data}")

# ===== INTERFACE SIMPLES =====
st.title("Agente Fin - Educador Financeiro")

if pergunta := st.chat_input("Faça sua pergunta sobre finanças pessoais:"):
    st.chat_message("user").write(pergunta)
    with st.spinner("Pensando..."):
        st.chat_message("assistant").write(perguntar(pergunta))