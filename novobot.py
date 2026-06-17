import time
import ctypes
import sys
import os
import traceback
import win32api
import win32con
import pyautogui
from pywinauto import Desktop

# ============================================================
#  CONFIGURAÇÕES GLOBAIS (Caminhos das imagens)
# ============================================================
IMAGEM_PARADA        = None              # Caminho para a imagem de parada (definido via Menu)
IMAGEM_PROCURAR      = "Procurar.PNG"    # Imagem do botão Procurar
IMAGEM_APLICAR       = "Aplicar.PNG"     # Imagem do botão Aplicar
IMAGEM_SELECIONAR    = "selecionar.PNG"  # Imagem do botão Selecionar
IMAGEM_EXCLUIR       = "excluir.PNG"     # Imagem do botão Excluir
IMAGEM_SIM           = "Sim.PNG"         # Imagem do botão Sim

# Imagem para detecção do erro (ORA-00060 / erro do servidor)
IMAGEM_ERRO_SERVIDOR = "erro novo.jpeg"

# Imagem para detecção de fim de registros
IMAGEM_LANCAMENTO_NAO_ENCONTRADO = "lançamento não encontrado.PNG"

BOT_RODANDO   = False  # Flag para parar o loop

# Cache de coordenadas: depois de encontrar um botão, guarda a posição pra clicar mais rapido
CACHE_CLIQUE = {}

# ============================================================
#  UTILITÁRIOS
# ============================================================
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def limpar_tela():
    os.system('cls')

def linha(char='=', n=55):
    print(char * n)

def pausado_flag():
    """Flag de pausa controlada pelo F8."""
    return win32api.GetAsyncKeyState(win32con.VK_F8) & 0x8000

# ============================================================
#  FUNÇÃO AUXILIAR PARA CLIQUE POR IMAGEM (COM FALLBACK)
# ============================================================
def clicar_por_imagem(caminho_imagem, coords_fallback, descricao, confidence=0.75, grayscale=True):
    """
    Tenta localizar a imagem na tela e clicar no centro dela.
    Caso não encontre ou o arquivo não exista, realiza o clique nas coordenadas de fallback.
    Usa cache para evitar scan repetido.
    """
    global CACHE_CLIQUE
    # Verifica cache primeiro
    if caminho_imagem in CACHE_CLIQUE:
        x, y = CACHE_CLIQUE[caminho_imagem]
        pyautogui.click(x, y)
        print(f"  [Cache] Clicou em '{descricao}' via cache ({x}, {y}).")
        return True
    if os.path.exists(caminho_imagem):
        try:
            ponto = pyautogui.locateCenterOnScreen(caminho_imagem, confidence=confidence, grayscale=grayscale)
            if ponto:
                x, y = int(ponto[0]), int(ponto[1])
                CACHE_CLIQUE[caminho_imagem] = (x, y)
                pyautogui.click(x, y)
                print(f"  [OK] Clicou no botão '{descricao}' localizado via imagem ({x}, {y}).")
                return True
        except Exception as e:
            pass

    # Fallback se a imagem não for localizada ou se o arquivo não existir
    print(f"  [Aviso] Botão '{descricao}' não localizado por imagem. Usando coordenadas fixas: {coords_fallback}")
    pyautogui.click(coords_fallback[0], coords_fallback[1])
    return False

# ============================================================
#  FUNÇÃO PARA ESPERAR IMAGEM E CLICAR COM DESLOCAMENTO (OFFSET)
# ============================================================
def esperar_e_clicar_deslocado(caminho_imagem, offset_y, descricao, timeout=10, confidence=0.75, grayscale=True):
    """
    Aguarda a imagem aparecer na tela dentro do limite de tempo (timeout).
    Quando localizada, clica no centro X e no centro Y somando o offset_y (em pixels).
    Retorna True se clicou com sucesso, False se der timeout.
    """
    global BOT_RODANDO
    if not os.path.exists(caminho_imagem):
        print(f"  [Erro] Arquivo de imagem do campo '{descricao}' ({caminho_imagem}) não encontrado!")
        return False

    print(f"  [Aguardando] Esperando o campo '{descricao}' aparecer na tela...")
    inicio = time.time()
    while time.time() - inicio < timeout:
        if not BOT_RODANDO:
            return False
        try:
            ponto = pyautogui.locateCenterOnScreen(caminho_imagem, confidence=confidence, grayscale=grayscale)
            if ponto:
                alvo_x = int(ponto[0])
                alvo_y = int(ponto[1]) + offset_y
                pyautogui.click(alvo_x, alvo_y)
                print(f"  [OK] Campo '{descricao}' localizado! Clicado em ({alvo_x}, {alvo_y}) com deslocamento de +{offset_y}px.")
                return True
        except Exception as e:
            pass
        time.sleep(0.1)

    print(f"  [Tempo Esgotado] Não foi possível localizar o campo '{descricao}' em {timeout} segundos.")
    return False

