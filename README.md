<p align="center"><img src="https://raw.githubusercontent.com/TilmanGriesel/chipper/refs/heads/main/docs/public/assets/banner.png" width="640" alt="Logo Chipper RAG Util"/></p>
<p align="center">
	<a href="https://chipper.tilmangriesel.com/"><img src="https://img.shields.io/github/actions/workflow/status/TilmanGriesel/chipper/.github%2Fworkflows%2Fdocs-deploy.yml?colorA=1F2229&colorB=ffffff&style=for-the-badge&label=GitHub Pages"></a>
    <a href="https://github.com/TilmanGriesel/chipper/actions"><img src="https://img.shields.io/github/actions/workflow/status/TilmanGriesel/chipper/.github%2Fworkflows%2Fpublish-docker.yml?colorA=1F2229&colorB=ffffff&style=for-the-badge&label=DockerHub"></a>
    <a href="https://github.com/tilmangriesel/chipper/stargazers"><img src="https://img.shields.io/github/stars/tilmangriesel/chipper?colorA=1F2229&colorB=ffffff&style=for-the-badge"></a>
    <a href="https://github.com/tilmangriesel/chipper/issues"><img src="https://img.shields.io/github/issues/tilmangriesel/chipper?colorA=1F2229&colorB=ffffff&style=for-the-badge"></a><a href="https://hub.docker.com/repository/docker/griesel/chipper"><img src="https://img.shields.io/docker/pulls/griesel/chipper?colorA=1F2229&colorB=ffffff&style=for-the-badge"></a>
</p>

**Chipper** provides a web interface, CLI, and a modular, hackable, and lightweight architecture for RAG pipelines, document chunking, web scraping, and query workflows, enhancing generative AI models with advanced information retrieval capabilities. It can also function as a proxy between an **Ollama** client, such as **Enchanted** or **Open WebUI**, and an **Ollama** instance. Built with **Haystack**, **Ollama**, **Hugging Face**, **Docker**, **TailwindCSS**, and **ElasticSearch**, it runs as a fully containerized service.

This project started as a personal tool to help my girlfriend with her book, using local RAG and LLMs to explore characters and creative ideas while keeping her work private and off cloud services like ChatGPT. What began as a few handy scripts soon grew into a fully dockerized, extensible service and along the way, it became a labor of love. Now, I'm excited to share it with the world.

If you find Chipper useful, **leaving a star would be lovely** and will help others discover Chipper too.

