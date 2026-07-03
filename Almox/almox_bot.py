import time
import os
import sys
import re
import ctypes
import tkinter as tk
from tkinter import filedialog
from pywinauto import Desktop, mouse
from pywinauto.keyboard import send_keys
import openpyxl
import PyPDF2

# ============================================================
# CONFIGURACOES
# ============================================================
EDIT_COORDS    = (328, 280)
FILTRAR_COORDS = (416, 678)
GRID_POS       = (639, 282)  # Ponto qualquer dentro da grade para clicar

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
# LER TEXTO DA GRADE via CLIPBOARD (Ctrl+A + Ctrl+C)
# ============================================================
import tkinter as tk

def capturar_grid_pela_tela():
    """Clica na grade (um clique no alto da tabela) e copia tudo."""
    mouse.click(button="left", coords=GRID_POS)
    time.sleep(0.3)
    send_keys("^{HOME}")  # Vai para primeira celula
    time.sleep(0.2)
    send_keys("^a")       # Seleciona tudo
    time.sleep(0.3)
    send_keys("^c")       # Copia
    time.sleep(0.5)
    try:
        root = tk.Tk()
        root.withdraw()
        texto = root.clipboard_get()
        root.destroy()
        return texto
    except:
        return ""

def extrair_saida_por_data(texto_grid, data_pdf):
    """Procura 'Saida' na grade que tenha a data igual a data_pdf. Ignora 'Final'."""
    if not texto_grid:
        return "#N/D", "grid_vazia"
    
    linhas = texto_grid.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    linhas = [l for l in linhas if l.strip()]
    
    if len(linhas) < 2:
        return "#N/D", "poucas_linhas"
    
    cabecalho = linhas[0].split("\t")
    col_mov = col_data = col_vl = -1
    for idx, col in enumerate(cabecalho):
        c = col.strip().lower()
        if "movimenta" in c:
            col_mov = idx
        if "data do movimento" in c or "data movimento" in c:
            col_data = idx
        if "vl.sa" in c or "vl_sa" in c or "vl. sa" in c:
            col_vl = idx
    
    if -1 in (col_mov, col_data, col_vl):
        return "#N/D", f"colunas_mov={col_mov}_data={col_data}_vl={col_vl}"
    
    data_pdf = data_pdf.strip()
    
    for linha in linhas[1:]:
        cols = linha.split("\t")
        if col_mov >= len(cols) or col_data >= len(cols) or col_vl >= len(cols):
            continue
        
        tipo_mov = cols[col_mov].strip().lower()
        data_grid = cols[col_data].strip()
        
        if "final" in tipo_mov or tipo_mov == "":
            continue
        if "saida" not in tipo_mov:
            continue
        if data_grid != data_pdf:
            continue
        
        valor = cols[col_vl].strip()
        return "Saida", valor if valor else "#N/D"
    
    return "#N/D", f"sem_match_data_{data_pdf}"

def listar_saidas_grid(texto_grid):
    """Retorna lista de (data, valor) de todas linhas 'Saida' na grid (ignora Final)."""
    saidas = []
    if not texto_grid:
        return saidas
    linhas = texto_grid.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    linhas = [l for l in linhas if l.strip()]
    if len(linhas) < 2:
        return saidas
    cabecalho = linhas[0].split("\t")
    col_mov = col_data = col_vl = -1
    for idx, col in enumerate(cabecalho):
        c = col.strip().lower()
        if "movimenta" in c: col_mov = idx
        if "data do movimento" in c: col_data = idx
        if "vl.sa" in c or "vl_sa" in c: col_vl = idx
    if -1 in (col_mov, col_data, col_vl):
        return saidas
    for linha in linhas[1:]:
        cols = linha.split("\t")
        if len(cols) <= max(col_mov, col_data, col_vl):
            continue
        tipo = cols[col_mov].strip().lower()
        if "final" in tipo: continue
        if "saida" not in tipo: continue
        data = cols[col_data].strip()
        valor = cols[col_vl].strip()
        saidas.append((data, valor))
    return saidas

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

print("[3/5] Conectando ao desktop...")
desktop = Desktop(backend="uia")
print("  Pronto!")
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

    # 3. Captura via clipboard (uma vez por codigo)
    texto_grid = capturar_grid_pela_tela()

    # Mostra todas as saidas disponiveis na grid
    saidas_grid = listar_saidas_grid(texto_grid)
    if saidas_grid:
        print(f"    -> Saidas encontradas na grid: {len(saidas_grid)}")
        for d, v in saidas_grid:
            print(f"       Data: {d} | Vl.Saida: {v}")
    else:
        print(f"    -> Nenhuma linha 'Saida' encontrada na grid")

    # 4. Para cada linha do PDF com este codigo, tenta match pela data
    for item in linhas_por_codigo.get(codigo, []):
        data_pdf = item["data"]
        tipo, preco = extrair_saida_por_data(texto_grid, data_pdf)
        chave = (codigo, data_pdf)
        resultados[chave] = preco

        print(f"    -> Data PDF: {data_pdf} | Tipo: {tipo} | Preco: {preco}")

    # Salva log completo + saidas disponiveis
    with open(LOG_PATH, "a", encoding="utf-8") as log:
        log.write(f"=== Codigo: {codigo} ===\n")
        log.write(f"Saidas na grid: {len(saidas_grid)}\n")
        for d, v in saidas_grid:
            log.write(f"  Saida: data={d} valor={v}\n")
        log.write(f"Tamanho clipboard: {len(texto_grid)} chars\n")
        log.write(texto_grid + "\n")
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
