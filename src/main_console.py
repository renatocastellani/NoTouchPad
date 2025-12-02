#!/usr/bin/env python3
"""
NoTouchPad - Console Version (Para teste de standalone)
Versão em linha de comando para testar o pipeline de build

Author: Renato Castellani
Version: 1.0.0
"""

import sys
import time
import threading
from pathlib import Path

class NoTouchPadConsole:
    """
    Versão console do NoTouchPad para teste de build
    """
    
    def __init__(self):
        self.is_running = False
        self.gestures = ["✊ Punho", "✋ Mão Aberta", "👆 Apontando", "👍 Joinha", "🤚 Pare"]
        self.current_gesture_index = 0
    
    def print_header(self):
        """
        Mostra o cabeçalho da aplicação
        """
        print("\n" + "="*60)
        print("🎮 NOTOUCHPAD v1.0.0")
        print("Gamepad controlado por webcam")
        print("="*60)
        print("📝 Desenvolvido por: Renato Castellani")
        print("🏗️  Versão: Standalone Console Test")
        print("="*60 + "\n")
    
    def print_menu(self):
        """
        Mostra o menu de opções
        """
        print("📋 MENU DE OPÇÕES:")
        print("1. ▶️  Iniciar simulação de detecção")
        print("2. ⏹️  Parar simulação")
        print("3. ℹ️  Informações do sistema")
        print("4. ❌ Sair")
        print("\n" + "-"*40)
    
    def show_system_info(self):
        """
        Mostra informações do sistema
        """
        print("\n📊 INFORMAÇÕES DO SISTEMA:")
        print(f"🐍 Python: {sys.version}")
        print(f"💽 Plataforma: {sys.platform}")
        print(f"📁 Diretório atual: {Path.cwd()}")
        print(f"📦 Executável: {sys.executable}")
        print(f"🔧 Argumentos: {sys.argv}")
        
        # Testa imports básicos
        print("\n🧪 TESTE DE DEPENDÊNCIAS:")
        dependencies = [
            ("threading", "threading"),
            ("time", "time"),
            ("sys", "sys"),
            ("pathlib", "pathlib"),
        ]
        
        for name, module in dependencies:
            try:
                __import__(module)
                print(f"✅ {name}: OK")
            except ImportError:
                print(f"❌ {name}: ERRO")
        
        print("\n" + "-"*40)
    
    def simulate_gesture_detection(self):
        """
        Simula a detecção de gestos
        """
        while self.is_running:
            gesture = self.gestures[self.current_gesture_index]
            print(f"🎯 Gesto detectado: {gesture}")
            
            # Simula comando do gamepad
            commands = {
                "✊ Punho": "Botão A pressionado",
                "✋ Mão Aberta": "Botão B pressionado", 
                "👆 Apontando": "Analógico movendo",
                "👍 Joinha": "Start pressionado",
                "🤚 Pare": "Todos botões liberados"
            }
            
            print(f"🎮 Comando: {commands.get(gesture, 'Comando desconhecido')}")
            print("-" * 30)
            
            self.current_gesture_index = (self.current_gesture_index + 1) % len(self.gestures)
            time.sleep(2)  # Simula detecção a cada 2 segundos
    
    def start_detection(self):
        """
        Inicia a simulação de detecção
        """
        if not self.is_running:
            self.is_running = True
            print("\n🟢 INICIANDO DETECÇÃO SIMULADA...")
            print("(Pressione Ctrl+C para parar)\n")
            
            # Executa em thread separada
            detection_thread = threading.Thread(target=self.simulate_gesture_detection, daemon=True)
            detection_thread.start()
            
            try:
                # Loop principal - aguarda interrupção
                while self.is_running:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                self.stop_detection()
        else:
            print("⚠️  Detecção já está rodando!")
    
    def stop_detection(self):
        """
        Para a simulação
        """
        if self.is_running:
            self.is_running = False
            print("\n🔴 DETECÇÃO PARADA")
            print("💤 NoTouchPad em standby...\n")
        else:
            print("⚠️  Detecção já está parada!")
    
    def run(self):
        """
        Loop principal da aplicação console
        """
        self.print_header()
        
        while True:
            self.print_menu()
            
            try:
                choice = input("Escolha uma opção (1-4): ").strip()
                
                if choice == "1":
                    self.start_detection()
                elif choice == "2":
                    self.stop_detection()
                elif choice == "3":
                    self.show_system_info()
                elif choice == "4":
                    print("\n👋 Encerrando NoTouchPad...")
                    self.stop_detection()
                    print("✅ Encerrado com sucesso!")
                    break
                else:
                    print("❌ Opção inválida! Digite 1, 2, 3 ou 4.")
                
                print()  # Linha em branco
                
            except KeyboardInterrupt:
                print("\n\n⏸️  Interrompido pelo usuário...")
                self.stop_detection()
                print("👋 Até logo!")
                break
            except EOFError:
                print("\n\n👋 Saindo...")
                break

def main():
    """
    Função principal da aplicação
    """
    try:
        app = NoTouchPadConsole()
        app.run()
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        print("📞 Reporte este erro para o desenvolvedor")
        sys.exit(1)

if __name__ == "__main__":
    main()