def aguardar_janela_aparecer(desktop, title_re, timeout=5):
    """Espera janela com title_re aparecer. Rápido, sem scan de tela."""
    global BOT_RODANDO
    inicio = time.time()
    while time.time() - inicio < timeout:
        if not BOT_RODANDO:
            return False
        try:
            w = desktop.window(title_re=title_re)
            if w.exists(timeout=0.01):
                return True
        except:
            pass
        time.sleep(0.02)
    return False

def aguardar_janela_desaparecer(desktop, title_re, timeout=5):
    """Espera janela com title_re desaparecer. Rápido, sem scan de tela."""
    global BOT_RODANDO
    inicio = time.time()
    while time.time() - inicio < timeout:
        if not BOT_RODANDO:
            return False
        try:
            w = desktop.window(title_re=title_re)
            if not w.exists(timeout=0.01):
                return True
        except:
            return True
        time.sleep(0.02)
    return False

# ============================================================
#  DETECÇÃO E TRATAMENTO SEGURO DE ERRO DE SERVIDOR (ORA-00060)
# ============================================================
def verificar_e_tratar_erro_servidor():
    """
    Verificação robusta em duas camadas (Imagem + Estrutura de Janela) para detectar
    o erro 'ORA-00060' de conflito de recursos do servidor e clicar em 'Sim' para continuar.
    """
    global BOT_RODANDO
    if not BOT_RODANDO:
        return False

    # --- CAMADA 1: DETECÇÃO POR VISÃO COMPUTACIONAL (IMAGEM) ---
    if os.path.exists(IMAGEM_ERRO_SERVIDOR):
        try:
            # Varre a tela procurando o padrão do erro
            detectou = pyautogui.locateOnScreen(IMAGEM_ERRO_SERVIDOR, confidence=0.75, grayscale=True)
            if detectou:
                print("\n" + "!"*60)
                print("  [ALERTA] ERRO DE SERVIDOR DETECTADO VIA IMAGEM (ORA-00060)!")
                print("  Pausando fluxo temporariamente para recuperação segura...")
                print("!"*60)
                time.sleep(1.0) # Estabilização
                
                # Clica no botão Sim para retransmitir/gravar de novo
                if clicar_por_imagem(IMAGEM_SIM, (684, 423), "Sim (Recuperação de Erro)"):
                    print("  [Sucesso] Erro de rede/banco contornado! Retomando em 3 segundos...")
                    time.sleep(3.0)
                    return True
        except Exception as e:
            pass

    # --- CAMADA 2: DETECÇÃO DIRETA POR APIS DO WINDOWS (PYWINAUTO - FALLBACK SEGURO) ---
    try:
        desktop = Desktop(backend="uia")
        # Procura por uma janela ativa com título "Confirmar"
        janela_confirmar = desktop.window(title="Confirmar")
        if janela_confirmar.exists(timeout=0.05):
            # Valida se é o erro específico procurando as strings críticas do ORA-00060 na estrutura do texto
            texto_erro = janela_confirmar.child_window(title_re=".*ORA-00060.*|.*Servidor no momento.*", control_type="Text")
            if texto_erro.exists(timeout=0.05):
                print("\n" + "!"*60)
                print("  [ALERTA] ERRO DE SERVIDOR DETECTADO VIA ESTRUTURA (ORA-00060)!")
                print("  Recuperando sessão do banco de dados...")
                print("!"*60)
                time.sleep(1.0)
                
                # Localiza e clica no botão "Sim" físico do pop-up
                botao_sim = janela_confirmar.child_window(title="Sim", control_type="Button")
                if botao_sim.exists():
                    botao_sim.click_input()
                    print("  [Sucesso] Botão Sim clicado via Windows API! Retomando em 3 segundos...")
                    time.sleep(3.0)
                    return True
    except Exception as e:
        pass

    return False

