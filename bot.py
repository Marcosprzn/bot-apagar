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

    # O bot agora vai focar apenas em clicar no botão "Aplicar" e depois "Selecionar"
    
    # Localiza a janela "Procurar Movimento Financeiro"
    print("Aguardando a janela de pesquisa abrir...")
    try:
        janela_busca = desktop.window(title_re=".*Procurar Movimento Financeiro.*")
        janela_busca.wait('visible', timeout=10)
    except Exception as e:
        print(f"Erro ao encontrar a janela de pesquisa: {e}")
        return

    # 1. Clicar no botão Aplicar @[botao aplicar.txt]
    # ClassName: "TMgBitBtn", Name: "Aplicar"
    print("Clicando no botão Aplicar...")
    try:
        botao_aplicar = janela_busca.child_window(
            title="Aplicar",
            class_name="TMgBitBtn",
            control_type="Button"
        )
        botao_aplicar.click_input()
        time.sleep(2) # Aguarda a tabela carregar e a janela fechar
    except Exception as e:
        print(f"Erro ao clicar no botão Aplicar: {e}")

    # 2. Clicar no primeiro item da tabela @[dados tabela.txt]
    # O botão "Selecionar" está na janela principal (Movimento Financeiro)
    print("Clicando no botão Selecionar (primeiro item da tabela)...")
    try:
        # Pega a janela principal novamente
        janela_principal = None
        padroes = [
            ".*Mega Empresarial.*",
            ".*Mega ERP.*",
            ".*Movimento Financeiro.*",
        ]
        for padrao in padroes:
            try:
                janela_principal = desktop.window(title_re=padrao)
                janela_principal.wait('visible', timeout=5)
                break
            except:
                continue
                
        if janela_principal:
            botao_selecionar = janela_principal.child_window(
                title="Selecionar",
                class_name="TMgSpeedButton",
                control_type="Button"
            )
            botao_selecionar.click_input()
            time.sleep(1)
        else:
            print("Janela principal não encontrada para clicar em Selecionar.")
    except Exception as e:
        print(f"Erro ao clicar no item da tabela: {e}")

    print("\nPassos do 'Aplicar' em diante concluídos com sucesso!")

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
