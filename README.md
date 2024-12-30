<p align="center"><img src="https://raw.githubusercontent.com/TilmanGriesel/chipper/refs/heads/main/docs/public/assets/banner_chipper.png" width="480" alt="Logo Chipper RAG Util"/></p>

**Chipper** gives you a web interface, CLI, and a hackable, simple architecture for embedding pipelines, document chunking, web scraping, and query workflows. Built with **Haystack**, **Ollama**, **Docker**, **Tailwind**, and **ElasticSearch**, it runs locally or scales as a Dockerized service.

This project started as a way to help my girlfriend with her new book. The idea was to use local RAG and LLMs to ask questions about characters and explore creative possibilities, all without sharing proprietary details or your own book with cloud services like ChatGPT. What began as a bunch of scripts is now growing into a fully dockerized service architecture.

**Quick note:** This is just a research project, so it's not built for production.

If you like what you see, leaving a star would be sweet and will help more people discover Chipper!

### Features

- Build a powerful knowledge base using ElasticSearch embeddings.
- Automatically split documents via Haystack.
- Scrape content from web sources.
- Transcribe audio files into text.
- Access via a user-friendly CLI or web client interface.
- Deploy effortlessly using Docker.

## Installation and Setup

**Note:** This part of the documentation is not completed yet. Use the **run.sh** to set up and run Chipper. Invoke without arguments to see the available options.

### Prerequisites

- Ensure you have a running Ollama instance on your local system or a remote inference server.
  - Default `OLLAMA_URL`: `http://host.docker.internal:11434`
- Docker and Docker Compose installed on your system.

### Quick Start

1. **Default Docker Setup:**

   - In the `docker` directory, you will find a default `docker-compose.yml` file.
   - For customization, create a `user.docker-compose.yml` file in the same directory. This custom file will automatically be used by the `run.sh` if it exists.

2. **Environment Configuration:**
   - Each service uses a `.env` file by default.
   - For personalized settings, create a `user_files` folder in the `docker` directory and place your custom configurations there. (Note: The `user_files` directory is in `.gitignore`.)

### Available Services

- **API and WEB:**
  - Located in the `services` directory.
- **Tools:**
  - Found in the `tools` directory, these include helpful utilities like scraper, embedder, cli chat tools.

### CLI Chat

The CLI chat allows terminal-based interaction with Chipper but is less maintained than the web interface. Currently, it does not support chunk streaming.

### Run Chipper Services

- `./run.sh up`

### Import Testdata

- `./run.sh embed-testdata`

### Test Embeddings

1. Visit: http://localhost:5000
1. Ask Chipper: `Tell me a story about Chipper, the brilliant golden retriever.`

## Demo

<p align="center"><img src="https://raw.githubusercontent.com/TilmanGriesel/chipper/refs/heads/main/docs/public/assets/chipper_demo_win_01.gif"alt="Chipper RAG Util Demo Browser"/></p>

<p align="center"><img src="https://raw.githubusercontent.com/TilmanGriesel/chipper/refs/heads/main/docs/public/assets/chipper_demo_mobile_01.gif"alt="Chipper RAG Util Demo Mobile"/></p>

## Philosophy

At the heart of this project lies my passion for education and exploration. I believe in creating tools that are both approachable for beginners and helpful for experts. My goal is to offer you a well-thought-out service architecture, an a stepping stone for those eager to learn and innovate.

This project wants to be more than just a technical foundation, for educators, it provides a framework to teach AI concepts in a manageable and practical way. For explorers, tinkerers and companies, it offers a playground where you can experiment, iterate, and build upon a versatile platform.

Feel free to improve, fork, copy, share or expand this project. Contributions are always very welcome!

### Roadmap

- [x] Basic functionality
- [x] CLI
- [x] Web UI
- [x] Docker
- [x] Improved Web UI with better mobile support
- [ ] Improve linting and formatting
- [ ] React based web app
- [ ] CI test
- [ ] Docker Hub registry images
- [ ] Smart document chunking and embedding

---

## CLI Demo

<p align="center"><img src="https://raw.githubusercontent.com/TilmanGriesel/chipper/refs/heads/main/docs/public/assets/demo_cli_01.gif"alt="Chipper RAG Util Demo CLI"/></p>
