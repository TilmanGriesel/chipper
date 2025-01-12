<p align="center"><img src="https://raw.githubusercontent.com/TilmanGriesel/chipper/refs/heads/main/docs/public/assets/banner.png" width="640" alt="Logo Chipper RAG Util"/></p>
<p align="center">
	<a href="https://chipper.tilmangriesel.com/"><img src="https://img.shields.io/github/actions/workflow/status/TilmanGriesel/chipper/.github%2Fworkflows%2Fdocs-deploy.yml?colorA=1F2229&colorB=ffffff&style=for-the-badge&label=GitHub Pages"></a>
    <a href="https://github.com/TilmanGriesel/chipper/actions"><img src="https://img.shields.io/github/actions/workflow/status/TilmanGriesel/chipper/.github%2Fworkflows%2Fpublish-docker.yml?colorA=1F2229&colorB=ffffff&style=for-the-badge&label=DockerHub"></a>
    <a href="https://github.com/tilmangriesel/chipper/stargazers"><img src="https://img.shields.io/github/stars/tilmangriesel/chipper?colorA=1F2229&colorB=ffffff&style=for-the-badge"></a>
    <a href="https://github.com/tilmangriesel/chipper/issues"><img src="https://img.shields.io/github/issues/tilmangriesel/chipper?colorA=1F2229&colorB=ffffff&style=for-the-badge"></a><a href="https://hub.docker.com/repository/docker/griesel/chipper"><img src="https://img.shields.io/docker/pulls/griesel/chipper?colorA=1F2229&colorB=ffffff&style=for-the-badge"></a>
</p>

**Chipper** gives you a web interface, CLI, and a hackable, simple architecture for embedding pipelines, document chunking, web scraping, and query workflows. Built with **Haystack**, **Ollama**, **Hugging Face**, **Docker**, **Tailwind**, and **ElasticSearch**, it runs locally or scales as a Dockerized service.

This project started as a way to help my girlfriend with her new book. The idea was to use local RAG and LLMs to ask questions about characters and explore creative possibilities, all without sharing proprietary details or your own book with cloud services like ChatGPT. What began as a bunch of scripts is now growing into a fully dockerized service architecture.

If you **like what you see, leaving a star would be sweet** and will help more people discover Chipper!

Check out the **live demo**: https://demo.chipper.tilmangriesel.com/

## Features

- Local [Ollama](https://ollama.com/) and [hosted Hugging Face API](https://huggingface.co/)
- Build a powerful knowledge base using ElasticSearch embeddings.
- Automatically split documents via Haystack.
- Scrape content from web sources.
- Transcribe audio files into text.
- Access via a user-friendly CLI or web client interface.
- Deploy effortlessly using Docker.

## Installation and Setup

Visit the [Chipper project website](https://chipper.tilmangriesel.com/) for detailed setup instructions.

**Note:** This is just a research project, so it's not built for production.

## Philosophy

At the heart of this project lies my passion for education and exploration. I believe in creating tools that are both approachable for beginners and helpful for experts. My goal is to offer you a well-thought-out service architecture, and a stepping stone for those eager to learn and innovate.

This project wants to be more than just a technical foundation, for educators, it provides a framework to teach AI concepts in a manageable and practical way. For explorers, tinkerers and companies, it offers a playground where you can experiment, iterate, and build upon a versatile platform.

Feel free to improve, fork, copy, share or expand this project. Contributions are always very welcome!

## Demo

<p align="center"><img src="https://raw.githubusercontent.com/TilmanGriesel/chipper/refs/heads/main/docs/public/assets/chipper_demo_01.gif"alt="Chipper RAG Util Demo Browser"/></p>

## Roadmap

- [x] Basic functionality
- [x] CLI
- [x] Web UI
- [x] Docker
- [x] Improved Web UI with better mobile support
- [x] Improve linting and formatting
- [x] Docker Hub registry images
- [x] Edge inference TTS
- [ ] Automated unit-tests
- [ ] React based web app
- [ ] Smart document chunking and embedding

---

## Acknowledgments

My sincere gratitude goes to the remarkable projects that have helped making Chipper a reality.

- **[Haystack](https://haystack.deepset.ai/):**
- **[Ollama](https://ollama.com/):**
- **[Hugging Face](https://huggingface.co/):**
- **[Elastic](https://www.elastic.co)**
- **[Elasticvue](https://elasticvue.com/):**
- **[Docker](https://docker.com):**
- **[VitePress](https://vitepress.dev/):**
- **[Sherpa ONNX](https://github.com/k2-fsa/sherpa-onnx):**
- **[Sherpa ONNX Wasm](https://huggingface.co/spaces/k2-fsa/web-assembly-tts-sherpa-onnx-en/tree/main):**

---

This revision maintains professionalism while expressing gratitude and clearly attributing contributions.

These projects are the backbone of Chipper, and their contributions inspire endless possibilities.

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
