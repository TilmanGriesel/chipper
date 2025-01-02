Source: https://en.wikipedia.org/wiki/Llama_(language_model)

# Llama (language model)

Llama (Large Language Model Meta AI, formerly stylized as LLaMA) is a family of autoregressive large language models (
LLMs) released by Meta AI starting in February 2023. The latest version is Llama 3.3, released in December 2024.
Llama models are trained at different parameter sizes, ranging between 1B and 405B. Originally, Llama was only available
as a foundation model. Starting with Llama 2, Meta AI started releasing instruction fine-tuned versions alongside
foundation models.
Model weights for the first version of Llama were made available to the research community under a non-commercial
license, and access was granted on a case-by-case basis. Unauthorized copies of the first model were shared via
BitTorrent. Subsequent versions of Llama were made accessible outside academia and released under licenses that
permitted some commercial use.
Alongside the release of Llama 3, Meta added virtual assistant features to Facebook and WhatsApp in select regions, and
a standalone website. Both services use a Llama 3 model.

## Background

After the release of large language models such as GPT-3, a focus of research was up-scaling models which in some
instances showed major increases in emergent capabilities. The release of ChatGPT and its surprise success caused an
increase in attention to large language models.
Compared with other responses to ChatGPT, Meta's Chief AI scientist Yann LeCun stated that large language models are
best for aiding with writing.
An empirical investigation of the Llama series was the scaling laws. It was observed that the Llama 3 models showed that
when a model is trained on data that is more than the "Chinchilla-optimal" amount, the performance continues to scale
log-linearly. For example, the Chinchilla-optimal dataset for Llama 3 8B is 200 billion tokens, but performance
continued to scale log-linearly to the 75-times larger dataset of 15 trillion tokens.

## Initial release

LLaMA was announced on February 24, 2023, via a blog post and a paper describing the model's training, architecture, and
performance. The inference code used to run the model was publicly released under the open-source GPLv3 license. Access
to the model's weights was managed by an application process, with access to be granted "on a case-by-case basis to
academic researchers; those affiliated with organizations in government, civil society, and academia; and industry
research laboratories around the world".
Llama was trained on only publicly available information, and was trained at various model sizes, with the intention to
make it more accessible to different hardware. The model was exclusively a foundation model, although the paper
contained examples of instruction fine-tuned versions of the model.
Meta AI reported the 13B parameter model performance on most NLP benchmarks exceeded that of the much larger GPT-3 (with
175B parameters), and the largest 65B model was competitive with state of the art models such as PaLM and Chinchilla.

### Leak

On March 3, 2023, a torrent containing LLaMA's weights was uploaded, with a link to the torrent shared on the 4chan
imageboard and subsequently spread through online AI communities. That same day, a pull request on the main LLaMA
repository was opened, requesting to add the magnet link to the official documentation. On March 4, a pull request was
opened to add links to HuggingFace repositories containing the model. On March 6, Meta filed takedown requests to remove
the HuggingFace repositories linked in the pull request, characterizing it as "unauthorized distribution" of the model.
HuggingFace complied with the requests. On March 20, Meta filed a DMCA takedown request for copyright infringement
against a repository containing a script that downloaded LLaMA from a mirror, and GitHub complied the next day.
Reactions to the leak varied. Some speculated that the model would be used for malicious purposes, such as more
sophisticated spam. Some have celebrated the model's accessibility, as well as the fact that smaller versions of the
model can be run relatively cheaply, suggesting that this will promote the flourishing of additional research
developments. Multiple commentators, such as Simon Willison, compared LLaMA to Stable Diffusion, a text-to-image model
which, unlike comparably sophisticated models which preceded it, was openly distributed, leading to a rapid
proliferation of associated tools, techniques, and software.

## Llama 2

