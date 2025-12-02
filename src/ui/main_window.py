"""
Main Window Module
Janela principal da interface gráfica do NoTouchPad

Author: Renato Castellani
Version: 1.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
import threading
import time

class MainWindow:
    """
    Janela principal da aplicação
    """
    
    def __init__(self):
        self.root = None
        self.is_running = False
        self.setup_window()
        self.create_widgets()
    
    def setup_window(self):
        """
        Configura a janela principal
        """
        self.root = tk.Tk()
        self.root.title("NoTouchPad v1.0.0 - Gamepad por Webcam")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Centraliza a janela
        self.center_window()
        
        # Configura o fechamento da janela
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
    
    def center_window(self):
        """
        Centraliza a janela na tela
        """
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """
        Cria os widgets da interface
        """
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(
            main_frame, 
            text="🎮 NoTouchPad", 
            font=('Arial', 24, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Subtítulo
        subtitle_label = ttk.Label(
            main_frame,
            text="Gamepad controlado por webcam",
            font=('Arial', 12)
        )
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Frame da câmera (placeholder)
        camera_frame = ttk.LabelFrame(main_frame, text="📹 Preview da Câmera", padding="10")
        camera_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        camera_frame.columnconfigure(0, weight=1)
        camera_frame.rowconfigure(0, weight=1)
        
        # Placeholder para preview
        self.camera_placeholder = tk.Label(
            camera_frame,
            text="📷 Câmera será exibida aqui\n\n(Em desenvolvimento)",
            bg="#f0f0f0",
            font=('Arial', 14),
            width=50,
            height=15
        )
        self.camera_placeholder.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Frame de controles
        controls_frame = ttk.LabelFrame(main_frame, text="🎮 Controles", padding="10")
        controls_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Botões
        self.start_button = ttk.Button(
            controls_frame,
            text="▶️ Iniciar Detecção",
            command=self.start_detection,
            style="Accent.TButton"
        )
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(
            controls_frame,
            text="⏹️ Parar",
            command=self.stop_detection,
            state="disabled"
        )
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        self.config_button = ttk.Button(
            controls_frame,
            text="⚙️ Configurações",
            command=self.show_settings
        )
        self.config_button.grid(row=0, column=2)
        
        # Status
        status_frame = ttk.LabelFrame(main_frame, text="📊 Status", padding="10")
        status_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(
            status_frame,
            text="💤 NoTouchPad pronto para usar",
            font=('Arial', 10)
        )
        self.status_label.grid(row=0, column=0, sticky=(tk.W,))
        
        # Informações da versão
        version_frame = ttk.Frame(main_frame)
        version_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))
        
        ttk.Label(
            version_frame,
            text="v1.0.0 | Desenvolvido por Renato Castellani",
            font=('Arial', 8),
            foreground="gray"
        ).grid(row=0, column=0)
        
        # Configurar weights para expansão
        main_frame.rowconfigure(2, weight=1)
    
    def start_detection(self):
        """
        Inicia a detecção de gestos (simulado)
        """
        if not self.is_running:
            self.is_running = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.status_label.config(text="🟢 Detectando gestos... (Simulado)")
            
            # Simula detecção em thread separada
            threading.Thread(target=self.simulate_detection, daemon=True).start()
    
    def stop_detection(self):
        """
        Para a detecção de gestos
        """
        self.is_running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_label.config(text="🔴 Detecção parada")
        self.camera_placeholder.config(text="📷 Câmera será exibida aqui\n\n(Em desenvolvimento)")
    
    def simulate_detection(self):
        """
        Simula detecção de gestos para demonstração
        """
        gestures = ["✊ Punho", "✋ Mão Aberta", "👆 Apontando", "👍 Joinha", "🤚 Pare"]
        counter = 0
        
        while self.is_running:
            gesture = gestures[counter % len(gestures)]
            # Atualiza UI de forma thread-safe
            self.root.after(0, self.update_gesture_display, gesture)
            time.sleep(2)  # Muda gesto a cada 2 segundos
            counter += 1
    
    def update_gesture_display(self, gesture: str):
        """
        Atualiza a exibição do gesto atual
        """
        if self.is_running:
            self.camera_placeholder.config(
                text=f"📷 Simulando Detecção\n\nGesto Atual: {gesture}\n\n(Em desenvolvimento)"
            )
            self.status_label.config(text=f"🟢 Gesto detectado: {gesture}")
    
    def show_settings(self):
        """
        Mostra janela de configurações (placeholder)
        """
        messagebox.showinfo(
            "Configurações",
            "⚙️ Configurações em desenvolvimento!\n\n"
            "Em breve você poderá configurar:\n"
            "• Mapeamento de gestos\n"
            "• Sensibilidade da câmera\n"
            "• Calibração personalizada\n"
            "• E muito mais!"
        )
    
    def on_closing(self):
        """
        Trata o fechamento da janela
        """
        if self.is_running:
            self.stop_detection()
        
        if messagebox.askokcancel("Sair", "Deseja realmente sair do NoTouchPad?"):
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """
        Inicia o loop principal da interface
        """
        print("🖥️  Interface gráfica iniciada")
        self.root.mainloop()
        print("🖥️  Interface gráfica encerrada")
