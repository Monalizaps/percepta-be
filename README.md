# 📊 Percepta - Script de Detecção de Anomalias com HBOS

Este projeto contém um exemplo simples de uso do algoritmo **HBOS (Histogram-Based Outlier Score)** para detectar comportamentos anômalos em logs de autenticação simulados.

---

## 📁 Estrutura

```
backend/
├── data/
│   └── raw_logs.csv             # Dados simulados de autenticação
├── run_hbos.py                  # Script de análise HBOS
```

---

## ▶️ Como rodar

1. Certifique-se de estar no ambiente virtual (venv) com as dependências instaladas:

```bash
source venv/bin/activate
```

2. Rode o script:

```bash
cd backend
python run_hbos.py
```

3. O resultado será salvo em:

```
data/anomalies_detected.json
```

---

## 🧠 O que é HBOS?

O **HBOS** é um algoritmo de detecção de anomalias não supervisionado, baseado em histogramas de distribuição para cada feature. Ele é **extremamente rápido**, ideal para grandes volumes de dados onde há independência entre atributos.

> Para mais detalhes técnicos, veja o [paper original (Goldstein & Dengel, 2012)](https://www.goldiges.de/publications/HBOS-KI-2012.pdf)

---

## 📌 Observação

Este script é um ponto de partida. No projeto completo (Percepta), esses dados serão analisados dinamicamente pela API com integração ao Firestore ou banco real.