On July 18, 2023, in partnership with Microsoft, Meta announced Llama 2, the next generation of Llama. Meta trained and
released Llama 2 in three model sizes: 7, 13, and 70 billion parameters. The model architecture remains largely
unchanged from that of LLaMA-1 models, but 40% more data was used to train the foundational models. The accompanying
preprint also mentions a model with 34B parameters that might be released in the future upon satisfying safety targets.
Llama 2 includes foundation models and models fine-tuned for chat. In a further departure from the original version of
Llama, all models are released with weights and may be used for many commercial use cases. However, because Llama's
license enforces an acceptable use policy that prohibits Llama from being used for some purposes, Meta's use of the term
open source to describe Llama has been disputed by the Open Source Initiative (which maintains The Open Source
Definition) and others.
Code Llama is a fine-tune of Llama 2 with code specific datasets. 7B, 13B, and 34B versions were released on August 24,
2023, with the 70B releasing on the January 29, 2024. Starting with the foundation models from Llama 2, Meta AI would
train an additional 500B tokens of code datasets, before an additional 20B token of long-context data, creating the Code
Llama foundation models. This foundation model was further trained on 5B instruction following token to create the
instruct fine-tune. Another foundation model was created for Python code, which trained on 100B tokens of Python-only
code, before the long-context data.

## Llama 3

On April 18, 2024, Meta released Llama-3 with two sizes: 8B and 70B parameters. The models have been pre-trained on
approximately 15 trillion tokens of text gathered from “publicly available sources” with the instruct models fine-tuned
on “publicly available instruction datasets, as well as over 10M human-annotated examples". Meta AI's testing showed in
April 2024 that Llama 3 70B was beating Gemini Pro 1.5 and Claude 3 Sonnet on most benchmarks. Meta also announced plans
to make Llama 3 multilingual and multimodal, better at coding and reasoning, and to increase its context window.
During an interview with Dwarkesh Patel, Mark Zuckerberg said that the 8B version of Llama 3 was nearly as powerful as
the largest Llama 2. Compared to previous models, Zuckerberg stated the team was surprised that the 70B model was still
learning even at the end of the 15T tokens training. The decision was made to end training to focus GPU power elsewhere.
Llama-3.1 was released on July 23, 2024, with three sizes: 8B, 70B, and 405B parameters.

## Comparison of models

For the training cost column, only the largest model's cost is written. So for example, "21,000" is the training cost of
Llama 2 69B in units of petaFLOP-day. Also, 1 petaFLOP-day = 1 petaFLOP/sec × 1 day = 8.64E19 FLOP. "T" means "trillion"
and "B" means "billion".

## Architecture and training

### Architecture

Like GPT-3, the Llama series of models are decoder-only Transformers, but there are some minor differences:

SwiGLU activation function instead of GeLU;
rotary positional embeddings (RoPE) instead of absolute positional embedding;
RMSNorm instead of layer normalization;

### Training datasets

LLaMA's developers focused their effort on scaling the model's performance by increasing the volume of training data,
rather than the number of parameters, reasoning that the dominating cost for LLMs is from doing inference on the trained
model rather than the computational cost of the training process.
LLaMA 1 foundational models were trained on a data set with 1.4 trillion tokens, drawn from publicly available data
sources, including:

Webpages scraped by CommonCrawl
Open source repositories of source code from GitHub
Wikipedia in 20 languages
Public domain books from Project Gutenberg
Books3 books dataset
The LaTeX source code for scientific papers uploaded to ArXiv
Questions and answers from Stack Exchange websites
On April 17, 2023, TogetherAI launched a project named RedPajama to reproduce and distribute an open source version of
the LLaMA dataset. The dataset has approximately 1.2 trillion tokens and is publicly available for download.
Llama 2 foundational models were trained on a data set with 2 trillion tokens. This data set was curated to remove Web
sites that often disclose personal data of people. It also upsamples sources considered trustworthy. Llama 2 - Chat was
additionally fine-tuned on 27,540 prompt-response pairs created for this project, which performed better than larger but
lower-quality third-party datasets. For AI alignment, reinforcement learning with human feedback (RLHF) was used with a
combination of 1,418,091 Meta examples and seven smaller datasets. The average dialog depth was 3.9 in the Meta
examples, 3.0 for Anthropic Helpful and Anthropic Harmless sets, and 1.0 for five other sets, including OpenAI
Summarize, StackExchange, etc.
Llama 3 consists of mainly English data, with over 5% in over 30 other languages. Its dataset was filtered by a
text-quality classifier, and the classifier was trained by text synthesized by Llama 2.

### Fine-tuning

