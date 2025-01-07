# Chipper in Action 🎬

Experience Chipper live right here! Please note that the demo's functionality is subject to limitations. It utilizes the **Hugging Face serverless inference API**, which operates under strict quotas and rate limits. Each user is allowed up to **8 prompts per day**. The embedded documents are the chipper test data.

**Maybe you ask Chipper now:**
```plain
Tell me a story about Chipper, the brilliant golden retriever.
```

<div style="border-radius: 24px; overflow: hidden;">
 <iframe
   title="Chipper AI Demo"
   width="100%" 
   height="600"
   style="border: none;"
   src="https://demo.chipper.tilmangriesel.com/">
 </iframe>
</div>

This demo **is limited by the free resources** available from Hugging Face and myself. The quality of the results depends on the specific model and its size, with larger models typically producing more accurate outcomes. Please note that model and index selection options are disabled in this demo.

Additionally, the serverless inference API may sometimes queue your request, leading to delays. During this period, you’ll see the "**Chipper is thinking...**" message. Keep in mind that the performance of Hugging Face inference in this demo may vary and does **not represent the experience of a self-hosted setup**.

### Experimentation 🧪
Since Chipper uses embeddings, you can ask him about his adventures based on the [embedded stories](https://github.com/TilmanGriesel/chipper/tree/main/tools/embed/testdata/md/internal).

### Models Used
- **Inference**: [meta-llama/Meta-Llama-3-8B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct)
- **Embedding**: [sentence-transformers/all-mpnet-base-v2](https://huggingface.co/sentence-transformers/all-mpnet-base-v2)

### Demo Server Specs
The demo operates on a **Scaleway Stardust 1** instance, utilizing the latest Chipper stack along with Elasticsearch from Docker Hub, powered by the **Hugging Face** provider.

| **Specification**   | **Details**            |
|----------------------|------------------------|
| **CPU**             | AMD EPYC 7282 (2.8 GHz) |
| **CPU Architecture** | amd64                 |
| **Sizing**           | 1 vCPU, 1 GiB RAM, 8 GiB Swap |
| **Storage**          | 25 GB                 |

[More about the stardust instance](https://www.scaleway.com/en/docs/compute/instances/reference-content/instances-datasheet/#stardust1-instances)

## Screenshots and GIFs

:::info
Soon, a more in-depth demo of Chipper will be available here. In the meantime, I’ve prepared some preliminary screen recordings for you to check out!
:::

### Web Interface

![chipper_demo](/assets/chipper_demo_01.gif)

### CLI Interface

![chipper_demo](/assets/demo_cli_01.gif)

#### Setup

![chipper_demo](/assets/chipper_setup_demo_01.gif)

::: info
This section is still under construction.
:::
