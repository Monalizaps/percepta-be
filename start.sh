#!/bin/bash

echo "🚀 Iniciando o backend Percepta..."

# Ativa o ambiente virtual (se estiver usando venv)
if [ -d "venv" ]; then
  source venv/bin/activate
  echo "🔄 Ambiente virtual ativado."
fi

# Instala dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Sobe o FastAPI
echo "⚙️ Rodando FastAPI com Uvicorn..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000
