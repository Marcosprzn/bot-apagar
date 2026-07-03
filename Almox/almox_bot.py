import time
import os
import sys
import re
import ctypes
import tkinter as tk
from tkinter import filedialog
from pywinauto import mouse
from pywinauto.keyboard import send_keys
import openpyxl
import PyPDF2

# ============================================================
# CONFIGURACOES
# ============================================================
EDIT_COORDS       = (328, 280)
FILTRAR_COORDS    = (416, 678)
PRIMEIRA_LINHA    = (649, 262)  # Primeiro item da tabela

PASTA_ATUAL = os.path.dirname(__file__)
EXCEL_PATH  = os.path.join(PASTA_ATUAL, "resultados_almox.xlsx")

BOT_RODANDO = True
PAUSADO = False

# ============================================================
# PAUSA F8
# ============================================================
def verificar_pausa():
    global PAUSADO
    if ctypes.windll.user32.GetAsyncKeyState(0x77) & 0x8000:
        PAUSADO = not PAUSADO
        if PAUSADO:
            print("\n  [F8] PAUSADO. Pressione F8 para retomar...")
        else:
            print("\n  [F8] Retomando...")
        time.sleep(0.5)
    while PAUSADO:
        if ctypes.windll.user32.GetAsyncKeyState(0x77) & 0x8000:
            PAUSADO = False
            print("\n  [F8] Retomando...")
            time.sleep(0.5)
        time.sleep(0.1)

# ============================================================
# SELECIONAR PDF
# ============================================================
def selecionar_pdf():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    caminho = filedialog.askopenfilename(
        title="Selecione o PDF com os codigos",
        filetypes=[("Arquivos PDF", "*.pdf"), ("Todos", "*.*")]
    )
    root.destroy()
    return caminho

