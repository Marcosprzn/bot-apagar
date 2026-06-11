import time
from pywinauto import Desktop

def main():
    print("Iniciando o bot de automação do MEGA ERP...")
    
    # Utilizando o backend 'uia' pois os arquivos txt mostram propriedades do UIAutomation (ex: UIA_ButtonControlTypeId)
    desktop = Desktop(backend="uia")
    
    # Tenta encontrar a janela principal do Mega ERP
    # Título como "Mega Empresarial - Sistemas de Gestão Empresarial..."
    print("Aguardando a janela principal do Mega ERP...")
    try:
        janela_principal = desktop.window(title_re=".*Mega Empresarial.*")
        janela_principal.wait('visible', timeout=15)
    except Exception as e:
        print(f"Erro ao encontrar a janela do Mega ERP: {e}")
        return

    # 1. Clicar em @[botao procurar.txt]
    # Botão está na janela "Movimento Financeiro" (filho da janela principal)
    print("Clicando no botão Procurar...")
    try:
        # AutomationId: "66582", ClassName: "TMgBitBtn", Name: "Procurar"
        botao_procurar = janela_principal.child_window(auto_id="66582", control_type="Button")
        botao_procurar.click_input()
        time.sleep(1.5)  # Aguarda a janela de busca abrir
    except Exception as e:
        print(f"Erro ao clicar no botão Procurar: {e}")
        return

    # Localiza a janela filha "Procurar Movimento Financeiro" que abriu
    print("Aguardando a janela de pesquisa abrir...")
    try:
        janela_busca = desktop.window(title_re=".*Procurar Movimento Financeiro.*")
        janela_busca.wait('visible', timeout=10)
    except Exception as e:
        print(f"Erro ao encontrar a janela de pesquisa: {e}")
        return

    # 2. Colocar data em @[campo data um.txt]
    print("Inserindo a primeira data (01/01/2026)...")
    try:
        # AutomationId: "197502", ClassName: "TcxCustomDropDownInnerEdit"
        campo_data_um = janela_busca.child_window(auto_id="197502", control_type="Edit")
        campo_data_um.click_input()
        campo_data_um.set_edit_text("01/01/2026")
        time.sleep(0.5)
    except Exception as e:
        print(f"Erro ao inserir a primeira data: {e}")

    # 3. Colocar data em @[campo data dois.txt]
    print("Inserindo a segunda data (31/05/2026)...")
    try:
        # AutomationId: "197490", ClassName: "TcxCustomDropDownInnerEdit"
        campo_data_dois = janela_busca.child_window(auto_id="197490", control_type="Edit")
        campo_data_dois.click_input()
        campo_data_dois.set_edit_text("31/05/2026")
        time.sleep(0.5)
    except Exception as e:
        print(f"Erro ao inserir a segunda data: {e}")

    # 4. Clicar no primeiro item da tabela @[dados tabela.txt]
    # O botão "Selecionar" está na janela principal (Movimento Financeiro)
    print("Clicando no botão Selecionar (primeiro item da tabela)...")
    try:
        # AutomationId: "1115764", ClassName: "TMgSpeedButton", Name: "Selecionar"
        botao_selecionar = janela_principal.child_window(auto_id="1115764", control_type="Button")
        botao_selecionar.click_input()
        time.sleep(1)
    except Exception as e:
        print(f"Erro ao clicar no item da tabela: {e}")

    # 5. Clicar no botão Aplicar @[botao aplicar.txt]
    print("Clicando no botão Aplicar...")
    try:
        # AutomationId: "132308", ClassName: "TMgBitBtn", Name: "Aplicar"
        # Este botão aparece na janela de busca (Procurar Movimento Financeiro)
        botao_aplicar = janela_busca.child_window(auto_id="132308", control_type="Button")
        botao_aplicar.click_input()
        time.sleep(1)
    except Exception as e:
        print(f"Erro ao clicar no botão Aplicar: {e}")

    print("\nTodos os passos concluídos com sucesso!")

if __name__ == "__main__":
    main()
