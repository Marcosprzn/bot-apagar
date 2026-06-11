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

    # Sistema de "Aprendizado" para deixar as próximas repetições muito mais rápidas!
    # O MEGA ERP muda o AutomationId toda vez que abre, MAS durante a mesma sessão eles são fixos.
    # Na 1ª vez ele busca devagar (por Título/Classe). Na 2ª vez ele lembra o ID e acha quase instantaneamente.
    CACHE = {}

    def get_elemento_rapido(nome_logico, parent, **kwargs):
        # 1. Tenta achar rápido pelo cache (ID aprendido)
        if nome_logico in CACHE:
            try:
                rapido = parent.child_window(auto_id=CACHE[nome_logico], control_type=kwargs.get("control_type", "Button"))
                if rapido.exists(timeout=1):
                    return rapido
            except:
                pass # Se falhar, cai na busca normal
        
        # 2. Busca normal, mais lenta (por title e class_name)
        lento = parent.child_window(**kwargs)
        lento.wait('exists', timeout=10) # Aguarda existir
        
        # 3. "Aprende" o AutomationId para a próxima repetição!
        try:
            CACHE[nome_logico] = lento.element_info.automation_id
        except:
            pass
            
        return lento

    contador = 1
    print("\nIniciando o ciclo de exclusão...")
    print("O bot vai APRENDER os botões na 1ª vez. Da 2ª em diante será super rápido!")
    print("Pressione CTRL+C no terminal para parar o bot a qualquer momento.\n")

    while True:
        print(f"=== APAGANDO REGISTRO {contador} ===")
        
        try:
            # 1. Clicar no botão "Procurar"
            botao_procurar = get_elemento_rapido("btn_procurar", janela_principal, title="Procurar", class_name="TMgBitBtn", control_type="Button")
            botao_procurar.wait('ready', timeout=10)
            botao_procurar.click_input()
            time.sleep(1) # Espera a janela abrir internamente

            # 2. Clicar no botão "Aplicar"
            botao_aplicar = get_elemento_rapido("btn_aplicar", janela_principal, title="Aplicar", class_name="TMgBitBtn", control_type="Button")
            botao_aplicar.wait('ready', timeout=10)
            botao_aplicar.click_input()
            time.sleep(1.5) # Espera a tabela atualizar

            # 3. Interagir com a Tabela (clicando na primeira linha)
            tabela = get_elemento_rapido("tabela_resultados", janela_principal, class_name="TcxGridSite", control_type="Pane")
            tabela.wait('visible', timeout=10)
            tabela.click_input(coords=(50, 30))
            time.sleep(0.5)

            # 4. Clicar no botão "Selecionar"
            botao_selecionar = get_elemento_rapido("btn_selecionar", janela_principal, title="Selecionar", class_name="TMgSpeedButton", control_type="Button")
            botao_selecionar.wait('ready', timeout=5)
            botao_selecionar.click_input()
            time.sleep(1.5) # Espera voltar para o dashboard do Mega ERP

            # 5. Clicar no botão "Excluir"
            botao_excluir = get_elemento_rapido("btn_excluir", janela_principal, title="Excluir", class_name="TMgSpeedButton", control_type="Button")
            botao_excluir.wait('ready', timeout=10) # Garante que o botão está habilitado e visível
            botao_excluir.click_input()
            time.sleep(1) # Aguarda o popup de confirmação

            # 6. Clicar no botão "Sim" (Confirmação)
            # Pode estar na janela_principal ou ser um popup top-level. Vamos tentar primeiro na janela_principal.
            try:
                botao_sim = get_elemento_rapido("btn_sim", janela_principal, title="Sim", class_name="TcxButton", control_type="Button")
                botao_sim.wait('ready', timeout=5)
                botao_sim.click_input()
            except:
                # Fallback: Se for uma janela popup isolada do sistema
                botao_sim_desk = desktop.child_window(title="Sim", class_name="TcxButton", control_type="Button")
                botao_sim_desk.wait('ready', timeout=5)
                botao_sim_desk.click_input()

            print(f"Registro {contador} excluído com sucesso!\n")
            contador += 1
            time.sleep(1) # Pausa pequena antes de reiniciar o ciclo

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