**Live Demo:** [https://demo.chipper.tilmangriesel.com/](https://demo.chipper.tilmangriesel.com/)

## Features

- **Local & Cloud Model Support** — Run models locally with [Ollama](https://ollama.com/) or connect to remote models via the [Hugging Face API](https://huggingface.co/).
- **ElasticSearch Integration** — Store and retrieve vectorized data efficiently with scalable indexing.
- **Document Chunking** — Process and split documents into structured segments.
- **Web Scraping** — Extract and index content from web pages.
- **Audio Transcription** — Convert audio files to text.
- **CLI & Web UI** — Access Chipper via a command-line tool or a lightweight, self-contained web interface.
- **Dockerized Deployment** — Run in a fully containerized setup with minimal configuration.
- **Customizable RAG Pipelines** — Adjust model selection, query parameters, and system prompts as needed.
- **Ollama API Proxy** — Extend Ollama with retrieval capabilities, enabling interoperability with clients like **Enchanted** and **Open WebUI**.
- **API Security** — Proxy the Ollama API with API key-based and Baerer token service authentication.
- **Offline Web UI** — Works without an internet connection using vanilla JavaScript and TailwindCSS.
- **Distributed Processing** — Chain multiple Chipper instances together for workload distribution and extended processing.

## Installation and Setup

Visit the [Chipper project website](https://chipper.tilmangriesel.com/) for detailed setup instructions.

**Note:** This is just a research project, so it's not built for production.

## Philosophy

At the heart of this project lies my passion for education and exploration. I believe in creating tools that are both approachable for beginners and helpful for experts. My goal is to offer you a well-thought-out service architecture, and a stepping stone for those eager to learn and innovate.

This project wants to be more than just a technical foundation, for educators, it provides a framework to teach AI concepts in a manageable and practical way. For explorers, tinkerers and companies, it offers a playground where you can experiment, iterate, and build upon a versatile platform.

Feel free to improve, fork, copy, share or expand this project. Contributions are always very welcome!

## Demos

### Web Interface

Use Chipper's built-in web interface to set up and customize RAG pipelines with ease. Built with vanilla JavaScript and TailwindCSS, it works offline and doesn't require any framework-specific knowledge. Run the `/help` command to learn how to switch models, update the embeddings index, and more.

<p align="center"><img src="https://raw.githubusercontent.com/TilmanGriesel/chipper/refs/heads/main/docs/public/assets/demos/demo_rag_chat.gif" alt="chipper_demo_chat"/></p>

### Code Output

Automatic syntax highlighting for popular programming languages in the web interface.

<p align="center"><img src="https://raw.githubusercontent.com/TilmanGriesel/chipper/refs/heads/main/docs/public/assets/demos/demo_rag_chat_code.gif" alt="chipper_demo_code_gen"/></p>

### Reasoning

For models like DeepSeek-R1, Chipper suppresses the "think" output in the UI while preserving the reasoning steps in the console output.

<p align="center"><img src="https://raw.githubusercontent.com/TilmanGriesel/chipper/refs/heads/main/docs/public/assets/demos/demo_rag_chat_ds.gif" alt="chipper_demo_deepseek"/></p>

### CLI Interface

Full support for the Ollama CLI and API, including reflection and proxy capabilities, with API key route decorations.

<p align="center"><img src="https://raw.githubusercontent.com/TilmanGriesel/chipper/refs/heads/main/docs/public/assets/demos/demo_rag_chat_cli.gif" alt="chipper_demo_ollama_cli"/></p>

### Third-Party Clients

Enhance every third-party Ollama client with server-side knowledge base embeddings, allowing server side model selection, query parameters, and system prompt overrides. Enable RAG for any Ollama client or use Chipper as a centralized knowledge base.

<p align="center"><img src="https://raw.githubusercontent.com/TilmanGriesel/chipper/refs/heads/main/docs/public/assets/demos/demo_rag_chat_ollamac.gif" alt="chipper_demo_ollamac"/></p>

## Roadmap

#### Done

- [x] **Basic Functionality**
- [x] **CLI**
- [x] **Web UI**
- [x] **Docker**
- [x] **Enhanced Web UI** (better mobile support)
- [x] **Improved Linting and Formatting**
- [x] **Docker Hub Registry Images**
- [x] **Edge Inference TTS**
- [x] **Mirror Ollama Chat API** to enable Chipper as a drop-in middleware
- [x] **Baerer token support**
- [x] **Haystack Chat Generators** Implement `ChatPromptBuilder` and `OllamaChatGenerator`.
- [x] **Allow For Distributed Processing** — Chain multiple Chipper instances together for workload distribution and extended processing.

#### Todo

- [ ] **Automated Unit Tests**
- [ ] **Smart Document Chunking and Embedding**
- [ ] **React-Based Web Application**

---

## Acknowledgments

- [Haystack](https://haystack.deepset.ai/)
- [Ollama](https://ollama.com/)
- [Hugging Face](https://huggingface.co/)
- [Elastic](https://www.elastic.co)
- [Elasticvue](https://elasticvue.com/)
- [Docker](https://docker.com)
- [VitePress](https://vitepress.dev/)
- [Sherpa ONNX](https://github.com/k2-fsa/sherpa-onnx)
- [Sherpa ONNX Wasm](https://huggingface.co/spaces/k2-fsa/web-assembly-tts-sherpa-onnx-en/tree/main)

## Star History

<a href="https://star-history.com/#TilmanGriesel/chipper&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=TilmanGriesel/chipper&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=TilmanGriesel/chipper&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=TilmanGriesel/chipper&type=Date" />
 </picture>
</a>

---

Be sure to visit the [Chipper project website](https://chipper.tilmangriesel.com/) for detailed setup instructions and more information.
