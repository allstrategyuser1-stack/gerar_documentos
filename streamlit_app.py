import streamlit as st
import random
import csv
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
import io

st.set_page_config(page_title="Gerador de documentos fictícios (Fluxo)", layout="wide")
st.title("Gerador de documentos fictícios (Fluxo)")

# --- Função para gerar o template em memória ---
def gerar_template_csv(tipo):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["codigo", "nome"])
    if tipo == "entrada":
        writer.writerow(["E001", "Exemplo de entrada"])
        writer.writerow(["E002", "Venda de produto"])
    else:
        writer.writerow(["S001", "Exemplo de saída"])
        writer.writerow(["S002", "Pagamento de fornecedor"])
    output.seek(0)
    return output.getvalue().encode("utf-8-sig")

# --- Seção de período ---
st.markdown(
    """
    <h2 style="text-align: center;">Período dos registros</h2>
    """,
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)
with col1:
    data_inicio_str = st.text_input("Data inicial (dd/mm/aaaa)", value="01/01/2025")
    try:
        data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y")
    except:
        st.error("Formato de data inicial inválido! Use dd/mm/aaaa")
        st.stop()

with col2:
    data_fim_str = st.text_input("Data final (dd/mm/aaaa)", value="31/12/2025")
    try:
        data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y")
    except:
        st.error("Formato de data final inválido! Use dd/mm/aaaa")
        st.stop()

### Importação de parâmetros para geração do arquivo ###

# --- Unidades ---
st.markdown(
    """
    <h2 style="text-align: center;">Identificação de Unidades</h2>
    """,
    unsafe_allow_html=True
)
unidades_input = st.text_area(
    "Lista de unidades (separadas por vírgula)",
    value="01,02,03"
)
lista_unidades = [u.strip() for u in unidades_input.split(",") if u.strip()]

# --- Upload das classificações ---
st.markdown(
    """
    <h2 style="text-align: center;">Identificação de Classificações</h2>
    """,
    unsafe_allow_html=True
)

# três colunas: esquerda (Entrada), coluna estreita (linha), direita (Saída)
col_esq, col_vline, col_dir = st.columns([48, 1, 48])

# coluna esquerda: Entradas
with col_esq:
    st.markdown("**Entradas**")
    st.download_button(
        label="Clique para **Baixar modelo** (CSV)",
        data=gerar_template_csv("entrada"),
        file_name="classificacoes_de_entrada.csv",
        mime="text/csv"
    )
    arquivo_entradas = st.file_uploader("Importar lista de classificações de Entrada", type=["csv"])

# coluna central: linha vertical
# ajuste a altura (px) conforme necessário para cobrir a altura do conteúdo
vline_html = """
<div style="
    border-left: 2px solid #CCCCCC;
    height: 240px;
    margin-left: 50%;
">
</div>
"""
# Exibe a linha (vazia na coluna central)
col_vline.markdown(vline_html, unsafe_allow_html=True)

# coluna direita: Saídas
with col_dir:
    st.markdown("**Saídas**")
    st.download_button(
        label="Clique para **Baixar modelo** (CSV)",
        data=gerar_template_csv("saida"),
        file_name="classificacoes_de_saida.csv",
        mime="text/csv"
    )
    arquivo_saidas = st.file_uploader("Importar lista de classificações de Saída", type=["csv"])

# --- Ler arquivos importados, se existirem ---
entradas_codigos, saidas_codigos = [], []
entradas_nomes, saidas_nomes = [], []

if arquivo_entradas is not None:
    try:
        df_entradas = pd.read_csv(arquivo_entradas)
        if "codigo" in df_entradas.columns and "nome" in df_entradas.columns:
            entradas_codigos = df_entradas["codigo"].dropna().astype(str).tolist()
            entradas_nomes = df_entradas["nome"].dropna().astype(str).tolist()
            st.success(f"{len(entradas_codigos)} classificações de Entrada importadas com sucesso!")
            st.dataframe(df_entradas, use_container_width=True)
        else:
            st.error("Arquivo de entradas deve conter as colunas 'codigo' e 'nome'.")
    except Exception as e:
        st.error(f"Erro ao ler arquivo de entradas: {e}")