# ============================================================
#  SLEEP COM SUPORTE A PAUSA (F8), PARADA E ERROS EM TEMPO REAL
# ============================================================
def sleep_inteligente(segundos):
    global BOT_RODANDO, IMAGEM_PARADA
    pausado = False
    inicio  = time.time()
    ultima_verificacao_erro = 0  # throttle: checa erro no max 1x por segundo

    while time.time() - inicio < segundos:
        if not BOT_RODANDO:
            return

        # Verifica erro de servidor com throttle (1x por segundo)
        agora = time.time()
        if agora - ultima_verificacao_erro > 1.0:
            verificar_e_tratar_erro_servidor()
            ultima_verificacao_erro = agora

        # Verifica parada por imagem
        if IMAGEM_PARADA and os.path.exists(IMAGEM_PARADA):
            try:
                encontrou = pyautogui.locateOnScreen(IMAGEM_PARADA, confidence=0.75, grayscale=True)
                if encontrou:
                    BOT_RODANDO = False
                    print("\n[IMAGEM DE PARADA DETECTADA] Encerrando o bot...")
                    return
            except:
                pass

        # Verifica F8 para pausar/retomar
        if pausado_flag():
            pausado = not pausado
            if pausado:
                print("\n[PAUSADO] Pressione F8 para retomar...")
            else:
                print("\n[RETOMADO] Continuando...")
            time.sleep(0.5)  # debounce

        while pausado:
            if pausado_flag():
                pausado = False
                print("\n[RETOMADO] Continuando...")
                time.sleep(0.5)
                break
            time.sleep(0.1)

        time.sleep(0.05)

# ============================================================
#  LOOP PRINCIPAL DE AUTOMAÇÃO
# ============================================================
def executar_automacao():
    global BOT_RODANDO

    desktop = Desktop(backend="uia")
    print()
    linha()
    print("  INICIANDO AUTOMAÇÃO - Mega ERP (Localização Inteligente)")
    linha()
    print("  [ F8 ]     = Pausar / Retomar")
    print("  [ CTRL+C ] = Parar imediatamente")
    if IMAGEM_PARADA:
        print(f"  Imagem de parada: {os.path.basename(IMAGEM_PARADA)}")
    else:
        print("  Sem imagem de parada configurada.")
    linha()
    print("\nIniciando em 5 segundos... Prepare a tela do MEGA ERP!\n")
    time.sleep(5)

    contador = 1
    while BOT_RODANDO:
        # Checagem extra de prevenção de erro no começo do loop
        verificar_e_tratar_erro_servidor()

        print(f"=== APAGANDO REGISTRO {contador} ===")
        try:
            # 1. Clica em Procurar (coordenada fixa)
            print("1. Clicando em 'Procurar'...")
            pyautogui.click(414, 149)
            # Espera a janela "Procurar Movimento Financeiro" aparecer
            if not aguardar_janela_aparecer(desktop, "Procurar Movimento.*", timeout=5):
                print("  [Aviso] Timeout esperando janela Procurar, continuando...")
            if not BOT_RODANDO:
                break

            # 2. Aplicar (coordenada fixa)
            print("2. Clicando em 'Aplicar'...")
            pyautogui.click(815, 644)
            time.sleep(0.5)

            # Aguarda a janela "Procurar Movimento" fechar (tabela carregada)
            print("  Aguardando tabela carregar (janela fechando)...")
            if not aguardar_janela_desaparecer(desktop, "Procurar Movimento.*", timeout=10):
                print("  [Aviso] Timeout esperando tabela, continuando...")
            if not BOT_RODANDO:
                break

            # --- Verificação de fim por imagem (logo após Aplicar e Seleção) ---
            if IMAGEM_PARADA and os.path.exists(IMAGEM_PARADA):
                try:
                    if pyautogui.locateOnScreen(IMAGEM_PARADA, confidence=0.75, grayscale=True):
                        print("\n[IMAGEM DE PARADA DETECTADA] Todos os registros foram excluídos!")
                        BOT_RODANDO = False
                        break
                except:
                    pass

            # --- Verificação de fim por imagem (Lançamento não encontrado) ---
            if os.path.exists(IMAGEM_LANCAMENTO_NAO_ENCONTRADO):
                try:
                    if pyautogui.locateOnScreen(IMAGEM_LANCAMENTO_NAO_ENCONTRADO, confidence=0.75, grayscale=True):
                        print("\n[IMAGEM] 'Lançamento não encontrado.' detectado! Fim dos registros.")
                        BOT_RODANDO = False
                        break
                except:
                    pass

            # --- Verificação pelo texto da janela (fallback) ---
            try:
                msg = desktop.child_window(title="Lançamento não encontrado.", control_type="Pane")
                if msg.exists(timeout=0.5):
                    print("\n-> 'Lançamento não encontrado.' detectado! Fim dos registros.")
                    BOT_RODANDO = False
                    break
            except:
                pass

            if not BOT_RODANDO:
                break

            # 3. Clica na Tabela (Mantido coordenadas fixas para selecionar a linha do grid)
            print("3. Clicando no 1º item da Tabela...")
            pyautogui.click(367, 244)
            sleep_inteligente(0.5)
            if not BOT_RODANDO:
                break

            # 4. Selecionar (coordenada fixa direta)
            print("4. Clicando em 'Selecionar'...")
            pyautogui.click(1021, 582)
            sleep_inteligente(0.5)
            if not BOT_RODANDO:
                break

            # 5. Excluir (Por imagem ou fallback de coordenadas antigas)
            print("5. Procurando e clicando em 'Excluir'...")
            clicar_por_imagem(IMAGEM_EXCLUIR, (1252, 144), "Excluir")
            sleep_inteligente(0.5)
            if not BOT_RODANDO:
                break

            # 6. Sim (Por imagem ou fallback de coordenadas antigas)
            print("6. Procurando e clicando em 'Sim'...")
            clicar_por_imagem(IMAGEM_SIM, (684, 423), "Sim")
            # Espera a janela de confirmacao desaparecer + folga minima
            aguardar_janela_desaparecer(desktop, "Confirmar", timeout=5)
            sleep_inteligente(0.5)

            print(f"Registro {contador} excluído!\n")
            contador += 1

        except KeyboardInterrupt:
            print("\n[CTRL+C] Bot interrompido pelo usuário!")
            BOT_RODANDO = False
            break
        except Exception as e:
            print(f"[ERRO] Ciclo {contador}: {e}")
            print("Tentando novamente em 3 segundos...")
            time.sleep(3)

    linha()
    print(f"  Bot finalizado. Total de registros excluídos: {contador - 1}")
    linha()

