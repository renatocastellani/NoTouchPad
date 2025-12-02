#!/usr/bin/env python3
"""
NoTouchPad - Web GUI Minimal
Interface gráfica web usando apenas bibliotecas padrão do Python
Preparada para exibir webcam no futuro

Author: Renato Castellani
Version: 1.0.0
"""

import http.server
import socketserver
import threading
import webbrowser
import json
import time
import os
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

class NoTouchPadWebGUI:
    """
    Interface gráfica web para o NoTouchPad
    """
    
    def __init__(self, port=8080):
        self.port = port
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
        self.max_messages = 10
        
    def add_message(self, message):
        """
        Adiciona mensagem ao log
        """
        timestamp = time.strftime("%H:%M:%S")
        self.messages.append(f"[{timestamp}] {message}")
        
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
        
        print(f"LOG: {message}", file=sys.stderr)
    
    def get_html_template(self):
        """
        Template HTML da interface
        """
        return """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NoTouchPad v1.0.0</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-gap: 20px;
            height: calc(100vh - 40px);
        }
        
        .panel {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .header {
            grid-column: 1 / -1;
            text-align: center;
            padding: 15px;
            margin-bottom: 20px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .camera-panel {
            display: flex;
            flex-direction: column;
        }
        
        .camera-preview {
            flex: 1;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
            border: 2px dashed rgba(255, 255, 255, 0.3);
            position: relative;
            min-height: 300px;
        }
        
        .preview-content {
            text-align: center;
            font-size: 1.5em;
        }
        
        .gesture-display {
            font-size: 3em;
            margin: 20px 0;
        }
        
        .status-panel {
            display: flex;
            flex-direction: column;
        }
        
        .status-info {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        }
        
        .status-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        
        .controls {
            margin-bottom: 20px;
        }
        
        .btn-group {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        
        .btn {
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            padding: 12px 20px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s ease;
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .btn.primary {
            background: rgba(76, 175, 80, 0.6);
        }
        
        .btn.danger {
            background: rgba(244, 67, 54, 0.6);
        }
        
        .btn.warning {
            background: rgba(255, 152, 0, 0.6);
        }
        
        .gesture-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .gesture-btn {
            padding: 15px;
            font-size: 1.1em;
            text-align: center;
        }
        
        .messages {
            flex: 1;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 15px;
            overflow-y: auto;
            max-height: 200px;
        }
        
        .message {
            margin-bottom: 5px;
            font-family: monospace;
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .indicator.active { background: #4CAF50; }
        .indicator.inactive { background: #F44336; }
        
        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
                gap: 15px;
            }
            
            .gesture-buttons {
                grid-template-columns: 1fr;
            }
            
            .btn-group {
                flex-direction: column;
            }
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header panel">
            <h1>🎮 NoTouchPad</h1>
            <p>Gamepad Controlado por Webcam - Interface Gráfica</p>
        </div>
        
        <div class="camera-panel panel">
            <h3>📹 Preview da Câmera</h3>
            <div class="camera-preview" id="cameraPreview">
                <div class="preview-content">
                    <div id="cameraStatus">📷 Câmera será exibida aqui</div>
                    <div class="gesture-display" id="gestureDisplay">🤚</div>
                    <div id="commandDisplay">Aguardando...</div>
                </div>
            </div>
        </div>
        
        <div class="status-panel panel">
            <h3>📊 Status do Sistema</h3>
            <div class="status-info">
                <div class="status-item">
                    <span>Status:</span>
                    <span><span class="indicator" id="statusIndicator"></span><span id="statusText">Parado</span></span>
                </div>
                <div class="status-item">
                    <span>Modo:</span>
                    <span id="modeText">Manual</span>
                </div>
                <div class="status-item">
                    <span>Gesto:</span>
                    <span id="currentGesture">Nenhum</span>
                </div>
                <div class="status-item">
                    <span>Comando:</span>
                    <span id="currentCommand">Standby</span>
                </div>
            </div>
            
            <div class="controls">
                <h4>🎮 Controles Principais</h4>
                <div class="btn-group">
                    <button class="btn primary" onclick="startManual()">▶️ Manual</button>
                    <button class="btn primary" onclick="startAuto()">🔄 Auto</button>
                    <button class="btn danger" onclick="stopDetection()">⏹️ Parar</button>
                </div>
                
                <h4>👋 Gestos Manuais</h4>
                <div class="gesture-buttons">
                    <button class="btn gesture-btn" onclick="sendGesture('punch')">✊ Punho</button>
                    <button class="btn gesture-btn" onclick="sendGesture('open')">✋ Aberta</button>
                    <button class="btn gesture-btn" onclick="sendGesture('point')">👆 Apontar</button>
                    <button class="btn gesture-btn" onclick="sendGesture('thumbs')">👍 Joinha</button>
                    <button class="btn gesture-btn warning" onclick="sendGesture('stop')">🤚 Pare</button>
                </div>
            </div>
            
            <div class="messages">
                <h4>📝 Log de Mensagens</h4>
                <div id="messagesList"></div>
            </div>
        </div>
    </div>
    
    <script>
        let isRunning = false;
        let isAuto = false;
        
        // Atualiza status na tela
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('statusText').textContent = data.is_running ? 'Ativo' : 'Parado';
                    document.getElementById('statusIndicator').className = 'indicator ' + (data.is_running ? 'active' : 'inactive');
                    document.getElementById('modeText').textContent = data.is_auto ? 'Automático' : 'Manual';
                    document.getElementById('currentGesture').textContent = data.gesture;
                    document.getElementById('currentCommand').textContent = data.command;
                    
                    // Atualiza preview
                    document.getElementById('gestureDisplay').textContent = data.gesture_icon || '🤚';
                    document.getElementById('commandDisplay').textContent = data.command;
                    
                    if (data.is_running) {
                        document.getElementById('cameraPreview').classList.add('pulse');
                    } else {
                        document.getElementById('cameraPreview').classList.remove('pulse');
                    }
                    
                    // Atualiza mensagens
                    const messagesList = document.getElementById('messagesList');
                    messagesList.innerHTML = data.messages.map(msg => 
                        `<div class="message">${msg}</div>`
                    ).join('');
                    messagesList.scrollTop = messagesList.scrollHeight;
                });
        }
        
        // Funções de controle
        function startManual() {
            fetch('/api/start_manual', {method: 'POST'});
        }
        
        function startAuto() {
            fetch('/api/start_auto', {method: 'POST'});
        }
        
        function stopDetection() {
            fetch('/api/stop', {method: 'POST'});
        }
        
        function sendGesture(gesture) {
            fetch('/api/gesture', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({gesture: gesture})
            });
        }
        
        // Atualiza a cada 500ms
        setInterval(updateStatus, 500);
        updateStatus(); // Primeira atualização
    </script>
</body>
</html>"""
    
    def simulate_auto_detection(self):
        """
        Simula detecção automática
        """
        while self.is_running and self.is_auto_simulation:
            gesture = self.gestures[self.gesture_index]
            command = self.commands[gesture]
            
            self.current_gesture = gesture
            self.current_command = command
            self.add_message(f"Auto: {gesture} → {command}")
            
            self.gesture_index = (self.gesture_index + 1) % len(self.gestures)
            
            for _ in range(20):  # 2 segundos
                if not (self.is_running and self.is_auto_simulation):
                    break
                time.sleep(0.1)

class NoTouchPadRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    Handler para requisições HTTP
    """
    
    def __init__(self, *args, gui_instance=None, **kwargs):
        self.gui = gui_instance
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """
        Trata requisições GET
        """
        path = urlparse(self.path).path
        
        if path == '/' or path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.gui.get_html_template().encode('utf-8'))
            
        elif path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Ícones dos gestos
            gesture_icons = {
                "✊ Punho": "✊",
                "✋ Mão Aberta": "✋", 
                "👆 Apontando": "👆",
                "👍 Joinha": "👍",
                "🤚 Pare": "🤚"
            }
            
            status = {
                'is_running': self.gui.is_running,
                'is_auto': self.gui.is_auto_simulation,
                'gesture': self.gui.current_gesture,
                'command': self.gui.current_command,
                'gesture_icon': gesture_icons.get(self.gui.current_gesture, '🤚'),
                'messages': self.gui.messages[-5:]  # Últimas 5 mensagens
            }
            
            self.wfile.write(json.dumps(status).encode('utf-8'))
        else:
            self.send_error(404)
    
    def do_POST(self):
        """
        Trata requisições POST
        """
        path = urlparse(self.path).path
        
        if path == '/api/start_manual':
            if not self.gui.is_running:
                self.gui.is_running = True
                self.gui.is_auto_simulation = False
                self.gui.current_gesture = "Manual ativo"
                self.gui.current_command = "Aguardando gesto..."
                self.gui.add_message("👆 Modo manual iniciado")
            
            self.send_response(200)
            self.end_headers()
            
        elif path == '/api/start_auto':
            if not self.gui.is_running:
                self.gui.is_running = True
                self.gui.is_auto_simulation = True
                self.gui.add_message("🔄 Simulação automática iniciada")
                
                thread = threading.Thread(target=self.gui.simulate_auto_detection, daemon=True)
                thread.start()
            
            self.send_response(200)
            self.end_headers()
            
        elif path == '/api/stop':
            if self.gui.is_running:
                self.gui.is_running = False
                self.gui.is_auto_simulation = False
                self.gui.current_gesture = "Parado"
                self.gui.current_command = "Sistema em standby"
                self.gui.add_message("⏹️ Detecção parada")
            
            self.send_response(200)
            self.end_headers()
            
        elif path == '/api/gesture':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            gesture_map = {
                'punch': "✊ Punho",
                'open': "✋ Mão Aberta",
                'point': "👆 Apontando",
                'thumbs': "👍 Joinha",
                'stop': "🤚 Pare"
            }
            
            gesture_key = data.get('gesture')
            if gesture_key in gesture_map:
                gesture = gesture_map[gesture_key]
                command = self.gui.commands[gesture]
                
                self.gui.current_gesture = gesture
                self.gui.current_command = command
                self.gui.add_message(f"Manual: {gesture} → {command}")
                
                # Simula ativação por 1 segundo
                if not self.gui.is_auto_simulation:
                    threading.Timer(1.0, lambda: self._reset_manual()).start()
            
            self.send_response(200)
            self.end_headers()
        else:
            self.send_error(404)
    
    def _reset_manual(self):
        """
        Reseta estado manual após gesto
        """
        if not self.gui.is_auto_simulation and self.gui.is_running:
            self.gui.current_gesture = "Manual ativo"
            self.gui.current_command = "Aguardando gesto..."
    
    def log_message(self, format, *args):
        """
        Suprime logs do servidor HTTP
        """
        pass

def create_server(gui_instance, port):
    """
    Cria servidor HTTP com instância da GUI
    """
    handler = lambda *args, **kwargs: NoTouchPadRequestHandler(*args, gui_instance=gui_instance, **kwargs)
    return socketserver.TCPServer(("", port), handler)

def main():
    """
    Função principal
    """
    print("🎮 NoTouchPad Web GUI - Iniciando...")
    
    try:
        gui = NoTouchPadWebGUI()
        gui.add_message("🌐 Servidor web iniciando...")
        
        # Cria servidor
        server = create_server(gui, gui.port)
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()
        
        # URL da aplicação
        url = f"http://localhost:{gui.port}"
        gui.add_message(f"🌐 Servidor rodando em: {url}")
        
        print(f"🌐 NoTouchPad Web GUI disponível em: {url}")
        print("🚀 Abrindo navegador automaticamente...")
        print("💡 Para parar: pressione Ctrl+C")
        
        # Abre navegador automaticamente
        try:
            webbrowser.open(url)
        except:
            print("⚠️  Não foi possível abrir o navegador automaticamente")
            print(f"🔗 Acesse manualmente: {url}")
        
        # Mantém servidor ativo
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Encerrando servidor...")
            server.shutdown()
            gui.add_message("👋 Servidor encerrado")
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()