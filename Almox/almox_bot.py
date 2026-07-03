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
    """Clica na grade, seleciona tudo, copia e retorna texto do clipboard."""
    mouse.click(button="left", coords=GRID_POS)
    time.sleep(0.3)
    send_keys("^a")
    time.sleep(0.2)
    send_keys("^c")
    time.sleep(0.3)
    try:
        root = tk.Tk()
        root.withdraw()
        texto = root.clipboard_get()
        root.destroy()
        return texto
    except:
        return ""

def extrair_saida_e_preco(texto_grid):
    """Procura por 'saida' e o preco na mesma linha do texto copiado."""
    if not texto_grid:
        return "#N/D", "#N/D"
    
    linhas = texto_grid.split("\n")
    for linha in linhas:
        if "saida" in linha.lower():
            # Extrai o ultimo numero (preco) da linha
            # O formato esperado: ... saida ... 1,23  ou  #N/D
            partes = linha.split()
            preco = "#N/D"
            for p in reversed(partes):
                p = p.replace(",", ".").replace(".", "", 1) if "," in p else p
                try:
                    float(p.replace(",", "."))
                    preco = p
                    break
                except:
                    if p == "#N/D":
                        preco = p
                        break
            return "saida", preco
    
    return "#N/D", "#N/D"

# ============================================================
# GERAR EXCEL
# ============================================================
def gerar_excel(linhas, precos_map, caminho):
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
        cod = item["codigo"]
        val_unit = precos_map.get(cod, item["val_unit"])
        ws.append([
            cod, item["descricao"], item["dept_codigo"],
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

precos = {}
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

    # 3. Captura via clipboard
    texto_grid = capturar_grid_pela_tela()
    tipo, preco = extrair_saida_e_preco(texto_grid)

    print(f"    -> Tipo: {tipo} | Preco: {preco}")

    if preco == "#N/D" and texto_grid:
        print(f"    -> Texto copiado da grid (primeiras 200 chars):")
        print(f"       {texto_grid[:200]}")

    precos[codigo] = preco

print()
print("Gerando planilha final...")
gerar_excel(linhas, precos, EXCEL_PATH)

print()
print("=" * 55)
print("  FINALIZADO!")
print(f"  Codigos processados: {len(codigos)}")
print(f"  Planilha: {EXCEL_PATH}")
print("=" * 55)
print()
input("Pressione ENTER para fechar...")
