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

    # 1. Clicar no botão "Procurar"
    print("Clicando no botão Procurar...")
    try:
        botao_procurar = janela_principal.child_window(
            title="Procurar",
            class_name="TMgBitBtn",
            control_type="Button"
        )
        botao_procurar.click_input()
        time.sleep(2)  # Aguarda a janela de busca abrir
    except Exception as e:
        print(f"Erro ao clicar no botão Procurar: {e}")
        return

    # 2. Localiza a janela "Procurar Movimento Financeiro" e clica em Aplicar
    print("Aguardando a janela de pesquisa...")
    try:
        janela_busca = desktop.window(title_re=".*Procurar Movimento Financeiro.*")
        janela_busca.wait('visible', timeout=10)

        print("Clicando no botão Aplicar (pulando datas)...")
        botao_aplicar = janela_busca.child_window(
            title="Aplicar",
            class_name="TMgBitBtn",
            control_type="Button"
        )
        botao_aplicar.click_input()
        time.sleep(3)  # Aguarda a tabela carregar e a janela de busca fechar
    except Exception as e:
        print(f"Erro ao interagir com a janela de pesquisa (Aplicar): {e}")
        return

    # 3. Interagir com a Tabela na janela principal (Movimento Financeiro)
    print("Aguardando os resultados carregarem na tabela...")
    try:
        # Pega a janela principal novamente
        janela_resultados = None
        for padrao in padroes:
            try:
                janela_resultados = desktop.window(title_re=padrao)
                janela_resultados.wait('visible', timeout=5)
                break
            except:
                continue
                
        if not janela_resultados:
            print("Janela de resultados não encontrada.")
            return

        # Localiza o TcxGridSite (tabela)
        tabela = janela_resultados.child_window(class_name="TcxGridSite", control_type="Pane")
        tabela.wait('visible', timeout=10)
        print("Tabela encontrada. Clicando no primeiro item...")

        # Tenta clicar no primeiro item via controle filho ou fallback por coordenada relativa
        try:
            # TcxGridSite às vezes expõe as linhas como filhos
            itens = tabela.children()
            if itens:
                itens[0].click_input()
            else:
                raise Exception("Sem filhos detectados")
        except:
            # Fallback: clica na coordenada (x=30, y=30) relativa ao topo esquerdo da tabela
            # Isso costuma acertar a primeira linha de dados
            rect = tabela.rectangle()
            import win32api, win32con
            x_click = rect.left + 50
            y_click = rect.top + 30
            # Usar click_input na tabela passando as coords
            tabela.click_input(coords=(50, 30))
        
        time.sleep(1)

        # 4. Clicar no botão Selecionar
        print("Clicando no botão Selecionar...")
        botao_selecionar = janela_resultados.child_window(
            title="Selecionar",
            class_name="TMgSpeedButton",
            control_type="Button"
        )
        botao_selecionar.click_input()
        time.sleep(1)

    except Exception as e:
        print(f"Erro ao interagir com a tabela ou botão Selecionar: {e}")

    print("\nTodos os passos concluídos com sucesso!")

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
