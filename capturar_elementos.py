import time
import win32api
import win32con
from pywinauto import Desktop

def main():
    print("=" * 60)
    print(" CAPTURADOR DE ELEMENTOS DA TELA")
    print("=" * 60)
    print(" 1. Mova o mouse sobre o botão, campo ou tabela que deseja.")
    print(" 2. Pressione a tecla [ F8 ] para capturar os detalhes.")
    print(" 3. Pressione a tecla [ ESC ] para sair do capturador.")
    print("=" * 60)
    print(" Aguardando você pressionar F8...")
    print()

    desktop = Desktop(backend="uia")

    while True:
        # Verifica se F8 foi pressionado
        if win32api.GetAsyncKeyState(win32con.VK_F8) & 0x8000:
            try:
                x, y = win32api.GetCursorPos()
                print(f"Capturando elemento na posição X:{x} Y:{y} ...")
                
                # Obtém o elemento UIA abaixo do cursor
                elem = desktop.from_point(x, y)
                
                info = (
                    "-" * 50 + "\n"
                    f"DADOS CAPTURADOS EM: {time.strftime('%H:%M:%S')} (X:{x} Y:{y})\n"
                    f"  Title (Name) : '{elem.window_text()}'\n"
                    f"  ClassName    : '{elem.class_name()}'\n"
                    f"  ControlType  : '{elem.element_info.control_type}'\n"
                    f"  AutomationId : '{elem.element_info.automation_id}'\n"
                )
                
                # Mostra também o elemento pai para ajudar no contexto
                try:
                    parent = elem.parent()
                    info += f"  Janela/Pai   : '{parent.window_text()}' (Class: {parent.class_name()})\n"
                except:
                    pass
                
                info += "-" * 50 + "\n"
                
                # Imprime na tela
                print(info)
                print("Pronto para capturar o próximo (pressione F8 novamente)...")

                # Salva no arquivo .txt
                with open("elementos_capturados.txt", "a", encoding="utf-8") as f:
                    f.write(info)

            except Exception as e:
                print(f"\n[ERRO] Não foi possível capturar o elemento: {e}")
            
            # Aguarda meio segundo para não capturar várias vezes por um único clique da tecla
            time.sleep(0.5)
            
        # Verifica se ESC foi pressionado para sair
        if win32api.GetAsyncKeyState(win32con.VK_ESCAPE) & 0x8000:
            print("\nEncerrando o capturador...")
            break
            
        # Pequena pausa para não consumir 100% da CPU
        time.sleep(0.05)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Erro fatal: {e}")
    finally:
        print()
        input("Pressione ENTER para fechar a janela...")
