# 📁 Estrutura do Projeto NoTouchPad

## 🎯 Visão Geral
Este documento explica a estrutura organizacional do projeto NoTouchPad, um gamepad controlado por webcam que transforma movimentos das mãos em comandos de controle para games.

## 📂 Estrutura Completa

```
NoTouchPad/
├── 📁 src/                          # Código fonte principal
│   ├── __init__.py                  # Módulo principal
│   ├── main.py                      # Ponto de entrada da aplicação
│   ├── camera_detector.py           # Detecção e captura de vídeo
│   ├── gesture_recognizer.py        # Reconhecimento de gestos
│   ├── gamepad_controller.py        # Simulação de gamepad
│   ├── config.py                    # Configurações da aplicação
│   └── 📁 ui/                       # Interface gráfica
│       ├── __init__.py              # Módulo UI
│       └── main_window.py           # Janela principal
├── 📁 assets/                       # Recursos (ícones, imagens)
│   └── README.md                    # Documentação de assets
├── 📁 tests/                        # Testes unitários
│   └── README.md                    # Documentação de testes
├── 📁 docs/                         # Documentação
│   └── ESTRUTURA_PROJETO.md         # Este arquivo
├── 📁 scripts/                      # Scripts de instalação
│   ├── install.sh                   # Instalador Linux/Mac
│   └── install.bat                  # Instalador Windows
├── requirements.txt                 # Dependências principais
├── requirements-dev.txt             # Dependências de desenvolvimento
├── setup.py                         # Configuração de instalação
├── build.py                         # Script de build PyInstaller
├── .gitignore                       # Arquivos ignorados pelo Git
└── README.md                        # Documentação principal
```

## 🏗️ Arquitetura dos Módulos

### 📱 Core Modules (src/)

#### 🎥 `camera_detector.py`
**Responsabilidade**: Captura e processamento de vídeo da webcam
- **Funcionalidades**:
  - Inicialização da câmera
  - Captura de frames em tempo real
  - Controle de resolução e FPS
  - Liberação de recursos
- **Dependências**: OpenCV
- **Classes**: `CameraDetector`

#### 👋 `gesture_recognizer.py`
**Responsabilidade**: Reconhecimento de gestos das mãos
- **Funcionalidades**:
  - Detecção de mãos usando MediaPipe
  - Classificação de gestos (punho, mão aberta, apontar, etc.)
  - Tracking de posição das mãos
  - Cálculo de movimento e velocidade
- **Dependências**: MediaPipe, NumPy
- **Classes**: `GestureRecognizer`, `HandPosition`
- **Enums**: `GestureType`

#### 🎮 `gamepad_controller.py`
**Responsabilidade**: Simulação de comandos de gamepad
- **Funcionalidades**:
  - Mapeamento de gestos para botões
  - Simulação de botões e analógicos
  - Suporte a múltiplos tipos de controle
  - Configuração de sensibilidade
- **Dependências**: pygame, pynput
- **Classes**: `GamepadController`
- **Enums**: `GamepadButton`

#### ⚙️ `config.py`
**Responsabilidade**: Gerenciamento de configurações
- **Funcionalidades**:
  - Carregamento/salvamento de configurações
  - Configurações padrão
  - Validação de parâmetros
  - API de acesso a configurações
- **Classes**: `Config`

#### 🖥️ `main.py`
**Responsabilidade**: Ponto de entrada e orquestração
- **Funcionalidades**:
  - Inicialização da aplicação
  - Loop principal
  - Coordenação entre módulos
  - Tratamento de erros globais

### 🎨 Interface (src/ui/)

#### 🪟 `main_window.py`
**Responsabilidade**: Interface gráfica principal
- **Funcionalidades**:
  - Janela principal da aplicação
  - Preview da câmera
  - Feedback visual de gestos
  - Controles de configuração
- **Dependências**: tkinter
- **Classes**: `MainWindow`

## 🔧 Scripts e Configuração

### 📦 Dependências
- **`requirements.txt`**: Bibliotecas essenciais para execução
- **`requirements-dev.txt`**: Ferramentas de desenvolvimento e build

### 🛠️ Build e Distribuição
- **`setup.py`**: Configuração para instalação via pip
- **`build.py`**: Script para gerar executáveis com PyInstaller

### 💿 Instalação
- **`scripts/install.sh`**: Instalador automático Linux/Mac
- **`scripts/install.bat`**: Instalador automático Windows

## 🔄 Fluxo de Dados

```
Webcam → CameraDetector → GestureRecognizer → GamepadController → Game
   ↓                                                                ↑
MainWindow ← ← ← ← ← ← ← Config ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ←
```

1. **Captura**: `CameraDetector` obtém frames da webcam
2. **Detecção**: `GestureRecognizer` identifica mãos e gestos
3. **Mapeamento**: `GamepadController` converte gestos em comandos
4. **Execução**: Comandos são enviados para o sistema/game
5. **Feedback**: `MainWindow` mostra status visual
6. **Configuração**: `Config` persiste preferências do usuário

## 🎛️ Configurações Disponíveis

### 📹 Câmera
- Índice da câmera (0, 1, 2...)
- Resolução (width, height)
- FPS (frames por segundo)

### 🤖 Detecção
- Threshold de confiança
- Número máximo de mãos
- Sensibilidade de tracking

### 🎮 Gamepad
- Sensibilidade dos analógicos
- Dead zone
- Mapeamento personalizado de gestos

### 🖥️ Interface
- Tamanho da janela
- Exibir FPS
- Mostrar landmarks das mãos

## 🧪 Testes

A pasta `tests/` conterá:
- Testes unitários para cada módulo
- Testes de integração
- Mocks para câmera e gamepad
- Benchmarks de performance

## 📊 Assets

A pasta `assets/` conterá:
- Ícones da aplicação (.ico, .png)
- Imagens da interface
- Modelos de ML customizados (futuro)
- Arquivos de configuração padrão

## 🚀 Próximos Passos

1. **Implementar módulos core** (camera, gesture, gamepad)
2. **Criar interface básica** (preview + controles)
3. **Adicionar sistema de configuração**
4. **Implementar build automático**
5. **Criar testes e documentação**
6. **Distribuir primeira versão**

---

## 💡 Principios de Design

- **Modularidade**: Cada componente tem responsabilidade específica
- **Configurabilidade**: Usuário pode ajustar comportamento
- **Portabilidade**: Funciona em Windows, Linux e Mac
- **Simplicidade**: Interface intuitiva e fácil de usar
- **Performance**: Otimizado para tempo real
- **Extensibilidade**: Fácil adicionar novos gestos e comandos