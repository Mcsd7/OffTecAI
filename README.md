# OffTec AI

<p align="center">
  <b>A Local AI Coding Assistant for Android</b><br>
  Powered by Qwen, llama.cpp, Python and Termux.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Android-3DDC84?style=for-the-badge&logo=android&logoColor=white" alt="Android">
  <img src="https://img.shields.io/badge/Runtime-Termux-000000?style=for-the-badge" alt="Termux">
  <img src="https://img.shields.io/badge/AI-Local%20Inference-00C853?style=for-the-badge" alt="Local AI">
  <img src="https://img.shields.io/badge/Language-Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
</p>

OffTec AI is an experimental, local-first AI coding assistant designed to bring AI-assisted programming to Android devices.

It provides a browser-based interface for chatting with a local language model, generating code, managing project files, and running supported Python scripts from a Termux environment.

The goal is simple: **build and experiment with code directly from your phone, without requiring a computer or a cloud AI API for inference.**

> **Project status:** Active development. Features, compatibility, security controls, and performance may change as the project evolves.

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Requirements](#requirements)
- [Installation](#installation)
- [Model Setup](#model-setup)
- [Start OffTec AI](#start-offtec-ai)
- [Using the Interface](#using-the-interface)
- [Project Structure](#project-structure)
- [Security](#security)
- [Limitations](#limitations)
- [Roadmap](#roadmap)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Local AI inference:** Connects to a locally running llama.cpp server.
- **Qwen model support:** Uses a compatible GGUF model configured by the user.
- **Browser-based interface:** Chat with the model through a local web interface.
- **Code generation:** Request supported source files from natural-language prompts.
- **File management:** Work with supported files inside the configured workspace.
- **Python execution:** Run supported Python scripts with output returned to the interface.
- **Android-first workflow:** Designed for Termux on Android devices.
- **No cloud AI API required:** Local inference does not require sending prompts to a third-party AI API.
- **Open-source development:** Intended for experimentation, learning, and community contributions.

Availability and behavior depend on the installed version, local model, device resources, and configuration.

## How It Works

OffTec AI combines a lightweight Python web server with a local language model.

```text
Android Device
     |
     v
Browser Interface
     |
     v
OffTec AI (Python)
     |
     +---- Chat and code-generation requests
     |
     +---- Workspace file operations
     |
     +---- Supported Python execution
     |
     v
llama.cpp HTTP Server
     |
     v
Local GGUF Language Model (Qwen)
```

The browser communicates with the Python application through local HTTP endpoints. The application sends model requests to llama.cpp and handles supported file operations.

Local inference keeps model prompts on the device during normal operation. This does not mean every future integration or network operation is automatically private; review your configuration and code before use.

## Requirements

- Android device capable of running Termux and the selected model.
- [Termux](https://github.com/termux/termux-app)
- Python 3
- CMake and a C/C++ build toolchain for building llama.cpp, if it is not already installed.
- [llama.cpp](https://github.com/ggml-org/llama.cpp)
- A compatible GGUF language model, such as a suitable Qwen model.
- Free storage and RAM appropriate for the selected model.

Performance varies significantly with the device, model size, quantization, context length, and thread settings. Smaller quantized models are generally more practical on mobile hardware.

## Installation

### 1. Install Termux packages

Update the package index and install the basic dependencies:

```bash
pkg update && pkg upgrade
pkg install python git cmake clang make
```

### 2. Clone the repository

Replace `Mcsd7` with the GitHub account that hosts this repository.

```bash
git clone https://github.com/Mcsd7/OffTecAI.git
cd OffTecAI
```

If you already have the project installed locally, enter its directory instead:

```bash
cd ~/OffTecAI
```

### 3. Prepare llama.cpp

If llama.cpp is not installed, clone and build it:

```bash
cd ~
git clone https://github.com/ggml-org/llama.cpp.git
cd ~/llama.cpp
cmake -B build
cmake --build build --target llama-server llama-cli -j 2
```

Building can take time and consume significant memory and storage. Reduce the build parallelism if your device struggles.

If you already have a working llama.cpp installation, you can use it instead of rebuilding.

## Model Setup

OffTec AI needs a compatible GGUF model and a llama.cpp server configuration matching the application.

For example, if your model is stored at:

```text
~/modelos/qwen/qwen.gguf
```

verify that the file exists:

```bash
ls -lh ~/modelos/qwen/qwen.gguf
```

The application's configured model path must point to the actual model file.

**Important:** Model names, file paths, memory requirements, and compatibility vary. Download models only from sources you trust and follow their licenses.

## Start OffTec AI

From the project directory, run:

```bash
cd ~/OffTecAI
python offtec_web.py
```

When the server starts successfully, open this address in your Android browser:

```text
http://127.0.0.1:8765
```

The web interface is intended for local access on the same device.

To stop the server, return to Termux and press `CTRL + C`.

If the application cannot start the model server, verify the configured model path, llama.cpp executable, port settings, and available memory.

## Using the Interface

### Chat with the local model

Enter a question or programming task in the chat interface.

Example:

```text
Explain how a Python function works.
```

### Generate a file

You can request a supported file by name.

Example:

```text
Create ram.py in my home directory to display Android memory information.
```

Review the generated source code before running it.

### Run a Python script

Request execution through the interface and confirm before running the script. Check its output for errors and unexpected behavior.

**Do not execute code you have not reviewed or do not understand.** AI-generated code can contain mistakes or unsafe operations.

## Project Structure

The layout below describes the expected main locations; the exact files may differ between versions.

```text
OffTecAI/
├── offtec_web.py
├── README.md
└── workspace/
    └── Your project files
```

Additional components may be stored separately, including the llama.cpp installation and the local model files.

- `offtec_web.py` — Python web server, application routes, and interface.
- `workspace/` — default workspace for supported project files.
- `~/llama.cpp/` — local inference runtime, when installed at that path.
- `~/modelos/` — example location for local model files.

## Security

OffTec AI is an experimental development tool. Use it responsibly.

- **Local access:** The default web interface is configured for loopback access at `127.0.0.1`.
- **Code review:** AI-generated files must be reviewed before execution.
- **Execution risks:** Running a Python script can modify files, consume resources, or access data available to the Termux process.
- **File boundaries:** Check the application's file validation and path restrictions before using it with important data.
- **Network exposure:** Do not expose the web server to a public network without appropriate authentication, access controls, and security testing.
- **Model privacy:** Local inference can reduce third-party data exposure, but external tools or future integrations may still communicate over a network.
- **Backups:** Keep backups of important projects before testing generated code.

This project is not a sandbox for untrusted code and should not be treated as a hardened production environment.

## Limitations

- Local model output quality depends on the selected model and its quantization.
- Generation speed depends on device hardware, RAM, and context settings.
- Android may terminate long-running processes or restrict background execution.
- Large models may be impractical on devices with limited memory.
- Generated code may be incorrect, incomplete, or insecure.
- Supported file types and operations depend on the installed application version.
- A local model does not automatically have unrestricted access to the operating system; capabilities are determined by the application code.

## Roadmap

Planned development directions may include:

- [ ] Improve code-generation reliability.
- [ ] Add clearer file-operation status and error reporting.
- [ ] Improve workspace navigation and editing.
- [ ] Add configurable model and server settings.
- [ ] Improve execution safeguards and permission boundaries.
- [ ] Expand automated tests and installation documentation.
- [ ] Improve performance on resource-constrained Android devices.
- [ ] Add optional integrations where appropriate.

Roadmap items are goals, not guarantees. Check the repository for the features implemented in the current release.

## Troubleshooting

### The web interface does not open

Make sure the Python server is running and visit:

```text
http://127.0.0.1:8765
```

Check the Termux terminal for startup errors.

### The model does not respond

Verify that the GGUF file exists, the model is compatible with llama.cpp, and the configured server address and port match the application.

### Python reports a syntax error

Run:

```bash
python -m py_compile ~/OffTecAI/offtec_web.py
```

Fix any reported error before restarting the application.

### A generated file is not saved

Check the response displayed in the interface, the selected destination, file permissions, and whether a file with the same name already exists.

### The device runs out of memory

Try a smaller quantized model, reduce the context length, and avoid running multiple memory-intensive processes simultaneously.

## Contributing

Contributions, bug reports, and suggestions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make a focused change.
4. Test the change on your setup.
5. Submit a pull request describing the change and how it was tested.

Please do not include API keys, personal files, private model downloads, or other secrets in commits.

## License

No license is specified by this README. Before publishing the project as open source, choose a license and add the appropriate `LICENSE` file. Also verify the licenses of any bundled dependencies and model files.

---

<p align="center">
  <b>OffTec AI</b><br>
  Built for local AI experimentation on Android.<br>
  <i>Offensive Technology</i>
</p>
