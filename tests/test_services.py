import os
import tempfile
import pytest
from datetime import date
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.base import Base
from services.sector_service import SectorService
from services.category_service import CategoryService
from services.employee_service import EmployeeService
from services.asset_service import AssetService
from services.maintenance_service import MaintenanceService
from services.attachment_service import AttachmentService
from utils.exceptions import BusinessRuleException

@pytest.fixture(name="db_session")
def fixture_db_session():
    """Conexão isolada do SQLite em memória para testar lógica de negócio."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_sector_service_rules(db_session):
    sec_service = SectorService(db_session)
    
    # 1. Valida setor com nome vazio ou espaços
    with pytest.raises(BusinessRuleException, match="nome do setor não pode ser vazio"):
        sec_service.create_sector("   ")
        
    # 2. Cadastro correto
    sector = sec_service.create_sector("TI")
    assert sector.id is not None
    assert sector.nome == "TI"
    
    # 3. Valida unicidade de nome do setor
    with pytest.raises(BusinessRuleException, match="Já existe um setor cadastrado"):
        sec_service.create_sector("TI")

def test_category_service_rules(db_session):
    cat_service = CategoryService(db_session)
    
    # 1. Cadastro correto
    cat = cat_service.create_category("Notebook")
    assert cat.id is not None
    
    # 2. Valida unicidade da categoria
    with pytest.raises(BusinessRuleException, match="Já existe uma categoria cadastrada"):
        cat_service.create_category("Notebook")

def test_employee_service_rules(db_session):
    sec_service = SectorService(db_session)
    emp_service = EmployeeService(db_session)
    
    sector = sec_service.create_sector("TI")
    
    # 1. Valida cadastro com setor inválido/inexistente
    with pytest.raises(BusinessRuleException, match="setor selecionado é inválido"):
        emp_service.create_employee("João", 999)
        
    # 2. Valida funcionário com nome vazio
    with pytest.raises(BusinessRuleException, match="nome do funcionário não pode ser vazio"):
        emp_service.create_employee("", sector.id)
        
    employee = emp_service.create_employee("João Silva", sector.id)
    assert employee.id is not None

def test_asset_service_rules_and_number_generation(db_session):
    sec_service = SectorService(db_session)
    cat_service = CategoryService(db_session)
    emp_service = EmployeeService(db_session)
    asset_service = AssetService(db_session)
    
    sector = sec_service.create_sector("TI")
    category = cat_service.create_category("Notebook")
    employee = emp_service.create_employee("João Silva", sector.id)
    
    # 1. Teste de preenchimento e formatação do Número Patrimonial (zeros à esquerda)
    asset1 = asset_service.create_asset("Notebook Dell", category.id, sector.id, status="Disponível")
    assert asset1.numero_patrimonial == "001"
    
    asset2 = asset_service.create_asset("Monitor LG", category.id, sector.id, status="Disponível")
    assert asset2.numero_patrimonial == "002"
    
    # 2. Teste status 'Em uso' exige funcionário responsável
    with pytest.raises(BusinessRuleException, match="funcionário responsável é obrigatório"):
        asset_service.create_asset("Notebook 3", category.id, sector.id, status="Em uso")
        
    # 3. Teste status 'Em uso' com funcionário válido
    asset3 = asset_service.create_asset("Notebook 3", category.id, sector.id, funcionario_id=employee.id, status="Em uso")
    assert asset3.funcionario_id == employee.id
    
    # 4. Teste status 'Disponível' remove funcionário responsável automaticamente
    asset4 = asset_service.create_asset("Notebook 4", category.id, sector.id, funcionario_id=employee.id, status="Disponível")
    assert asset4.funcionario_id is None
    
    # 5. Teste impede edição de patrimônio Baixado (terminalidade)
    asset1.status = "Baixado"
    db_session.commit()
    with pytest.raises(BusinessRuleException, match="Não é permitido editar patrimônios que já foram baixados"):
        asset_service.update_asset(asset1.id, "Notebook Dell Novo", category.id, sector.id, status="Disponível")

def test_maintenance_service_rules(db_session):
    sec_service = SectorService(db_session)
    cat_service = CategoryService(db_session)
    asset_service = AssetService(db_session)
    maint_service = MaintenanceService(db_session)
    
    sector = sec_service.create_sector("TI")
    category = cat_service.create_category("Notebook")
    asset = asset_service.create_asset("Notebook Dell", category.id, sector.id, status="Disponível")
    
    # 1. Teste impede valor gasto negativo
    with pytest.raises(BusinessRuleException, match="valor gasto não pode ser negativo"):
        maint_service.register_maintenance(
            patrimonio_id=asset.id,
            tipo="Corretiva",
            data_manutencao=date(2026, 6, 1),
            prestador="Técnico Autorizado",
            descricao_problema="Defeito na placa mãe",
            servico_executado="Troca de placa",
            valor_gasto=-50.00
        )
        
    # 2. Teste impede data de próxima manutenção retroativa
    with pytest.raises(BusinessRuleException, match="data da próxima manutenção não pode ser anterior"):
        maint_service.register_maintenance(
            patrimonio_id=asset.id,
            tipo="Preventiva",
            data_manutencao=date(2026, 6, 10),
            prestador="Técnico",
            descricao_problema="Rotina",
            servico_executado="Limpeza interna",
            valor_gasto=150.00,
            data_proxima=date(2026, 6, 9)
        )
        
    # 3. Teste atualização automática do status do bem ao registrar Corretiva
    maint = maint_service.register_maintenance(
        patrimonio_id=asset.id,
        tipo="Corretiva",
        data_manutencao=date(2026, 6, 10),
        prestador="Suporte Técnico",
        descricao_problema="Não liga",
        servico_executado="Reparo na fonte",
        valor_gasto=200.00,
        set_asset_in_maintenance=True
    )
    assert asset.status == "Em manutenção"
    assert asset.funcionario_id is None

def test_attachment_service_physical_upload(db_session):
    sec_service = SectorService(db_session)
    cat_service = CategoryService(db_session)
    asset_service = AssetService(db_session)
    att_service = AttachmentService(db_session)
    
    sector = sec_service.create_sector("TI")
    category = cat_service.create_category("Notebook")
    asset = asset_service.create_asset("Notebook Dell", category.id, sector.id, status="Disponível")
    
    # 1. Cria um arquivo temporário físico para simular o upload do FilePicker
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
        tmp_file.write(b"Conteudo da Nota Fiscal")
        temp_path = tmp_file.name
        
    try:
        # 2. Executa inclusão do anexo
        attachment = att_service.add_attachment(
            source_path=temp_path,
            tipo_documento="Nota Fiscal",
            patrimonio_id=asset.id
        )
        
        assert attachment.id is not None
        assert Path(attachment.caminho_local).exists()
        assert attachment.nome_arquivo == Path(temp_path).name
        
        # 3. Testa exclusão lógica e física correspondente do disco
        local_path = Path(attachment.caminho_local)
        att_service.delete_attachment(attachment.id)
        assert not local_path.exists()
        
    finally:
        # Garante a limpeza do arquivo temporário original usado como fonte do teste
        if os.path.exists(temp_path):
            os.remove(temp_path)