Llama 1 models are only available as foundational models with self-supervised learning and without fine-tuning. Llama
2 – Chat models were derived from foundational Llama 2 models. Unlike GPT-4 which increased context length during
fine-tuning, Llama 2 and Code Llama - Chat have the same context length of 4K tokens. Supervised fine-tuning used an
autoregressive loss function with token loss on user prompts zeroed out. The batch size was 64.
For AI alignment, human annotators wrote prompts and then compared two model outputs (a binary protocol), giving
confidence levels and separate safety labels with veto power. Two separate reward models were trained from these
preferences for safety and helpfulness using Reinforcement learning from human feedback (RLHF). A major technical
contribution is the departure from the exclusive use of Proximal Policy Optimization (PPO) for RLHF – a new technique
based on Rejection sampling was used, followed by PPO.
Multi-turn consistency in dialogs was targeted for improvement, to make sure that "system messages" (initial
instructions, such as "speak in French" and "act like Napoleon") are respected during the dialog. This was accomplished
using the new "Ghost attention" technique during training, which concatenates relevant instructions to each new user
message but zeros out the loss function for tokens in the prompt (earlier parts of the dialog).

## Applications

The Stanford University Institute for Human-Centered Artificial Intelligence (HAI) Center for Research on Foundation
Models (CRFM) released Alpaca, a training recipe based on the LLaMA 7B model that uses the "Self-Instruct" method of
instruction tuning to acquire capabilities comparable to the OpenAI GPT-3 series text-davinci-003 model at a modest
cost. The model files were officially removed on March 21, 2023, over hosting costs and safety concerns, though the code
and paper remain online for reference.
Meditron is a family of Llama-based finetuned on a corpus of clinical guidelines, PubMed papers, and articles. It was
created by researchers at École Polytechnique Fédérale de Lausanne School of Computer and Communication Sciences, and
the Yale School of Medicine. It shows increased performance on medical-related benchmarks such as MedQA and MedMCQA.
Zoom used Meta Llama 2 to create an AI Companion that can summarize meetings, provide helpful presentation tips, and
assist with message responses. This AI Companion is powered by multiple models, including Meta Llama 2.
Reuters reported in 2024 that many Chinese foundation models relied on Llama models for their training.

### llama.cpp

Software developer Georgi Gerganov released llama.cpp as open-source on March 10, 2023. It's a re-implementation of
LLaMA in C++, allowing systems without a powerful GPU to run the model locally. The llama.cpp project introduced the
GGUF file format, a binary format that stores both tensors and metadata. The format focuses on supporting different
quantization types, which can reduce memory usage, and increase speed at the expense of lower model precision.
llamafile created by Justine Tunney is an open-source tool that bundles llama.cpp with the model into a single
executable file. Tunney et al. introduced new optimized matrix multiplication kernels for x86 and ARM CPUs, improving
prompt evaluation performance for FP16 and 8-bit quantized data types.

### Military

In 2024, researchers from the People's Liberation Army Academy of Military Sciences (top military academy of China) were
reported to have developed a military tool using Llama, which Meta Platforms stated was unauthorized due to Llama's
license prohibiting the use of the model for military purposes. Meta granted the US government and US military
contractors permission to use Llama in November 2024, but continued to prohibit military use by non-US entities.

## Reception

Wired describes the 8B parameter version of Llama 3 as being "surprisingly capable" given its size.
The response to Meta's integration of Llama into Facebook was mixed, with some users confused after Meta AI told a
parental group that it had a child.
According to the Q4 2023 Earnings transcript, Meta adopted the strategy of open weights to improve on model safety,
iteration speed, increase adoption among developers and researchers, and to become the industry standard. Llama 5, 6,
and 7 are planned for the future.
The release of Llama models has sparked significant debates on the benefits and misuse risks of open weight models. Such
models can be fine-tuned to remove safeguards, notably by cyber criminals, until they comply with harmful requests. Some
experts contend that future models may facilitate causing damage more than defending against it, for example by making
it relatively easy to engineer advanced bioweapons without specialized knowledge. Conversely, open-weight models can be
useful for a wide variety of purposes, including for safety research.
Open Source Initiative head Stefano Maffulli criticized Meta for describing Llama as open source, saying that it was
causing confusion among users and "polluting" the term.

## See also

GPT-4o
IBM Granite, an open-source LLM made by IBM
Mistral AI, a French open-source AI company

## References

## Further reading

## External links
