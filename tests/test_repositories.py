import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.base import Base
from models.sector import Sector
from models.category import Category
from models.employee import Employee
from models.asset import Asset
from models.maintenance import Maintenance
from models.attachment import Attachment

from repositories.sector_repository import SectorRepository
from repositories.category_repository import CategoryRepository
from repositories.employee_repository import EmployeeRepository
from repositories.asset_repository import AssetRepository
from repositories.maintenance_repository import MaintenanceRepository
from repositories.attachment_repository import AttachmentRepository

@pytest.fixture(name="db_session")
def fixture_db_session():
    """Cria uma conexão em memória do SQLite específica para testes unitários/integração."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_sector_repository(db_session):
    repo = SectorRepository(db_session)
    
    # 1. Criação de Setor
    sector = Sector(nome="TI")
    repo.create(sector)
    db_session.commit()

    assert sector.id is not None
    
    # 2. Busca por ID
    fetched = repo.get_by_id(sector.id)
    assert fetched is not None
    assert fetched.nome == "TI"

    # 3. Busca por Nome (case-insensitive)
    fetched_by_name = repo.get_by_name("ti")
    assert fetched_by_name is not None
    assert fetched_by_name.id == sector.id

def test_category_repository(db_session):
    repo = CategoryRepository(db_session)
    
    # 1. Criação de Categoria
    category = Category(nome="Notebook")
    repo.create(category)
    db_session.commit()

    assert category.id is not None
    
    # 2. Busca por Nome
    fetched = repo.get_by_name("notebook")
    assert fetched is not None
    assert fetched.id == category.id

def test_employee_repository(db_session):
    sector_repo = SectorRepository(db_session)
    emp_repo = EmployeeRepository(db_session)
    
    sector = Sector(nome="TI")
    sector_repo.create(sector)
    db_session.commit()

    # 1. Criação de Funcionário
    employee = Employee(nome="João Silva", setor_id=sector.id)
    emp_repo.create(employee)
    db_session.commit()

    assert employee.id is not None
    
    # 2. Busca por ID
    fetched = emp_repo.get_by_id(employee.id)
    assert fetched.nome == "João Silva"
    
    # 3. Busca por Setor
    by_sector = emp_repo.get_by_sector(sector.id)
    assert len(by_sector) == 1
    assert by_sector[0].id == employee.id

def test_asset_and_maintenance_repositories(db_session):
    sec_repo = SectorRepository(db_session)
    cat_repo = CategoryRepository(db_session)
    emp_repo = EmployeeRepository(db_session)
    asset_repo = AssetRepository(db_session)
    maint_repo = MaintenanceRepository(db_session)
    att_repo = AttachmentRepository(db_session)

    sector = Sector(nome="TI")
    sec_repo.create(sector)
    
    category = Category(nome="Notebook")
    cat_repo.create(category)
    
    employee = Employee(nome="João", setor_id=sector.id)
    emp_repo.create(employee)
    db_session.flush()

    # 1. Teste da Sequence Simulada no SQLite
    seq1 = asset_repo.get_next_sequence_value()
    assert seq1 == 1

    # 2. Criação de Patrimônio
    asset = Asset(
        numero_patrimonial="001",
        nome="Laptop Dell",
        categoria_id=category.id,
        setor_id=sector.id,
        funcionario_id=employee.id,
        status="Em uso",
        data_compra=date(2026, 1, 1),
        garantia_meses=12
    )
    asset_repo.create(asset)
    db_session.commit()

    assert asset.id is not None

    # 3. Métricas de Dashboard
    metrics = asset_repo.get_dashboard_metrics()
    assert metrics["Total"] == 1
    assert metrics["Em uso"] == 1
    assert metrics["Disponível"] == 0

    # 4. Pesquisa Textual e Filtro
    results = asset_repo.search_assets(query_text="Laptop")
    assert len(results) == 1
    assert results[0].numero_patrimonial == "001"

    # 5. Registro de Manutenção
    maint = Maintenance(
        patrimonio_id=asset.id,
        tipo="Corretiva",
        data_manutencao=date(2026, 6, 1),
        prestador="Suporte Dell",
        descricao_problema="Tela piscando",
        servico_executado="Troca do cabo flat",
        valor_gasto=150.00
    )
    maint_repo.create(maint)
    db_session.commit()

    assert maint.id is not None

    # 6. Filtragem de Manutenções
    maints = maint_repo.filter_maintenances(asset_id=asset.id)
    assert len(maints) == 1
    assert maints[0].valor_gasto == 150.00

    # 7. Inclusão de Anexo
    att = Attachment(
        patrimonio_id=asset.id,
        nome_arquivo="nota_fiscal.pdf",
        caminho_local="assets/attachments/nf-uuid.pdf",
        tipo_documento="Nota Fiscal"
    )
    att_repo.create(att)
    db_session.commit()

    assert att.id is not None
    atts = att_repo.get_by_asset_id(asset.id)
    assert len(atts) == 1
    assert atts[0].nome_arquivo == "nota_fiscal.pdf"
