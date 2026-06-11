import time
import ctypes
import sys
import traceback
from pywinauto import Desktop, findwindows

def is_admin():
    """Verifica se o script está rodando como Administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    print("Iniciando o bot de automação do MEGA ERP...")
    print()

    # -------------------------------------------------------
    # VERIFICAÇÃO DE PRIVILÉGIOS
    # O MEGA ERP roda como Administrador. Para o pywinauto
    # conseguir interagir com ele, o bot também precisa rodar
    # como Administrador (restrição de segurança do Windows).
    # -------------------------------------------------------
    if not is_admin():
        print("=" * 55)
        print("  ERRO: Execute este script como ADMINISTRADOR!")
        print("  Clique com botão direito no arquivo .bat ou")
        print("  no Python e escolha 'Executar como administrador'")
        print("=" * 55)
        input("Pressione ENTER para sair...")
        sys.exit(1)

    print("[OK] Rodando como Administrador.")
    print()

    # Usando backend 'uia' (UIAutomation)
    desktop = Desktop(backend="uia")

    # Tenta encontrar a janela principal do Mega ERP
    # Título: "Mega Empresarial - Sistemas de Gestão Empresarial Mega ERP - [...]"
    print("Aguardando a janela principal do Mega ERP...")
    janela_principal = None

    # Padrões de título para tentar (do mais específico ao mais genérico)
    padroes = [
        ".*Mega Empresarial.*",
        ".*Mega ERP.*",
        ".*Movimento Financeiro.*",
    ]

    for padrao in padroes:
        try:
            janela_principal = desktop.window(title_re=padrao)
            janela_principal.wait('visible', timeout=5)
            print(f"  Janela encontrada com padrao: {padrao}")
            break
        except:
            janela_principal = None
            continue

    if janela_principal is None:
        print()
        print("  ERRO: Janela do MEGA ERP nao encontrada!")
        print("  Janelas abertas no momento:")
        try:
            todas = findwindows.find_elements(backend='uia')
            for j in todas:
                if j.name and j.name.strip():
                    print(f"    - '{j.name}'")
        except:
            print("    (nao foi possivel listar janelas)")
        input("\nPressione ENTER para sair...")
        return

    # =====================================================================
    # ABORDAGEM POR COORDENADAS (FALLBACK) SOLICITADA PELO USUÁRIO
    # =====================================================================
    from pywinauto import mouse
    import win32api
    import win32con
    
    pausado = False

    def sleep_com_pausa(segundos):
        nonlocal pausado
        inicio = time.time()
        while time.time() - inicio < segundos:
            # Verifica se F8 foi pressionado para pausar
            if win32api.GetAsyncKeyState(win32con.VK_F8) & 0x8000:
                pausado = not pausado
                if pausado:
                    print("\n[PAUSADO] Automação pausada! Pressione F8 novamente para continuar...")
                else:
                    print("\n[RETOMADO] Continuando automação...")
                time.sleep(0.5) # Evita múltiplos registros da mesma tecla (debounce)
            
            # Fica preso aqui dentro enquanto estiver pausado
            while pausado:
                if win32api.GetAsyncKeyState(win32con.VK_F8) & 0x8000:
                    pausado = False
                    print("\n[RETOMADO] Continuando automação...")
                    time.sleep(0.5)
                    break
                time.sleep(0.1)
                
            time.sleep(0.1)
    
    contador = 1
    print("\nIniciando o ciclo de exclusão por coordenadas (X, Y)...")
    print("IMPORTANTE: Não mova a janela do MEGA ERP e não use o mouse durante o processo!")
    print("-> Pressione [ F8 ] para PAUSAR ou RETOMAR o bot a qualquer momento.")
    print("-> Pressione [ CTRL+C ] no terminal para parar o bot de vez.")
    
    print("\nO bot vai começar em 5 segundos. Prepare a tela do MEGA ERP...")
    time.sleep(5)

    while True:
        # Checa se o usuário quis pausar antes de começar o próximo registro
        sleep_com_pausa(0.1) 
        
        print(f"=== APAGANDO REGISTRO {contador} ===")
        
        try:
            # 1. Procurar (X:414 Y:149)
            print("1. Clicando em Procurar...")
            mouse.click(button='left', coords=(414, 149))
            sleep_com_pausa(2)  # Aguarda a janela de busca abrir

            # 2. Aplicar (X:815 Y:644)
            print("2. Clicando em Aplicar...")
            mouse.click(button='left', coords=(815, 644))
            sleep_com_pausa(3)  # Aguarda a tabela de resultados carregar

            # ==========================================================
            # VERIFICAÇÃO DE FIM DOS REGISTROS (Lançamento não encontrado)
            # ==========================================================
            # Depois de Aplicar, se não houver mais registros, o MEGA mostra a mensagem
            try:
                msg_fim = desktop.child_window(title="Lançamento não encontrado.", control_type="Pane")
                if msg_fim.exists(timeout=1):
                    print("\n-> Mensagem 'Lançamento não encontrado.' detectada!")
                    print("-> Todos os itens da tabela foram excluídos com sucesso.")
                    print("\n=== FIM DA AUTOMAÇÃO! ===")
                    
                    # Clica no botão OK ou fechar da mensagem (tentativa de clicar no centro dela)
                    try:
                        msg_fim.click_input()
                    except:
                        pass
                    break
            except:
                pass # Segue o jogo, significa que tem registros para apagar

            # 3. Tabela (X:443 Y:242)
            print("3. Clicando no 1º item da Tabela...")
            mouse.click(button='left', coords=(443, 242))
            sleep_com_pausa(1)

            # 4. Selecionar (X:1021 Y:582)
            print("4. Clicando em Selecionar...")
            mouse.click(button='left', coords=(1021, 582))
            sleep_com_pausa(2)  # Aguarda fechar a busca e carregar o registro no painel
            
            # ==========================================================
            # VERIFICAÇÃO PARA NÃO FICAR EM LOOP INFINITO
            # ==========================================================
            print("Verificando se o registro foi carregado...")
            elem_excluir = desktop.from_point(1252, 144)
            
            if elem_excluir.window_text() != "Excluir":
                print("-> O botão Excluir não foi encontrado na posição esperada.")
                print("-> Isso significa que a tabela acabou ou a janela mudou.")
                print("\nFIM DOS REGISTROS! Loop finalizado.")
                break
                
            if not elem_excluir.is_enabled():
                print("-> O botão Excluir está desabilitado na tela.")
                print("-> Nenhum registro foi selecionado da tabela (ela deve estar vazia).")
                print("\nFIM DOS REGISTROS! Loop finalizado.")
                break

            # 5. Excluir (X:1252 Y:144)
            print("5. Clicando em Excluir...")
            mouse.click(button='left', coords=(1252, 144))
            sleep_com_pausa(1)  # Aguarda o popup de Sim/Não

            # Opcional: Verificando se o "Sim" abriu mesmo
            elem_sim = desktop.from_point(684, 423)
            if elem_sim.window_text() == "Sim":
                print("6. Clicando em Sim...")
                mouse.click(button='left', coords=(684, 423))
            else:
                print("Aviso: O botão Sim não estava na coordenada (684, 423). Tentando clicar mesmo assim...")
                mouse.click(button='left', coords=(684, 423))
                
            sleep_com_pausa(2)  # Aguarda a exclusão concluir e a tela resetar

            print(f"Registro {contador} excluído com sucesso!\n")
            contador += 1

        except KeyboardInterrupt:
            print("\nBot interrompido pelo usuário!")
            break
        except Exception as e:
            print(f"Erro durante o ciclo {contador}: {e}")
            print("Tentando novamente em 3 segundos...")
            time.sleep(3)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print()
        print("=" * 55)
        print("  ERRO INESPERADO:")
        print("=" * 55)
        traceback.print_exc()
        print("=" * 55)
    finally:
        print()
        input("Pressione ENTER para fechar...")