# ============================================================
# LER PDF
# ============================================================
def ler_pdf(caminho):
    linhas = []
    with open(caminho, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for pagina in reader.pages:
            texto = pagina.extract_text()
            for linha in texto.split("\n"):
                linha = linha.strip()
                if not linha:
                    continue
                dados = parse_linha(linha)
                if dados:
                    linhas.append(dados)
    return linhas

def parse_linha(linha):
    partes = re.split(r"(\d{2}/\d{2}/\d{4})", linha)
    if len(partes) < 3:
        return None
    antes_data = partes[0].strip()
    data = partes[1].strip()
    depois_data = partes[2].strip()
    m = re.match(r"^(\d{2}\.\d{3})", antes_data)
    if not m:
        return None
    codigo = m.group(1)
    resto = antes_data[m.end():].strip()
    dept_codigo = ""
    dept_nome = ""
    descricao = resto
    m_dept = re.search(r"(\d{3})([A-Za-z\u00C0-\u00FF].*)$", resto)
    if m_dept:
        descricao = resto[:m_dept.start()].strip()
        dept_codigo = m_dept.group(1)
        dept_nome = m_dept.group(2).strip()
    campos = depois_data.split()
    req = campos[0] if len(campos) > 0 else ""
    qtd = ""
    unidade = ""
    val_unit = ""
    val_total = ""
    if len(campos) > 1:
        m_qtd = re.match(r"([\d.,]+)([A-Za-z].*)$", campos[1])
        if m_qtd:
            qtd = m_qtd.group(1)
            unidade = m_qtd.group(2).strip()
        else:
            qtd = campos[1]
    if len(campos) > 2:
        val_unit = campos[2]
    if len(campos) > 3:
        val_total = campos[3]
    return {
        "codigo": codigo, "descricao": descricao,
        "dept_codigo": dept_codigo, "dept_nome": dept_nome,
        "data": data, "req": req, "qtd": qtd,
        "unidade": unidade, "val_unit": val_unit, "val_total": val_total,
    }

def codigos_unicos(linhas):
    vistos = set()
    unicos = []
    for item in linhas:
        c = item["codigo"]
        if c not in vistos:
            vistos.add(c)
            unicos.append(c)
    return unicos

# ============================================================
# LER CADA LINHA DA GRADE navegando com seta para baixo
# ============================================================
def ler_clipboard():
    try:
        root = tk.Tk()
        root.withdraw()
        texto = root.clipboard_get()
        root.destroy()
        return texto
    except:
        return ""

def parse_linha_grid(texto):
    """Converte linha tabulada do clipboard em dict."""
    if not texto:
        return None
    cols = texto.split("\t")
    return {
        "tipo": cols[0].strip() if len(cols) > 0 else "",
        "data": cols[2].strip() if len(cols) > 2 else "",
        "vl_saida": cols[9].strip() if len(cols) > 9 else "",
    }

def navegar_grade():
    """Clica na primeira linha, navega pra baixo ate 'Final', retorna precos."""
    time.sleep(0.5)
    mouse.click(button="left", coords=PRIMEIRA_LINHA)
    time.sleep(0.3)

    linhas_lidas = []
    max_linhas = 200  # segurança pra loop infinito

    for _ in range(max_linhas):
        send_keys("^c")
        time.sleep(0.3)
        texto = ler_clipboard()
        if not texto:
            print(f"       [DEBUG] Clipboard vazio")
            break

        dados = parse_linha_grid(texto)
        if not dados:
            print(f"       [DEBUG] Clipboard sem formato de linha: '{texto[:100]}'")
            break

        tipo = dados["tipo"].lower()
        if "final" in tipo:
            break
        if tipo == "":
            break

        linhas_lidas.append(dados)
        send_keys("{DOWN}")
        time.sleep(0.2)

    return linhas_lidas

# ============================================================
# GERAR EXCEL
# ============================================================
def gerar_excel(linhas, resultados, caminho):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Almox"
    cabecalhos = [
        "Codigo", "Descricao", "Dept Cod", "Dept Nome",
        "Data", "Requisicao", "Quantidade", "Unidade",
        "Valor Unitario", "Valor Total"
    ]
    ws.append(cabecalhos)
    for item in linhas:
        chave = (item["codigo"], item["data"])
        val_unit = resultados.get(chave, item["val_unit"])
        ws.append([
            item["codigo"], item["descricao"], item["dept_codigo"],
            item["dept_nome"], item["data"], item["req"],
            item["qtd"], item["unidade"], val_unit, item["val_total"],
        ])
    wb.save(caminho)
    print(f"  Planilha salva: {caminho}")

# ============================================================
# INTERFACE
# ============================================================
def perguntar_quantidade(total):
    print(f"  Total de codigos unicos disponiveis: {total}")
    resp = input("  Quantos codigos processar? (Enter = todos): ").strip()
    if resp == "":
        return total
    try:
        n = int(resp)
        return min(n, total)
    except:
        return total

# ============================================================
# MAIN
# ============================================================
os.system("cls" if os.name == "nt" else "clear")
print("=" * 55)
print("  BOT ALMOX - Captura de Unitarios")
print("=" * 55)
print()

print("[1/5] Selecione o arquivo PDF...")
PDF_PATH = selecionar_pdf()
if not PDF_PATH:
    print("  Nenhum PDF selecionado. Encerrando.")
    input("Pressione ENTER para sair...")
    sys.exit(0)
print(f"  PDF: {os.path.basename(PDF_PATH)}")
print()

print("Lendo PDF...")
linhas = ler_pdf(PDF_PATH)
codigos = codigos_unicos(linhas)
print(f"  Linhas no PDF: {len(linhas)}")
print(f"  Codigos unicos: {len(codigos)}")
print()

print("[2/5] Quantos codigos processar?")
qtd = perguntar_quantidade(len(codigos))
codigos = codigos[:qtd]
print(f"  Processando: {len(codigos)} codigos")
print()

print("[3/5] Pronto!")
print()

print("[4/5] Iniciando automacao...")
print("  Deixe a janela de consulta do MEGA ERP aberta e visivel.")
print("  [F8] = Pausar / Retomar a qualquer momento")
print("  Iniciando em 5 segundos...")
time.sleep(5)
print()

print("[5/5] Executando...")
print()

LOG_PATH = os.path.join(PASTA_ATUAL, "log_captura_grid.txt")
with open(LOG_PATH, "w", encoding="utf-8") as log:
    log.write("LOG DE CAPTURA DA GRADE - ALMOX BOT\n")
    log.write("=" * 60 + "\n\n")

# Agrupa linhas do PDF por codigo: {codigo: [linha1, linha2, ...]}
linhas_por_codigo = {}
for item in linhas:
    c = item["codigo"]
    if c not in linhas_por_codigo:
        linhas_por_codigo[c] = []
    linhas_por_codigo[c].append(item)

# Mapeia (codigo, data) -> valor capturado
resultados = {}  # chave = (codigo, data)

for i, codigo in enumerate(codigos, 1):
    verificar_pausa()
    if not BOT_RODANDO:
        break

    codigo_limpo = codigo.replace(".", "")
    print(f"  [{i}/{len(codigos)}] Codigo: {codigo} -> digitando: {codigo_limpo}")

    # 1. Digita codigo
    mouse.click(button="left", coords=EDIT_COORDS)
    time.sleep(0.3)
    send_keys("^a")
    time.sleep(0.1)
    send_keys("{DELETE}")
    time.sleep(0.1)
    send_keys(codigo_limpo)
    time.sleep(0.3)

    # 2. Clica Filtrar
    mouse.click(button="left", coords=FILTRAR_COORDS)
    time.sleep(2)

    # 3. Navega pela grade linha a linha
    linhas_grid = navegar_grade()
    print(f"    -> Linhas lidas da grid: {len(linhas_grid)}")

    # Mostra o que foi lido
    for lg in linhas_grid:
        print(f"       Tipo: {lg['tipo']} | Data: {lg['data']} | Vl.Saida: {lg['vl_saida']}")

    # 4. Para cada linha do PDF com este codigo, tenta match pela data
    for item in linhas_por_codigo.get(codigo, []):
        data_pdf = item["data"]
        preco = "#N/D"
        for lg in linhas_grid:
            if lg["data"] == data_pdf and "saida" in lg["tipo"].lower():
                preco = lg["vl_saida"]
                break
        chave = (codigo, data_pdf)
        resultados[chave] = preco
        print(f"    -> Data PDF: {data_pdf} | Preco capturado: {preco}")

    # Salva log
    with open(LOG_PATH, "a", encoding="utf-8") as log:
        log.write(f"=== Codigo: {codigo} ===\n")
        for lg in linhas_grid:
            log.write(f"  tipo={lg['tipo']} data={lg['data']} vl={lg['vl_saida']}\n")
        log.write("=" * 40 + "\n\n")

print()
print("Gerando planilha final...")
gerar_excel(linhas, resultados, EXCEL_PATH)

print()
print("=" * 55)
print("  FINALIZADO!")
print(f"  Codigos processados: {len(codigos)}")
print(f"  Planilha: {EXCEL_PATH}")
print(f"  Log da grid: {LOG_PATH}")
print("=" * 55)
print()
input("Pressione ENTER para fechar...")
