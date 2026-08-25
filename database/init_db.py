from sqlalchemy import text
from config.database import engine
from models.base import Base
from database.seed import seed_db

def init_database():
    print("Inicializando o banco de dados...")
    
    try:
        # 1. Cria a Sequence do número patrimonial apenas se for PostgreSQL
        if engine.dialect.name != "sqlite":
            with engine.connect() as conn:
                conn.execute(text("CREATE SEQUENCE IF NOT EXISTS numero_patrimonial_seq START WITH 1 INCREMENT BY 1;"))
                conn.commit()
                print("Sequence 'numero_patrimonial_seq' criada ou já existente no PostgreSQL.")
        else:
            print("Usando SQLite: Sequence não necessária.")
            
        # 2. Cria todas as tabelas mapeadas no SQLAlchemy
        Base.metadata.create_all(bind=engine)
        print("Tabelas criadas com sucesso!")
        
        # 3. Alimenta as tabelas com os setores e categorias iniciais
        seed_db()
        
        print("Banco de dados inicializado com sucesso!")
    except Exception as e:
        print(f"Erro crítico ao inicializar o banco de dados: {e}")
        if engine.dialect.name != "sqlite":
            print("Dica: Verifique se o PostgreSQL está ativo e se o banco especificado existe.")

if __name__ == "__main__":
    init_database()
