[README.md](https://github.com/user-attachments/files/27622251/README.md)
# 🚀 MLOps Platform

> Production-grade MLOps infrastructure for deploying, serving, and monitoring large language models at scale.

![Platform Status](https://img.shields.io/badge/status-production-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Docker](https://img.shields.io/badge/docker-ready-2496ED?logo=docker)
![GPU](https://img.shields.io/badge/GPU-NVIDIA%20H200-76B900?logo=nvidia)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                      (OpenWebUI / API)                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   API Gateway & Routing                      │
│              (Central Services API / magi-core)              │
└──────┬─────────────────┬──────────────────┬─────────────────┘
       │                 │                  │
┌──────▼──────┐  ┌───────▼───────┐  ┌──────▼──────┐
│  LLM Serving│  │  Embedding /  │  │  Document   │
│   (vLLM)    │  │  Vector Store │  │  Processing │
│             │  │(Vespa / Chroma│  │  (MinerU)   │
└──────┬──────┘  └───────┬───────┘  └─────────────┘
       │                 │
┌──────▼─────────────────▼──────────────────────────────────┐
│                   Monitoring & Observability               │
│         Prometheus + Grafana + DCGM GPU Exporter          │
└───────────────────────────────────────────────────────────┘
```

---

## ✨ Features

- **Multi-model LLM Serving** — Concurrent deployment of multiple LLMs via vLLM with persistent loading (no cold starts)
- **RAG Pipeline** — Full Retrieval-Augmented Generation stack: PDF ingestion → embedding → vector search → generation
- **GPU Monitoring** — Real-time H200 GPU metrics (utilization, VRAM, temperature, power) via DCGM Exporter
- **Observability** — Grafana dashboards with Prometheus metrics for all services (conversations, users, token usage)
- **Air-gapped Ready** — Fully operational in isolated network environments using private Docker registry
- **Multi-service Architecture** — Independent microservices for STT, OCR, diarization, embeddings, and chat

---

## 🧱 Stack

| Layer | Technology |
|-------|-----------|
| LLM Serving | [vLLM](https://github.com/vllm-project/vllm) |
| Models | Qwen3, Gemma4, Qwen3-VL, Qwen3-Coder |
| Embeddings | HuggingFace TEI (Text Embeddings Inference) |
| Vector DB | Vespa, ChromaDB |
| Document Parsing | MinerU (PDF → structured text) |
| OCR | Custom OCR service |
| Speech-to-Text | Speaches / Whisper-based STT |
| Speaker Diarization | Pyannote-based diarization service |
| Frontend | OpenWebUI |
| Monitoring | Prometheus + Grafana + DCGM GPU Exporter |
| Containerization | Docker + Docker Compose |
| GPU | NVIDIA H200 (143GB VRAM) × 8 |

---

## 📁 Repository Structure

```
mlops-platform/
├── infrastructure/
│   ├── docker/               # Docker Compose configs per service
│   ├── monitoring/           # Prometheus configs, Grafana dashboards (JSON)
│   │   ├── dashboards/
│   │   │   ├── llm-usage.json
│   │   │   └── gpu-metrics.json
│   │   └── prometheus.yml
│   ├── vector-db/            # Vespa schemas & Chroma configs
│   └── nginx/                # Reverse proxy configs
├── ml/
│   ├── serving/              # vLLM launch scripts & configs
│   ├── pipelines/            # RAG ingestion pipelines
│   └── evaluation/           # Model benchmarking scripts
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- NVIDIA GPU with CUDA 12+
- NVIDIA Container Toolkit

### 1. Clone & Configure

```bash
git clone https://github.com/gurbuzonur85/mlops-platform.git
cd mlops-platform
cp .env.example .env
# Edit .env with your settings
```

### 2. Start Core Services

```bash
# Start vector databases
docker compose -f infrastructure/docker/docker-compose.vectordb.yml up -d

# Start embedding service
docker compose -f infrastructure/docker/docker-compose.embeddings.yml up -d

# Start LLM serving (requires GPU)
docker compose -f infrastructure/docker/docker-compose.vllm.yml up -d
```

### 3. Start Monitoring

```bash
docker compose -f infrastructure/docker/docker-compose.monitoring.yml up -d
# Grafana → http://localhost:4000
# Prometheus → http://localhost:9091
```

---

## 📊 Monitoring Dashboards

### LLM Usage Dashboard
Tracks per-service metrics across all deployed applications:
- Total & daily conversations
- Active users
- Message counts (user vs assistant)
- Estimated token usage

### GPU Metrics Dashboard
Real-time NVIDIA GPU observability:
- GPU utilization (%)
- VRAM usage per GPU
- Temperature & power draw
- Multi-GPU cluster overview (8× H200)

---

## 🔧 LLM Services

| Service | Port | Model | Use Case |
|---------|------|-------|----------|
| qwen3 | 8001 | Qwen3 | General assistant |
| qwen3-coder | 8002 | Qwen3-Coder | Code generation |
| gemma | 8003 | Gemma | Lightweight tasks |
| gemma4 | 8013 | Gemma4 | Advanced reasoning |
| qwen3-VL | 8010 | Qwen3-VL | Vision + Language |

All models served with **vLLM** — persistent loading, no timeout, OpenAI-compatible API.

---

## 🔒 Security & Air-gap Deployment

This platform is designed to operate in **air-gapped environments**:
- All images pulled from private Docker registry
- No external API calls
- All models stored locally
- Internal DNS and network routing

---

## 📈 Roadmap

- [ ] MLflow experiment tracking integration
- [ ] Kubeflow Pipelines for training workflows
- [ ] Automated model evaluation & A/B testing
- [ ] CI/CD with GitHub Actions (model deployment pipeline)
- [ ] Kubernetes migration (Helm charts)
- [ ] Fine-tuning pipeline (LoRA / QLoRA)

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first.

---

## 📄 License

MIT © [gurbuzonur85](https://github.com/gurbuzonur85)
