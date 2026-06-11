import time
import ctypes
import sys
import os
import traceback
import threading
import win32api
import win32con
import pyautogui
from pywinauto import Desktop, mouse

# ============================================================
#  CONFIGURAÇÕES GLOBAIS
# ============================================================
IMAGEM_PARADA = None   # Caminho para a imagem de parada
BOT_RODANDO   = False  # Flag para parar o loop

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
#  SLEEP COM SUPORTE A PAUSA (F8) E PARADA POR IMAGEM
# ============================================================
def sleep_inteligente(segundos):
    global BOT_RODANDO, IMAGEM_PARADA
    pausado = False
    inicio  = time.time()

    while time.time() - inicio < segundos:
        # Verifica parada por imagem
        if IMAGEM_PARADA and os.path.exists(IMAGEM_PARADA):
            try:
                encontrou = pyautogui.locateOnScreen(IMAGEM_PARADA, confidence=0.85)
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
    print("  INICIANDO AUTOMAÇÃO - Mega ERP")
    linha()
    print("  [ F8 ]   = Pausar / Retomar")
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
        print(f"=== APAGANDO REGISTRO {contador} ===")
        try:
            # 1. Procurar
            print("1. Clicando em Procurar...")
            mouse.click(button='left', coords=(414, 149))
            sleep_inteligente(2)
            if not BOT_RODANDO:
                break

            # 2. Aplicar
            print("2. Clicando em Aplicar...")
            mouse.click(button='left', coords=(815, 644))
            time.sleep(0.8)  # fixo, mais rápido

            # --- Verificação de fim por imagem (logo após Aplicar) ---
            if IMAGEM_PARADA and os.path.exists(IMAGEM_PARADA):
                try:
                    if pyautogui.locateOnScreen(IMAGEM_PARADA, confidence=0.85):
                        print("\n[IMAGEM DE PARADA DETECTADA] Todos os registros foram excluídos!")
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

            # 3. Clica na Tabela
            print("3. Clicando no 1º item da Tabela...")
            mouse.click(button='left', coords=(367, 244))
            sleep_inteligente(0.5)
            if not BOT_RODANDO:
                break

            # 4. Selecionar
            print("4. Clicando em Selecionar...")
            mouse.click(button='left', coords=(1021, 582))
            sleep_inteligente(1.5)
            if not BOT_RODANDO:
                break

            # 5. Excluir
            print("5. Clicando em Excluir...")
            mouse.click(button='left', coords=(1252, 144))
            sleep_inteligente(1)
            if not BOT_RODANDO:
                break

            # 6. Sim
            print("6. Clicando em Sim...")
            mouse.click(button='left', coords=(684, 423))
            sleep_inteligente(2)

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
    print("  Cole o caminho completo da imagem abaixo.")
    print("  Dica: clique com botão direito na imagem -> 'Copiar como caminho'")
    print()

    caminho = input("  Caminho da imagem: ").strip().strip('"')

    if os.path.exists(caminho):
        IMAGEM_PARADA = caminho
        print()
        print(f"  [OK] Imagem configurada: {os.path.basename(caminho)}")
    else:
        print()
        print("  [ERRO] Arquivo não encontrado. Verifique o caminho.")

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