# ============================================================
#  SELECIONAR IMAGEM DE PARADA
# ============================================================
def selecionar_imagem():
    global IMAGEM_PARADA
    limpar_tela()
    linha()
    print("  SELECIONAR IMAGEM DE PARADA")
    linha()
    print()
    print("  Abrindo o explorador de arquivos... (pode aparecer atrás desta janela)")
    print()

    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()          
        root.attributes('-topmost', True)  

        caminho = filedialog.askopenfilename(
            title="Selecione a imagem de parada",
            filetypes=[
                ("Imagens", "*.png *.jpg *.jpeg *.bmp"),
                ("Todos os arquivos", "*.*")
            ]
        )
        root.destroy()

        if caminho:
            IMAGEM_PARADA = caminho
            print(f"  [OK] Imagem configurada: {os.path.basename(caminho)}")
        else:
            print("  [CANCELADO] Nenhuma imagem selecionada.")

    except Exception as e:
        print(f"  [ERRO] Não foi possível abrir o explorador: {e}")

    print()
    input("  Pressione ENTER para voltar ao menu...")

# ============================================================
#  DASHBOARD PRINCIPAL
# ============================================================
def dashboard():
    global BOT_RODANDO

    while True:
        limpar_tela()
        linha()
        print("       BOT MEGA ERP - DASHBOARD")
        linha()
        print()
        if IMAGEM_PARADA:
            print(f"  Imagem de parada : {os.path.basename(IMAGEM_PARADA)}")
        else:
            print("  Imagem de parada : Não configurada")
        print()
        linha('-')
        print("  [ 1 ] Iniciar automação")
        print("  [ 2 ] Selecionar imagem de parada")
        print("  [ 0 ] Sair")
        linha('-')
        print()

        opcao = input("  Escolha: ").strip()

        if opcao == '1':
            BOT_RODANDO = True
            executar_automacao()
            input("\n  Pressione ENTER para voltar ao menu...")

        elif opcao == '2':
            selecionar_imagem()

        elif opcao == '0':
            limpar_tela()
            print("  Encerrando. Até logo!")
            break
        else:
            print("  Opção inválida.")
            time.sleep(1)

# ============================================================
#  ENTRY POINT
# ============================================================
if __name__ == "__main__":
    if not is_admin():
        print("=" * 55)
        print("  ERRO: Execute como ADMINISTRADOR!")
        print("  Clique direito no .bat -> 'Executar como administrador'")
        print("=" * 55)
        input("Pressione ENTER para sair...")
        sys.exit(1)

    try:
        dashboard()
    except Exception as e:
        print()
        linha()
        print("  ERRO INESPERADO:")
        linha()
        traceback.print_exc()
        linha()
    finally:
        input("\nPressione ENTER para fechar...")
