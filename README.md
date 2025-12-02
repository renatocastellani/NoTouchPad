# 🎮 NoTouchPad

**Gamepad controlado por webcam que transforma seus movimentos em comandos de controle para seus games favoritos!**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green.svg)](https://opencv.org)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-orange.svg)](https://mediapipe.dev)
[![License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)

## 🚀 Características

- 🎥 **Detecção em tempo real** usando webcam comum
- 👋 **Reconhecimento de gestos** das mãos via MediaPipe
- 🎮 **Simulação de gamepad** Xbox/PlayStation compatível  
- 🪟 **Interface desktop nativa** (PySide6) com fallback web
- ⚙️ **Configuração personalizada** de mapeamento de gestos
- 📦 **Executável standalone** - zero dependências para usuário
- 🌍 **Multiplataforma** - Windows, Linux e macOS

## ⚡ Instalação Rápida

### Opção 1: Executável (Recomendado)
```bash
# 1. Baixe o executável para seu sistema operacional:
# Windows: NoTouchPad-windows.exe
# Linux: NoTouchPad-linux
# Mac: NoTouchPad-macos

# 2. Execute diretamente - sem instalação!
./NoTouchPad
```

### Opção 2: Código Fonte
```bash
# Clone o repositório
git clone https://github.com/renatocastellani/NoTouchPad.git
cd NoTouchPad

# Execute o instalador
# Linux/Mac:
bash scripts/install.sh

# Windows:
scripts\install.bat

# Execute a aplicação
python src/main.py
```

## 🎯 Como Usar

1. **Conecte sua webcam** e execute o NoTouchPad
2. **Posicione-se** na frente da câmera (1-2 metros de distância)
3. **Configure os gestos** na interface gráfica
4. **Abra seu game** favorito e comece a jogar com as mãos! 🙌

### Gestos Padrão

| Gesto | Comando | Descrição |
|-------|---------|-----------|
| ✊ **Punho fechado** | Botão A | Ação principal |
| ✋ **Mão aberta** | Botão B | Ação secundária |
| 👆 **Dedo indicador** | Analógico | Movimento direcional |
| 👍 **Joinha** | Start | Menu do jogo |

## 🔧 Desenvolvimento

### Estrutura do Projeto
```
NoTouchPad/
├── src/                    # Código fonte
│   ├── camera_detector.py  # Captura de vídeo
│   ├── gesture_recognizer.py # Detecção de gestos  
│   ├── gamepad_controller.py # Simulação de controle
│   └── ui/                 # Interface gráfica
├── docs/                   # Documentação
├── scripts/                # Scripts de instalação
└── requirements.txt        # Dependências
```

### Para Desenvolvedores
```bash
# Instalar dependências de desenvolvimento (recomendado em venv)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

# Executar testes
pytest tests/

# Gerar executável
python build.py

# Formatar código
black src/
```

## 📋 Roadmap

- ✅ **v1.0**: Detecção básica de gestos + interface
- 🔄 **v1.1**: Gestos avançados + configuração visual  
- 📅 **v1.2**: Suporte a múltiplas mãos
- 📅 **v2.0**: Machine Learning personalizado

Veja o [roadmap completo](docs/ROADMAP.md) para mais detalhes.

## 🤝 Contribuindo

Contribuições são muito bem-vindas! 

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📞 Suporte

- 🐛 **Bug reports**: [Issues](https://github.com/renatocastellani/NoTouchPad/issues)
- 💡 **Feature requests**: [Discussions](https://github.com/renatocastellani/NoTouchPad/discussions)
- 📧 **Email**: [seu-email@exemplo.com](mailto:seu-email@exemplo.com)

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## 🙏 Agradecimentos

- [MediaPipe](https://mediapipe.dev) pela detecção de mãos
- [OpenCV](https://opencv.org) pelo processamento de vídeo
- [pygame](https://pygame.org) pela simulação de gamepad
- Comunidade open source! 💙

---

**⭐ Se este projeto te ajudou, dê uma estrela no GitHub! ⭐**
