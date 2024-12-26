Source: https://en.wikipedia.org/wiki/Retrieval-augmented_generation

# Retrieval-augmented generation

Retrieval Augmented Generation (RAG) is a technique that grants generative artificial intelligence models information retrieval capabilities. It modifies interactions with a large language model (LLM) so that the model responds to user queries with reference to a specified set of documents, using this information to augment information drawn from its own vast, static training data. This allows LLMs to use domain-specific and/or updated information.  
Use cases include providing chatbot access to internal company data or giving factual information only from an authoritative source.

## Process

The RAG process is made up of four key stages. First, all the data must be prepared and indexed for use by the LLM. Thereafter, each query consists of a retrieval, augmentation, and generation phase.

### Indexing

Typically, the data to be referenced is converted into LLM embeddings, numerical representations in the form of large vectors. RAG can be used on unstructured (usually text), semi-structured, or structured data (for example knowledge graphs). These embeddings are then stored in a vector database to allow for document retrieval.

### Retrieval

Given a user query, a document retriever is first called to select the most relevant documents that will be used to augment the query. This comparison can be done using a variety of methods, which depend in part on the type of indexing used.

### Augmentation

The model feeds this relevant retrieved information into the LLM via prompt engineering of the user's original query. Newer implementations (as of 2023) can also incorporate specific augmentation modules with abilities such as expanding queries into multiple domains and using memory and self-improvement to learn from previous retrievals.

### Generation

Finally, the LLM can generate output based on both the query and the retrieved documents. Some models incorporate extra steps to improve output, such as the re-ranking of retrieved information, context selection, and fine-tuning.

## Improvements

Improvements to the basic process above can be applied at different stages in the RAG flow.

### Encoder

These methods center around the encoding of text as either dense or sparse vectors. Sparse vectors, used to encode the identity of a word, are typically dictionary length and contain almost all zeros. Dense vectors, used to encode meaning, are much smaller and contain far fewer zeros. Several enhancements can be made to the way similarities are calculated in the vector stores (databases).

Performance can be improved with faster dot products, approximate nearest neighors, or centroid searches.
Accuracy can be improved with Late Interactions.
Hybrid vectors: dense vector representations can be combined with sparse one-hot vectors in order to use the faster sparse dot products rather than the slower dense ones. Other methods can combine sparse methods (BM25, SPLADE) with dense ones like DRAGON.

### Retriever-centric methods

These methods focus on improving the quality of hits from the vector database:

pre-train the retriever using the Inverse Cloze Task.
progressive data augmentation. The method of Dragon samples difficult negatives to train a dense vector retriever.
Under supervision, train the retriever for a given generator. Given a prompt and the desired answer, retrieve the top-k vectors, and feed those vectors into the generator to achieve a perplexity score for the correct answer. Then minimize the KL-divergence between the observed retrieved vectors probability and LM likelihoods to adjust the retriever.
use reranking to train the retriever.

### Language model

By redesigning the language model with the retriever in mind, a 25-time smaller network can get comparable perplexity as its much larger counterparts. Because it is trained from scratch, this method (Retro) incurs the high cost of training runs that the original RAG scheme avoided. The hypothesis is that by giving domain knowledge during training, Retro needs less focus on the domain and can devote its smaller weight resources only to language semantics. The redesigned language model is shown here.  
It has been reported that Retro is not reproducible, so modifications were made to make it so. The more reproducible version is called Retro++ and includes in-context RAG.

### Chunking

Chunking involves various strategies for breaking up the data into vectors so the retriever can find details in it.

Three types of chunking strategies are:

Fixed length with overlap. This is fast and easy. Overlapping consecutive chunks helps to maintain semantic context across chunks.
Syntax-based chunks can break the document up into sentences. Libraries such as spaCy or NLTK can also help.
File format-based chunking. Certain file types have natural chunks built in, and it's best to respect them. For example, code files are best chunked and vectorized as whole functions or classes. HTML files should leave <table> or base64 encoded <img> elements intact. Similar considerations should be taken for pdf files. Libraries such as Unstructured or Langchain can assist with this method.

## Challenges
