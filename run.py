"""Ponto de entrada para execução do servidor de desenvolvimento Flask."""

from app import create_app
from app.extensions import db

app = create_app()

if __name__ == '__main__':
    # Auto-inicialização de tabelas e carga essencial caso a base esteja vazia
    try:
        with app.app_context():
            db.create_all()
            from app.models.user import User
            if User.query.count() == 0:
                print("Base de dados recém-criada. Executando seed inicial...")
                from seeds.seed_supabase import reset_and_seed_admin
                reset_and_seed_admin()
    except Exception as e:
        print(f"Aviso de inicialização do banco: {e}")

    print("Iniciando Sistema de Chamados ETEC...")
    print("Acesse em seu navegador: http://127.0.0.1:5000/")
    app.run(debug=True, host='127.0.0.1', port=5000)
