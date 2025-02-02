---
outline: deep
---

# Chipper in Action 🎬

Experience Chipper live right here! Please note that the demo's functionality is subject to limitations. It utilizes the **Hugging Face serverless inference API**, which operates under strict quotas and rate limits. Each user is allowed up to **8 prompts per day**. The embedded documents are the chipper test data.

## Live Demo

**Maybe you ask Chipper now:**

```plain
Tell me a story about Chipper, the brilliant golden retriever.
```

<div class="demo">
 <iframe
   title="Chipper AI Demo"
   width="100%"
   height="900"
   src="https://demo.chipper.tilmangriesel.com/">
 </iframe>
</div>

or visit the demo at: https://demo.chipper.tilmangriesel.com/

This demo **is limited by the free resources** available from Hugging Face and myself. The quality of the results depends on the specific model and its size, with larger models typically producing more accurate outcomes. Please note that model and index selection options are disabled in this demo.

Additionally, the serverless inference API may sometimes queue your request, leading to delays. During this period, you’ll see the "**Chipper is thinking...**" message. Keep in mind that the performance of Hugging Face inference in this demo may vary and does **not represent the experience of a self-hosted setup**.

## Demos

### Web Interface

Leverage the built-in Chipper web interface for an easy entry into customizable RAG pipelines and tailored output. Written in vanilla JavaScript, it requires no specific framework experience. The interface is built with TailwindCSS and includes all resources offline. Use the `/help` command learn how to switch models, update the embeddings index and more.

![chipper_demo_chat](/assets/demos/demo_rag_chat.gif)

### Code Output

Automatic syntax highlighting for popular programming languages in the web interface.

![chipper_demo_code_gen](/assets/demos/demo_rag_chat_code.gif)

### Reasoning

For models like DeepSeek-R1, Chipper suppresses the "think" output in the UI while preserving the reasoning steps in the console output.

![chipper_demo_deepseek](/assets/demos/demo_rag_chat_ds.gif)

### CLI Interface

Full support for the Ollama CLI and API, including reflection and proxy capabilities, with API key route decorations.

![chipper_demo_ollama_cli](/assets/demos/demo_rag_chat_cli.gif)

### Third-Party Client

Enhance every third-party Ollama client with server-side knowledge base embeddings, allowing server side model selection, query parameters, and system prompt overrides. Enable RAG for any Ollama client or use Chipper as a centralized knowledge base.

![chipper_demo_ollamac](/assets/demos/demo_rag_chat_ollamac.gif)

### Experimentation 🧪

Since Chipper uses embeddings, you can ask him about his adventures based on the [embedded stories](https://github.com/TilmanGriesel/chipper/tree/main/tools/embed/testdata/md/internal).

### Live-Demo Setup

- **Inference**: [meta-llama/Meta-Llama-3-8B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct)
- **Embedding**: [sentence-transformers/all-mpnet-base-v2](https://huggingface.co/sentence-transformers/all-mpnet-base-v2)

#### Server Specs

The demo operates on a **Scaleway Stardust 1** instance, utilizing the latest Chipper stack along with Elasticsearch from Docker Hub, powered by the **Hugging Face** provider.

| **Specification**    | **Details**                   |
| -------------------- | ----------------------------- |
| **CPU**              | AMD EPYC 7282 (2.8 GHz)       |
| **CPU Architecture** | amd64                         |
| **Sizing**           | 1 vCPU, 1 GiB RAM, 8 GiB Swap |
| **Storage**          | 25 GB                         |

[More about the stardust instance](https://www.scaleway.com/en/docs/compute/instances/reference-content/instances-datasheet/#stardust1-instances)

---

::: info
This section is still under construction.
:::
