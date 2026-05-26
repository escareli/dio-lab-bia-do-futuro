import pandas as pd
import json
import streamlit as st
import requests

# ===== CONFIGURAÇÕES =====
OLLAMA_URL = "http://localhost:11434/api/generate"  # URL do Ollama
MODELO = "gtp-oss"

# ===== CARREGAR DADOS =====
#CSVs
historico = pd.read_csv('data/historico_atendimento.csv')
transacoes = pd.read_csv('data/transacoes.csv')

#JSONs
with open('data/perfil_investidor.csv', 'r', enconding='utf-8') as f:
    perfil = json.load(f)

with open('data/produtos_financeiros.csv', 'r', enconding='utf-8') as f:
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
    
    return r.json()['response']

    # Aqui você chamaria a API do Ollama, passando o SYSTEM_PROMPT + contexto + pergunta
    # Exemplo (pseudocódigo):
    # resposta = ollama_api.call(system_prompt=SYSTEM_PROMPT, contexto=contexto, pergunta=pergunta)
    # return resposta
    # pass  # Substitua por chamada real à API

# ===== INTERFACE SIMPLES =====
st.title("Agente Fin - Educador Financeiro")

if pergunta := st.chat_input("Faça sua pergunta sobre finanças pessoais:"):
    st.chat_message("user").write(pergunta)
    with st.spinner("Pensando..."):
        st.chat_message("agent").write(perguntar(pergunta))