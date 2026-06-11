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

    # 1. Clicar em @[botao procurar.txt]
    # NOTA: AutomationId muda a cada sessao. Usamos ClassName + title (estáveis).
    # ClassName: "TMgBitBtn", Name: "Procurar"
    print("Clicando no botão Procurar...")
    try:
        botao_procurar = janela_principal.child_window(
            title="Procurar",
            class_name="TMgBitBtn",
            control_type="Button"
        )
        botao_procurar.click_input()
        time.sleep(1.5)  # Aguarda a janela de busca abrir
    except Exception as e:
        print(f"Erro ao clicar no botão Procurar: {e}")
        return

    # Localiza a janela "Procurar Movimento Financeiro" que abriu
    print("Aguardando a janela de pesquisa abrir...")
    try:
        janela_busca = desktop.window(title_re=".*Procurar Movimento Financeiro.*")
        janela_busca.wait('visible', timeout=10)
    except Exception as e:
        print(f"Erro ao encontrar a janela de pesquisa: {e}")
        return

    # 2 e 3. Preencher campos de data (se necessário)
    # ClassName: "TcxCustomDropDownInnerEdit" - campos aninhados dentro de paineis.
    # Usa descendants() para buscar em toda a hierarquia (nao apenas filhos diretos).
    # Se as datas já estiverem corretas, pula o preenchimento.
    DATA_INICIO = "01/01/2026"
    DATA_FIM    = "31/05/2026"

    print("Buscando campos de data na janela...")
    try:
        campos_data = janela_busca.descendants(class_name="TcxCustomDropDownInnerEdit")
        print(f"  Campos de data encontrados: {len(campos_data)}")

        if len(campos_data) < 2:
            print(f"  AVISO: Esperava 2 campos de data, encontrou {len(campos_data)}.")
            for i, c in enumerate(campos_data):
                print(f"    Campo {i}: rect={c.rectangle()}")
        else:
            # Ordena pela posição horizontal: esquerda = data início, direita = data fim
            campos_data = sorted(campos_data, key=lambda c: c.rectangle().left)
            campo_inicio = campos_data[0]
            campo_fim    = campos_data[1]

            # Lê os valores atuais dos campos (IsValuePatternAvailable = true)
            try:
                valor_inicio = campo_inicio.get_value()
                valor_fim    = campo_fim.get_value()
            except:
                valor_inicio = ""
                valor_fim    = ""

            print(f"  Data início atual : '{valor_inicio}'")
            print(f"  Data fim atual    : '{valor_fim}'")

            # Só preenche se o valor estiver diferente do esperado
            if valor_inicio == DATA_INICIO:
                print(f"  Data início já está correta, pulando...")
            else:
                print(f"  Inserindo data início: {DATA_INICIO}")
                campo_inicio.click_input()
                campo_inicio.type_keys("^a01012026", with_spaces=False)
                time.sleep(0.5)

            if valor_fim == DATA_FIM:
                print(f"  Data fim já está correta, pulando...")
            else:
                print(f"  Inserindo data fim: {DATA_FIM}")
                campo_fim.click_input()
                campo_fim.type_keys("^a31052026", with_spaces=False)
                time.sleep(0.5)

    except Exception as e:
        print(f"Erro ao preencher campos de data: {e}")

    # 4. Clicar no primeiro item da tabela @[dados tabela.txt]
    # ClassName: "TMgSpeedButton", Name: "Selecionar"
    print("Clicando no botão Selecionar (primeiro item da tabela)...")
    try:
        botao_selecionar = janela_principal.child_window(
            title="Selecionar",
            class_name="TMgSpeedButton",
            control_type="Button"
        )
        botao_selecionar.click_input()
        time.sleep(1)
    except Exception as e:
        print(f"Erro ao clicar no item da tabela: {e}")

    # 5. Clicar no botão Aplicar @[botao aplicar.txt]
    # ClassName: "TMgBitBtn", Name: "Aplicar"
    print("Clicando no botão Aplicar...")
    try:
        botao_aplicar = janela_busca.child_window(
            title="Aplicar",
            class_name="TMgBitBtn",
            control_type="Button"
        )
        botao_aplicar.click_input()
        time.sleep(1)
    except Exception as e:
        print(f"Erro ao clicar no botão Aplicar: {e}")

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
