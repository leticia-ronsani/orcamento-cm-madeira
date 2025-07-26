import streamlit as st
import pandas as pd
import os
from fpdf import FPDF

# Arquivos CSV
CLIENTES_CSV = "clientes.csv"
PRODUTOS_CSV = "produtos.csv"

# Carregar dados
def carregar_clientes():
    if os.path.exists(CLIENTES_CSV) and os.path.getsize(CLIENTES_CSV) > 0:
        return pd.read_csv(CLIENTES_CSV)
    else:
        return pd.DataFrame(columns=["Nome", "Telefone", "Documento", "Endereço"])

def carregar_produtos():
    if os.path.exists(PRODUTOS_CSV) and os.path.getsize(PRODUTOS_CSV) > 0:
        return pd.read_csv(PRODUTOS_CSV)
    else:
        return pd.DataFrame(columns=["Produto", "Unidade", "Preço", "Estoque"])

# Salvar cliente
def salvar_cliente(dados):
    df = carregar_clientes()
    df = pd.concat([df, pd.DataFrame([dados])], ignore_index=True)
    df.to_csv(CLIENTES_CSV, index=False)

# Salvar produto
def salvar_produto(dados):
    df = carregar_produtos()
    df = pd.concat([df, pd.DataFrame([dados])], ignore_index=True)
    df.to_csv(PRODUTOS_CSV, index=False)

# Gerar PDF
def gerar_pdf(cliente, produtos_selecionados, desconto, prazo_validade, forma_pagamento):
    pdf = FPDF()
    pdf.add_page()

    # Adiciona a logo no topo esquerdo
    pdf.image("logo.png", x=10, y=8, w=50)

    pdf.set_font("Arial", 'B', 16)
    pdf.ln(20)  # espaço depois da logo
    pdf.cell(0, 10, "Orçamento - CM Casa da Madeira", ln=1, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Cliente: {cliente['Nome']}", ln=1)
    pdf.cell(0, 10, f"Telefone: {cliente['Telefone']}", ln=1)
    pdf.cell(0, 10, f"Documento: {cliente['Documento']}", ln=1)
    pdf.cell(0, 10, f"Endereço: {cliente['Endereço']}", ln=1)
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(40, 10, "Produto", border=1)
    pdf.cell(30, 10, "Qtd", border=1)
    pdf.cell(40, 10, "Preço unit.", border=1)
    pdf.cell(40, 10, "Total", border=1)
    pdf.ln()

    total_geral = 0
    for idx, row in produtos_selecionados.iterrows():
        total = row['Quantidade'] * row['Preço']
        total_geral += total
        pdf.cell(40, 10, str(row['Produto']), border=1)
        pdf.cell(30, 10, str(row['Quantidade']), border=1)
        pdf.cell(40, 10, f"R$ {row['Preço']:.2f}", border=1)
        pdf.cell(40, 10, f"R$ {total:.2f}", border=1)
        pdf.ln()

    pdf.ln(5)
    valor_desconto = total_geral * desconto / 100
    valor_final = total_geral - valor_desconto
    pdf.cell(0, 10, f"Desconto: {desconto:.2f}% - R$ {valor_desconto:.2f}", ln=1)
    pdf.cell(0, 10, f"Total com desconto: R$ {valor_final:.2f}", ln=1)
    pdf.ln(10)

    pdf.cell(0, 10, f"Prazo de validade: {prazo_validade}", ln=1)
    pdf.cell(0, 10, f"Forma de pagamento: {forma_pagamento}", ln=1)

    return pdf.output(dest='S').encode('latin1')

# Interface principal
def main():
    st.title("📦 Sistema de Orçamentos - CM Casa da Madeira")

    menu = st.sidebar.selectbox("Menu", ["Cadastrar Cliente", "Cadastrar Produto", "Fazer Orçamento"])

    if menu == "Cadastrar Cliente":
        st.subheader("👤 Cadastro de Cliente")
        nome = st.text_input("Nome do cliente")
        telefone = st.text_input("Telefone")
        documento = st.text_input("CPF ou CNPJ")
        endereco = st.text_input("Endereço completo")

        if st.button("Salvar Cliente"):
            if nome and telefone:
                dados = {"Nome": nome, "Telefone": telefone, "Documento": documento, "Endereço": endereco}
                salvar_cliente(dados)
                st.success("✅ Cliente salvo com sucesso!")
            else:
                st.warning("Preencha pelo menos nome e telefone.")

    elif menu == "Cadastrar Produto":
        st.subheader("📦 Cadastro de Produto")
        produto = st.text_input("Nome do produto")
        unidade = st.text_input("Unidade (ex: m2, peça)")
        preco = st.number_input("Preço unitário (R$)", min_value=0.0, format="%.2f")
        estoque = st.number_input("Estoque disponível", min_value=0, step=1)

        if st.button("Salvar Produto"):
            if produto:
                dados = {"Produto": produto, "Unidade": unidade, "Preço": preco, "Estoque": estoque}
                salvar_produto(dados)
                st.success("✅ Produto salvo com sucesso!")
            else:
                st.warning("Informe o nome do produto.")

    elif menu == "Fazer Orçamento":
        st.subheader("🧾 Fazer Orçamento")

        clientes = carregar_clientes()
        produtos = carregar_produtos()

        if clientes.empty:
            st.warning("⚠️ Nenhum cliente cadastrado.")
            return
        if produtos.empty:
            st.warning("⚠️ Nenhum produto cadastrado.")
            return

        cliente_nome = st.selectbox("Selecione o cliente", clientes["Nome"].tolist())
        cliente = clientes[clientes["Nome"] == cliente_nome].iloc[0]

        produtos_selecionados = []
        st.write("Selecione os produtos e as quantidades:")

        for idx, row in produtos.iterrows():
            selecionado = st.checkbox(f"{row['Produto']} (Estoque: {row['Estoque']} {row['Unidade']})", key=idx)
            if selecionado:
                quantidade = st.number_input(f"Quantidade para {row['Produto']}", min_value=1, max_value=int(row['Estoque']), key=f"qtd_{idx}")
                produtos_selecionados.append({
                    "Produto": row['Produto'],
                    "Quantidade": quantidade,
                    "Preço": row['Preço']
                })

        if len(produtos_selecionados) == 0:
            st.warning("⚠️ Selecione pelo menos um produto.")
            return

        desconto = st.number_input("Desconto (%)", min_value=0.0, max_value=100.0, value=0.0)
        prazo_validade = st.text_input("Prazo de validade")
        forma_pagamento = st.text_input("Forma de pagamento")

        if st.button("Gerar Orçamento PDF"):
            pdf_bytes = gerar_pdf(cliente, pd.DataFrame(produtos_selecionados), desconto, prazo_validade, forma_pagamento)
            st.download_button("📥 Baixar Orçamento em PDF", data=pdf_bytes, file_name="orcamento.pdf", mime="application/pdf")

if __name__ == "__main__":
    main()