if arquivo_saidas is not None:
    try:
        df_saidas = pd.read_csv(arquivo_saidas)
        if "codigo" in df_saidas.columns and "nome" in df_saidas.columns:
            saidas_codigos = df_saidas["codigo"].dropna().astype(str).tolist()
            saidas_nomes = df_saidas["nome"].dropna().astype(str).tolist()
            st.success(f"{len(saidas_codigos)} classificações de Saída importadas com sucesso!")
            st.dataframe(df_saidas, use_container_width=True)
        else:
            st.error("Arquivo de saídas deve conter as colunas 'codigo' e 'nome'.")
    except Exception as e:
        st.error(f"Erro ao ler arquivo de saídas: {e}")

# --- Caso não tenha upload, permitir digitação manual ---
if not entradas_codigos:
    entradas_input = st.text_area(
        "Lista de classificações de Entrada (separadas por vírgula)",
        value="E001,E002,E003"
    )
    entradas_codigos = [e.strip() for e in entradas_input.split(",") if e.strip()]

if not saidas_codigos:
    saidas_input = st.text_area(
        "Lista de classificações de Saída (separadas por vírgula)",
        value="S001,S002,S003"
    )
    saidas_codigos = [s.strip() for s in saidas_input.split(",") if s.strip()]

num_registros = st.number_input("Número de registros", min_value=10, max_value=1000, value=100)

# --- Funções auxiliares ---
def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

def random_payment_date(due_date):
    if random.random() < 0.5:
        shift = random.randint(-5, 5)
        return due_date + timedelta(days=shift)
    else:
        return ""

def random_valor():
    return round(random.uniform(1, 101000), 2)

def random_cod_unidade():
    return random.choice(lista_unidades)

# --- Gerar registros ---
registros = []
id_counter = 1

if st.button("Gerar CSV"):
    while len(registros) < num_registros:
        tipo = random.choice(["E", "S"])
        descricao = random.choice(entradas_codigos) if tipo == "E" else random.choice(saidas_codigos)
        valor = random_valor()
        vencimento = random_date(data_inicio, data_fim)
        pagamento = random_payment_date(vencimento)

        venc_str = vencimento.strftime("%d/%m/%Y")
        pagamento_str = pagamento.strftime("%d/%m/%Y") if pagamento != "" else ""

        cliente_fornecedor = f"C{random.randint(1,50)}" if tipo == "E" else f"F{random.randint(1,50)}"
        cod_unidade = random.choice(lista_unidades)
        prev_s_doc = susp = pend_aprov = doc_edit = "N"
        cc = ""
        conta_bancaria = "12345-6"
        tipo_documento = ""
        projeto = ""
        dt_inc = (vencimento - timedelta(days=30)).strftime("%d/%m/%Y")
        dt_ems = (vencimento - timedelta(days=35)).strftime("%d/%m/%Y")
        erp_origem = ""
        erp_uuid = ""
        historico = f"Lançamento {id_counter} ({descricao})"

        registros.append([
            id_counter, tipo, valor, cod_unidade, cc, conta_bancaria, tipo_documento,
            descricao, projeto, prev_s_doc, susp, venc_str, pagamento_str,
            dt_inc, pend_aprov, erp_origem, erp_uuid, dt_ems, historico,
            cliente_fornecedor, doc_edit
        ])
        id_counter += 1

    # --- Criar CSV final ---
    csv_file = "documentos.csv"
    with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([
            "documento","natureza","valor","cod_unidade","centro_custo","conta_tesouraria",
            "tipo_doc","classif_fin","projeto","prev_s_doc","suspenso","data_venc","data_liq",
            "data_inc","pend_aprov","erp_origem","erp_uuid","data_emis","historico","cod_cli_for",
            "doc_edit"
        ])
        writer.writerows(registros)

    st.success(f"CSV gerado com {len(registros)} registros!")
    st.download_button("💾 Download do arquivo gerado", open(csv_file, "rb"), file_name="documentos.csv")