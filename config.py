"""Configurações centrais da aplicação Flask e conexão com banco de dados Supabase."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env localizado na raiz do projeto
basedir = Path(__file__).resolve().parent
load_dotenv(basedir / '.env')


class Config:
    """Configurações padrão da aplicação."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'etec-chamados-secret-key-2026-production')

    # Tratamento da URI para compatibilidade com SQLAlchemy 2.0+
    raw_db_url = os.environ.get('DATABASE_URL')
    if not raw_db_url:
        # Fallback para desenvolvimento local SQLite caso .env não seja configurado
        raw_db_url = f"sqlite:///{basedir / 'chamados_fallback.db'}"
    elif raw_db_url.startswith('postgres://'):
        raw_db_url = raw_db_url.replace('postgres://', 'postgresql+psycopg2://', 1)
    elif raw_db_url.startswith('postgresql://') and not raw_db_url.startswith('postgresql+psycopg2://'):
        raw_db_url = raw_db_url.replace('postgresql://', 'postgresql+psycopg2://', 1)

    SQLALCHEMY_DATABASE_URI = raw_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configurações de Pool de Conexões do SQLAlchemy para Postgres/Supabase
    # pool_pre_ping=True evita conexões mortas (dead connections) comuns em conexões remotas
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Credenciais Supabase caso necessárias para chamadas de API
    SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')
