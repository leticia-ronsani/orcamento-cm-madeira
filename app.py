import streamlit as st
import pandas as pd
from fpdf import FPDF
import os

# Arquivos CSV usados como banco de dados
CLIENTES_CSV = "clientes.csv"
PRODUTOS_CSV = "produtos.csv"

# Página
st.set_page_config(page_title="CM - Casa da Madeira", layout="wide")
st.title("📋 Sistema de Orçamentos - CM Casa da Madeira")

# Inicializar arquivos se não existirem
for arquivo in [CLIENTES_CSV, PRODUTOS_CSV]:
    if not os.path.exists(arquivo):
        pd.DataFrame().to_csv(arquivo, index=False)

# Menu lateral
menu = st.sidebar.selectbox("Menu", ["Cadastrar Cliente", "Cadastrar Produto", "Gerar Orçamento"])

# -------- 1. CADASTRO DE CLIENTES --------
if menu == "Cadastrar Cliente":
    st.subheader("👤 Cadastro de Cliente")
    nome = st.text_input("Nome do cliente")
    telefone = st.text_input("Telefone")
    documento = st.text_input("CPF ou CNPJ")
    endereco = st.text_input("Endereço completo")

    if st.button("Salvar Cliente"):
        dados = {
            "Nome": nome,
            "Telefone": telefone,
            "Documento": documento,
            "Endereço": endereco
        }
        if os.path.exists(CLIENTES_CSV) and os.path.getsize(CLIENTES_CSV) > 0:
            df = pd.read_csv(CLIENTES_CSV)
        else:
            df = pd.DataFrame(columns=dados.keys())

        df = df.append(dados, ignore_index=True)
        df.to_csv(CLIENTES_CSV, index=False)
        st.success("✅ Cliente salvo com sucesso!")

# -------- 2. CADASTRO DE PRODUTOS --------
elif menu == "Cadastrar Produto":
    st.subheader("📦 Cadastro de Produto")
    nome = st.text_input("Nome do produto")
    unidade = st.selectbox("Unidade", ["m²", "peça"])
    preco = st.number_input("Preço unitário (R$)", min_value=0.01, step=0.01)
    estoque = st.number_input("Quantidade em estoque", min_value=0, step=1)

    if st.button("Salvar Produto"):
        dados = {
            "Produto": nome,
            "Unidade": unidade,
            "Preço": preco,
            "Estoque": estoque
        }
        if os.path.exists(PRODUTOS_CSV) and os.path.getsize(PRODUTOS_CSV) > 0:
            df = pd.read_csv(PRODUTOS_CSV)
        else:
            df = pd.DataFrame(columns=dados.keys())

        df = df.append(dados, ignore_index=True)
        df.to_csv(PRODUTOS_CSV, index=False)
        st.success("✅ Produto salvo com sucesso!")

# -------- 3. GERAR ORÇAMENTO --------
elif menu == "Gerar Orçamento":
    st.subheader("🧾 Gerar Orçamento")
    if os.path.exists(CLIENTES_CSV) and os.path.exists(PRODUTOS_CSV):
        clientes = pd.read_csv(CLIENTES_CSV)
        produtos = pd.read_csv(PRODUTOS_CSV)
    else:
        st.warning("Cadastre clientes e produtos primeiro!")
        st.stop()

    if clientes.empty or produtos.empty:
        st.warning("Cadastre clientes e produtos primeiro!")
        st.stop()

    cliente = st.selectbox("Selecionar cliente", clientes["Nome"])
    forma_pagamento = st.selectbox("Forma de pagamento", ["PIX", "Dinheiro", "Cartão"])
    validade = st.text_input("Prazo de validade (ex: 10 dias)")
    numero_orcamento = st.number_input("Número do orçamento", step=1)

    st.markdown("### Produtos do orçamento")
    itens = []
    for i in range(3):  # até 3 itens por orçamento
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            produto = st.selectbox(f"Produto {i+1}", produtos["Produto"], key=f"prod_{i}")
        with col2:
            qtd = st.number_input("Qtd", min_value=0, step=1, key=f"qtd_{i}")
        with col3:
            desc = st.number_input("Desconto (R$)", min_value=0.0, step=0.01, key=f"desc_{i}")

        if qtd > 0:
            linha = produtos[produtos["Produto"] == produto].iloc[0]
            total = (linha["Preço"] * qtd) - desc
            itens.append({
                "produto": produto,
                "unidade": linha["Unidade"],
                "qtd": qtd,
                "preco": linha["Preço"],
                "desc": desc,
                "total": total
            })

    if st.button("Gerar PDF"):
        pdf = FPDF()
