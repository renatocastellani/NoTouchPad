#!/usr/bin/env python3
"""
NoTouchPad - GUI Terminal Version
Interface "gráfica" usando terminal com caracteres ASCII e cores
Simula uma interface gráfica completa no terminal

Author: Renato Castellani
Version: 1.0.0
"""

import os
import sys
import time
import threading
import subprocess
from pathlib import Path

class TerminalGUI:
    """
    Interface "gráfica" usando terminal com ASCII art e cores
    """
    
    def __init__(self):
        self.is_running = False
        self.is_auto_simulation = False
        self.current_gesture = "Nenhum"
        self.current_command = "Standby"
        self.gestures = ["✊ Punho", "✋ Mão Aberta", "👆 Apontando", "👍 Joinha", "🤚 Pare"]
        self.commands = {
            "✊ Punho": "🎮 Botão A",
            "✋ Mão Aberta": "🎮 Botão B", 
            "👆 Apontando": "🕹️ Analógico",
            "👍 Joinha": "⏯️ Start",
            "🤚 Pare": "⏹️ Stop"
        }
        self.gesture_index = 0
        self.messages = []
        self.max_messages = 5
    
    def clear_screen(self):
        """
        Limpa a tela do terminal
        """
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def get_terminal_size(self):
        """
        Obtém o tamanho do terminal
        """
        try:
            size = os.get_terminal_size()
            return size.columns, size.lines
        except:
            return 80, 24  # Padrão
    
    def add_message(self, message):
        """
        Adiciona mensagem ao log
        """
        timestamp = time.strftime("%H:%M:%S")
        self.messages.append(f"[{timestamp}] {message}")
        
        # Mantém apenas as últimas mensagens
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
        
        # Log no console para debug
        print(f"LOG: {message}", file=sys.stderr)
    
    def draw_header(self, width):
        """
        Desenha o cabeçalho da aplicação
        """
        lines = []
        lines.append("═" * width)
        lines.append("🎮 NOTOUCHPAD v1.0.0 - Interface Gráfica Terminal".center(width))
        lines.append("Gamepad Controlado por Webcam".center(width))
        lines.append("═" * width)
        return lines
    
    def draw_status_panel(self, width):
        """
        Desenha painel de status atual
        """
        lines = []
        lines.append("┌" + "─" * (width-2) + "┐")
        lines.append(f"│ 📊 STATUS ATUAL{' ' * (width-18)}│")
        lines.append("├" + "─" * (width-2) + "┤")
        
        # Status da detecção
        status_text = "🟢 ATIVO" if self.is_running else "🔴 PARADO"
        auto_text = " (Auto)" if self.is_auto_simulation else " (Manual)"
        status_line = f"│ Detecção: {status_text}{auto_text}"
        lines.append(status_line + " " * (width - len(status_line) - 1) + "│")
        
        # Gesto atual
        gesture_line = f"│ Gesto: {self.current_gesture}"
        lines.append(gesture_line + " " * (width - len(gesture_line) - 1) + "│")
        
        # Comando atual
        command_line = f"│ Comando: {self.current_command}"
        lines.append(command_line + " " * (width - len(command_line) - 1) + "│")
        
        lines.append("└" + "─" * (width-2) + "┘")
        return lines
    
    def draw_camera_preview(self, width, height):
        """
        Desenha simulação do preview da câmera
        """
        lines = []
        preview_height = height - 2
        
        lines.append("┌" + "─" * (width-2) + "┐")
        lines.append(f"│ 📹 PREVIEW DA CÂMERA{' ' * (width-22)}│")
        lines.append("├" + "─" * (width-2) + "┤")
        
        # Área de preview
        for i in range(preview_height - 3):
            if i == preview_height // 2 - 2:
                # Mostra o gesto atual no centro
                if self.is_running:
                    gesture_display = f"🎯 {self.current_gesture}"
                else:
                    gesture_display = "📷 Câmera em Standby"
                content = gesture_display.center(width-4)
                lines.append(f"│ {content} │")
            elif i == preview_height // 2:
                # Mostra o comando
                command_display = f"{self.current_command}"
                content = command_display.center(width-4)
                lines.append(f"│ {content} │")
            elif i == preview_height // 2 + 2:
                # Indicador visual
                if self.is_running:
                    indicator = "●●● DETECTANDO ●●●"
                else:
                    indicator = "○○○ AGUARDANDO ○○○"
                content = indicator.center(width-4)
                lines.append(f"│ {content} │")
            else:
                lines.append("│" + " " * (width-2) + "│")
        
        lines.append("└" + "─" * (width-2) + "┘")
        return lines
    
    def draw_buttons_panel(self, width):
        """
        Desenha painel de botões de controle
        """
        lines = []
        lines.append("┌" + "─" * (width-2) + "┐")
        lines.append(f"│ 🎮 CONTROLES{' ' * (width-14)}│")
        lines.append("├" + "─" * (width-2) + "┤")
        
        # Botões principais
        if not self.is_running:
            lines.append(f"│ [1] ▶️  Iniciar Detecção Manual{' ' * (width-32)}│")
            lines.append(f"│ [2] 🔄 Iniciar Simulação Auto{' ' * (width-31)}│")
        else:
            lines.append(f"│ [1] ⏹️  Parar Detecção{' ' * (width-23)}│")
            lines.append(f"│ [2] ---{' ' * (width-11)}│")
        
        # Botões de gestos manuais
        lines.append("├" + "─" * (width-2) + "┤")
        lines.append(f"│ 👆 GESTOS MANUAIS:{' ' * (width-21)}│")
        lines.append(f"│ [A] ✊ Punho → Botão A{' ' * (width-23)}│")
        lines.append(f"│ [B] ✋ Mão Aberta → Botão B{' ' * (width-27)}│")
        lines.append(f"│ [C] 👆 Apontar → Analógico{' ' * (width-26)}│")
        lines.append(f"│ [D] 👍 Joinha → Start{' ' * (width-22)}│")
        lines.append(f"│ [E] 🤚 Pare → Stop{' ' * (width-19)}│")
        
        lines.append("├" + "─" * (width-2) + "┤")
        lines.append(f"│ [Q] 🚪 Sair do Programa{' ' * (width-24)}│")
        lines.append("└" + "─" * (width-2) + "┘")
        return lines
    
    def draw_messages_panel(self, width):
        """
        Desenha painel de mensagens/log
        """
        lines = []
        lines.append("┌" + "─" * (width-2) + "┐")
        lines.append(f"│ 📝 MENSAGENS{' ' * (width-15)}│")
        lines.append("├" + "─" * (width-2) + "┤")
        
        # Exibe mensagens
        for i in range(self.max_messages):
            if i < len(self.messages):
                message = self.messages[i]
                if len(message) > width-4:
                    message = message[:width-7] + "..."
                message_line = f"│ {message}"
                lines.append(message_line + " " * (width - len(message_line) - 1) + "│")
            else:
                lines.append("│" + " " * (width-2) + "│")
        
        lines.append("└" + "─" * (width-2) + "┘")
        return lines
    
    def render_screen(self):
        """
        Renderiza toda a tela
        """
        width, height = self.get_terminal_size()
        width = min(width, 80)  # Limita largura máxima
        
        self.clear_screen()
        
        all_lines = []
        
        # Cabeçalho
        all_lines.extend(self.draw_header(width))
        all_lines.append("")  # Linha em branco
        
        # Painel de status (compacto)
        all_lines.extend(self.draw_status_panel(width))
        all_lines.append("")
        
        # Preview da câmera
        camera_height = 8
        all_lines.extend(self.draw_camera_preview(width, camera_height))
        all_lines.append("")
        
        # Painel de botões
        all_lines.extend(self.draw_buttons_panel(width))
        all_lines.append("")
        
        # Painel de mensagens
        all_lines.extend(self.draw_messages_panel(width))
        
        # Exibe na tela
        for line in all_lines:
            print(line)
        
        # Prompt de entrada
        print("\n> Digite um comando: ", end="", flush=True)
    
    def simulate_gesture_detection(self):
        """
        Simula detecção automática de gestos
        """
        while self.is_running and self.is_auto_simulation:
            # Próximo gesto
            gesture = self.gestures[self.gesture_index]
            command = self.commands[gesture]
            
            self.current_gesture = gesture
            self.current_command = command
            
            # Adiciona mensagem
            self.add_message(f"Detectado: {gesture} → {command}")
            
            # Atualiza tela
            self.render_screen()
            
            # Próximo gesto
            self.gesture_index = (self.gesture_index + 1) % len(self.gestures)
            
            # Aguarda
            for _ in range(20):  # 2 segundos divididos em 0.1s cada
                if not (self.is_running and self.is_auto_simulation):
                    break
                time.sleep(0.1)
    
    def simulate_manual_gesture(self, gesture_key):
        """
        Simula gesto manual
        """
        gesture_map = {
            'a': "✊ Punho",
            'b': "✋ Mão Aberta",
            'c': "👆 Apontando", 
            'd': "👍 Joinha",
            'e': "🤚 Pare"
        }
        
        if gesture_key in gesture_map:
            gesture = gesture_map[gesture_key]
            command = self.commands[gesture]
            
            self.current_gesture = gesture
            self.current_command = command
            
            self.add_message(f"Manual: {gesture} → {command}")
            
            # Simula ativação por 1 segundo
            self.render_screen()
            time.sleep(1)
            
            # Volta ao standby se não estiver em auto
            if not self.is_auto_simulation:
                self.current_gesture = "Standby"
                self.current_command = "Aguardando..."
            
            return True
        return False
    
    def start_auto_detection(self):
        """
        Inicia detecção automática
        """
        if not self.is_running:
            self.is_running = True
            self.is_auto_simulation = True
            self.add_message("🔄 Simulação automática iniciada")
            
            # Thread para simulação
            thread = threading.Thread(target=self.simulate_gesture_detection, daemon=True)
            thread.start()
    
    def start_manual_detection(self):
        """
        Inicia modo manual
        """
        if not self.is_running:
            self.is_running = True
            self.is_auto_simulation = False
            self.current_gesture = "Aguardando gesto manual..."
            self.current_command = "Use as teclas A-E"
            self.add_message("👆 Modo manual ativado - Use teclas A-E")
    
    def stop_detection(self):
        """
        Para qualquer detecção
        """
        if self.is_running:
            self.is_running = False
            self.is_auto_simulation = False
            self.current_gesture = "Parado"
            self.current_command = "Sistema em standby"
            self.add_message("⏹️ Detecção parada")
    
    def process_input(self, user_input):
        """
        Processa entrada do usuário
        """
        cmd = user_input.strip().lower()
        
        if cmd == '1':
            if not self.is_running:
                self.start_manual_detection()
            else:
                self.stop_detection()
        elif cmd == '2':
            if not self.is_running:
                self.start_auto_detection()
        elif cmd in ['a', 'b', 'c', 'd', 'e']:
            if self.simulate_manual_gesture(cmd):
                pass  # Gesto processado
            else:
                self.add_message(f"❌ Gesto '{cmd.upper()}' não reconhecido")
        elif cmd == 'q':
            return False  # Sair
        else:
            self.add_message(f"❌ Comando '{cmd}' não reconhecido")
        
        return True
    
    def run(self):
        """
        Loop principal da interface
        """
        self.add_message("🎮 NoTouchPad Terminal GUI iniciado")
        self.add_message("💡 Use os comandos 1-2 para controlar")
        
        while True:
            self.render_screen()
            
            try:
                user_input = input()
                
                if not self.process_input(user_input):
                    break
                    
            except KeyboardInterrupt:
                print("\n\n⏸️ Interrompido pelo usuário...")
                break
            except EOFError:
                print("\n\n👋 Saindo...")
                break
        
        self.stop_detection()
        self.add_message("👋 Encerrando NoTouchPad...")
        time.sleep(1)

def main():
    """
    Função principal da aplicação GUI
    """
    print("🎮 Iniciando NoTouchPad Terminal GUI...")
    
    try:
        gui = TerminalGUI()
        gui.run()
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        print("📞 Reporte este erro para o desenvolvedor")
        sys.exit(1)

if __name__ == "__main__":
    main()