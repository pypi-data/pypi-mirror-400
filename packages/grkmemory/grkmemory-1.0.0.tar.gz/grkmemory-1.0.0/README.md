# 🧠 GRKMemory - Graph Retrieve Knowledge Memory

> **GRKMemory** = **G**raph **R**etrieve **K**nowledge **Memory**

[![PyPI version](https://badge.fury.io/py/grkmemory.svg)](https://badge.fury.io/py/grkmemory)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**GRKMemory** é um sistema de memória semântica baseado em grafos para agentes de IA, desenvolvido pelo time **MonkAI**. Recuperação inteligente de conhecimento com economia de 95% em tokens.

## 🚀 Instalação

```bash
pip install grkmemory
```

Para token counting:
```bash
pip install grkmemory[embeddings]
```

## 🎯 Quick Start

```python
from grkmemory import GRKMemory

# Inicializar (usa OPENAI_API_KEY do ambiente)
grk = GRKMemory()

# Buscar memórias relevantes
results = grk.search("O que discutimos sobre IA?")

# Chat com contexto de memória automático
response = grk.chat("Me conte sobre nossas discussões anteriores")

# Salvar uma conversa
grk.save_conversation([
    {"role": "user", "content": "Vamos falar sobre Python"},
    {"role": "assistant", "content": "Claro! O que você quer saber?"}
])
```

## ⚙️ Configuração

```python
from grkmemory import GRKMemory, MemoryConfig

config = MemoryConfig(
    model="gpt-4o",
    memory_file="minhas_memorias.json",
    enable_embeddings=True,
    background_memory_method="graph",  # 'graph', 'embedding', 'tags', 'entities'
    background_memory_limit=5,
    background_memory_threshold=0.3
)

grk = GRKMemory(config=config)
```

## 🔐 Autenticação por Token

```python
from grkmemory import GRKMemory, GRKAuth, AuthenticatedGRK

# Criar API key
auth = GRKAuth()
api_key = auth.create_api_key("Minha App", permissions=["read", "write"])

# Usar GRKMemory protegido
grk = GRKMemory()
secure = AuthenticatedGRK(grk, api_key)
secure.chat("Olá!")
```

### CLI para Tokens

```bash
# Criar token
grkmemory-token create --name "Meu App" --expires 30

# Listar tokens
grkmemory-token list

# Revogar token
grkmemory-token revoke tok_abc123
```

## 📊 Métodos de Busca

| Método | Descrição |
|--------|-----------|
| `graph` | Grafo semântico (recomendado) |
| `embedding` | Similaridade vetorial |
| `tags` | Busca por tags |
| `entities` | Busca por entidades |

```python
# Busca por grafo semântico
results = grk.search("IA", method="graph")

# Busca por embedding
results = grk.search("machine learning", method="embedding")
```

## 📈 Estatísticas

```python
# Estatísticas gerais
stats = grk.get_stats()
print(f"Total de memórias: {stats['total_memories']}")

# Estatísticas do grafo
graph_stats = grk.get_graph_stats()
print(f"Nós: {graph_stats['total_nodes']}")
print(f"Arestas: {graph_stats['total_edges']}")

# Top memórias
top = grk.get_top_memories(limit=5, by="density")
```

## 📁 Estrutura do Projeto

```
GRKMemory/
├── grkmemory/              # 📦 Pacote principal
│   ├── core/               # Classes principais (GRKMemory, Config, Agent)
│   ├── memory/             # Repositório de memória
│   ├── graph/              # Grafo semântico (GRK)
│   ├── auth/               # Autenticação por token
│   └── utils/              # Utilitários (embeddings, text)
├── examples/               # 💡 Exemplos de uso
├── demos/                  # 🎮 Demos legados
├── papers/                 # 📄 Documentação técnica
├── pyproject.toml          # Configuração PyPI
└── README.md
```

## 📚 Exemplos

Veja a pasta `examples/` para exemplos completos:

- `01_basic_usage.py` - Uso básico
- `02_custom_config.py` - Configuração personalizada
- `03_chatbot_with_memory.py` - Chatbot com memória
- `04_graph_analysis.py` - Análise do grafo
- `05_batch_processing.py` - Processamento em lote
- `06_authentication.py` - Autenticação por token

## 🔬 Performance

| Métrica | Context Window | GRKMemory |
|---------|----------------|-----------|
| Tokens/query | ~50.000 | ~2.500 |
| Economia | - | **95%** |
| Precisão | Variável | **95%** |
| Velocidade | Lenta | **10x mais rápido** |

## 📄 Licença

MIT License - veja [LICENSE](LICENSE)

## 👨‍💻 Autor

**Arthur Vaz** - [MonkAI](https://www.monkai.com.br)
