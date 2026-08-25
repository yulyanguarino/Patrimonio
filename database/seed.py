from database.connection import get_db
from models.sector import Sector
from models.category import Category

def seed_db():
    print("Semeando dados padrão no banco de dados...")
    
    # Setores sugeridos
    default_sectors = [
        "Administrativo",
        "Financeiro",
        "Compras",
        "TI",
        "Comercial",
        "Expedição"
    ]
    
    # Categorias sugeridas
    default_categories = [
        "Notebook",
        "Monitor",
        "Impressora",
        "Mesa",
        "Cadeira",
        "Ferramenta",
        "Ar Condicionado",
        "Outros"
    ]
    
    try:
        with get_db() as db:
            # Insere os setores se não existirem
            for sector_name in default_sectors:
                existing_sector = db.query(Sector).filter_by(nome=sector_name).first()
                if not existing_sector:
                    db.add(Sector(nome=sector_name))
                    print(f"Setor semeado: {sector_name}")
            
            # Insere as categorias se não existirem
            for category_name in default_categories:
                existing_category = db.query(Category).filter_by(nome=category_name).first()
                if not existing_category:
                    db.add(Category(nome=category_name))
                    print(f"Categoria semeada: {category_name}")
                    
        print("Sementeira de dados concluída com sucesso!")
    except Exception as e:
        print(f"Erro ao semear banco de dados: {e}")

if __name__ == "__main__":
    seed_db()
