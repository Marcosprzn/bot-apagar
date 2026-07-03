import time
import os
import re
import ctypes
from pywinauto import Desktop, mouse
from pywinauto.keyboard import send_keys
import openpyxl
import PyPDF2

# ============================================================
# CONFIGURACOES (coordenas capturadas)
# ============================================================
EDIT_COORDS  = (328, 280)
FILTRAR_COORDS = (416, 678)
SAIDA_COORDS = (639, 282)
PRECO_COORDS = (745, 286)

PASTA_ATUAL = os.path.dirname(__file__)
PDF_PATH    = os.path.join(PASTA_ATUAL, "SaidaFaltaValorUnitario.pdf")
EXCEL_PATH  = os.path.join(PASTA_ATUAL, "resultados_almox.xlsx")

# ============================================================
# EXTRAIR CODIGOS UNICOS DO PDF
# ============================================================
def extrair_codigos(pdf_path):
    codigos = []
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for pagina in reader.pages:
            texto = pagina.extract_text()
            for linha in texto.split("\n"):
                linha = linha.strip()
                match = re.match(r"^(\d{2}\.\d{3})", linha)
                if match:
                    codigos.append(match.group(1))
    # Remove duplicatas mantendo ordem
    vistos = set()
    unicos = []
    for c in codigos:
        if c not in vistos:
            vistos.add(c)
            unicos.append(c)
    return unicos

# ============================================================
# LER TEXTO DE UMA POSICAO NA TELA (UIA)
# ============================================================
def texto_na_posicao(x, y, desktop):
    try:
        elem = desktop.from_point(x, y)
        txt = elem.window_text()
        return txt.strip() if txt else None
    except:
        return None

# ============================================================
# SALVAR RESULTADOS EM EXCEL
# ============================================================
def salvar_excel(resultados, caminho):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Resultados"
    ws.append(["Codigo", "Preco Capturado"])
    for codigo, preco in resultados:
        ws.append([codigo, preco])
    wb.save(caminho)
    print(f"  Resultados salvos em: {caminho}")

# ============================================================
# MAIN
# ============================================================
print("=" * 55)
print("  BOT ALMOX - Captura de Prec os")
print("=" * 55)
print()

# --- Ler PDF ---
print("[1/4] Extraindo codigos do PDF...")
codigos = extrair_codigos(PDF_PATH)
print(f"  Total de codigos unicos: {len(codigos)}")
print()

# --- Conectar desktop ---
print("[2/4] Conectando ao desktop...")
desktop = Desktop(backend="uia")
print("  Pronto!")
print()

print("[3/4] Iniciando automacao...")
print("  Prepare a tela do MEGA ERP com a janela de consulta.")
print("  Iniciando em 5 segundos...")
time.sleep(5)
print()

print("[4/4] Executando...")
print()

resultados = []
for i, codigo in enumerate(codigos, 1):
    print(f"  [{i}/{len(codigos)}] Processando codigo: {codigo}")

    # 1. Clica no campo Edit e digita o codigo
    mouse.click(button="left", coords=EDIT_COORDS)
    time.sleep(0.3)
    send_keys("^a")   # Seleciona tudo
    time.sleep(0.1)
    send_keys("{DELETE}")  # Apaga
    time.sleep(0.1)
    send_keys(codigo)  # Digita o codigo
    time.sleep(0.3)

    # 2. Clica em Filtrar
    mouse.click(button="left", coords=FILTRAR_COORDS)
    time.sleep(2)  # Aguarda carregar

    # 3. Verifica se achou "saida" na posicao esperada
    texto_saida = texto_na_posicao(SAIDA_COORDS[0], SAIDA_COORDS[1], desktop)
    preco = "#N/D"

    if texto_saida and "saida" in texto_saida.lower():
        # Captura o preco na mesma linha
        texto_preco = texto_na_posicao(PRECO_COORDS[0], PRECO_COORDS[1], desktop)
        if texto_preco:
            preco = texto_preco
        print(f"    -> Saida encontrada! Preco: {preco}")
    else:
        print(f"    -> Saida nao encontrada ou posicao fora da tela")
        if texto_saida:
            print(f"    -> Texto encontrado: '{texto_saida}'")

    resultados.append((codigo, preco))

# --- Salvar Excel ---
print()
print("Salvando resultados...")
salvar_excel(resultados, EXCEL_PATH)

print()
print("=" * 55)
print("  AUTOMACAO FINALIZADA!")
print(f"  Processados: {len(codigos)} codigos")
print(f"  Resultados: {EXCEL_PATH}")
print("=" * 55)
print()
input("Pressione ENTER para fechar...")
