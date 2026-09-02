import os
from datetime import date
from typing import List, Dict
from sqlalchemy.orm import Session
from models.asset import Asset
from repositories.asset_repository import AssetRepository
from repositories.category_repository import CategoryRepository
from repositories.sector_repository import SectorRepository
from repositories.employee_repository import EmployeeRepository
from utils.exceptions import BusinessRuleException

# Categorias de bens que não têm um responsável individual (são do
# setor/ambiente, não de uma pessoa) -- não exigem funcionário quando "Em uso".
NO_RESPONSIBLE_CATEGORIES = {"Ar Condicionado", "Switch"}

class AssetService:
    def __init__(self, db: Session):
        self.db = db
        self.asset_repo = AssetRepository(db)
        self.category_repo = CategoryRepository(db)
        self.sector_repo = SectorRepository(db)
        self.employee_repo = EmployeeRepository(db)

    def create_asset(
        self,
        nome: str,
        categoria_id: int,
        setor_id: int,
        funcionario_id: int | None = None,
        data_compra: date | None = None,
        nota_fiscal: str | None = None,
        garantia_meses: int | None = None,
        status: str = "Disponível",
        observacoes: str | None = None
    ) -> Asset:
        """
        Cadastra um novo patrimônio. Obtém um número patrimonial contínuo
        gerado pela sequence e valida regras de status e responsabilidade.
        """
        nome = nome.strip()
        if not nome:
            raise BusinessRuleException("O nome do patrimônio não pode ser vazio.")
            
        # Validação de Categoria e Setor
        category = self.category_repo.get_by_id(categoria_id)
        if not category:
            raise BusinessRuleException("A categoria selecionada é inválida ou não existe.")
        if not self.sector_repo.get_by_id(setor_id):
            raise BusinessRuleException("O setor selecionado é inválido ou não existe.")

        # Validação do Status
        valid_statuses = {"Disponível", "Em uso", "Em manutenção", "Baixado"}
        if status not in valid_statuses:
            raise BusinessRuleException(f"Status '{status}' é inválido.")

        # Validações condicionais por Status. Categorias em NO_RESPONSIBLE_CATEGORIES sao excecao: nao
        # tem um responsável individual, é um bem do setor/ambiente.
        if status == "Em uso" and category.nome not in NO_RESPONSIBLE_CATEGORIES:
            if not funcionario_id:
                raise BusinessRuleException("O funcionário responsável é obrigatório quando o status for 'Em uso'.")
            emp = self.employee_repo.get_by_id(funcionario_id)
            if not emp:
                raise BusinessRuleException("Funcionário selecionado é inválido.")
        else:
            # Sem uso, baixado, em manutenção, ou Ar Condicionado em uso:
            # garante que não fica com um funcionário vinculado sem sentido.
            funcionario_id = None

        if garantia_meses is not None and garantia_meses < 0:
            raise BusinessRuleException("O tempo de garantia em meses não pode ser negativo.")

        # Obtém o próximo valor sequencial e formata com zeros à esquerda (mínimo de 3 dígitos)
        next_seq = self.asset_repo.get_next_sequence_value()
        numero_patrimonial = f"{next_seq:03d}"

        asset = Asset(
            numero_patrimonial=numero_patrimonial,
            nome=nome,
            categoria_id=categoria_id,
            setor_id=setor_id,
            funcionario_id=funcionario_id,
            data_compra=data_compra,
            nota_fiscal=nota_fiscal.strip() if nota_fiscal else None,
            garantia_meses=garantia_meses,
            status=status,
            observacoes=observacoes.strip() if observacoes else None
        )
        
        return self.asset_repo.create(asset)

    def update_asset(
        self,
        asset_id: int,
        nome: str,
        categoria_id: int,
        setor_id: int,
        funcionario_id: int | None = None,
        data_compra: date | None = None,
        nota_fiscal: str | None = None,
        garantia_meses: int | None = None,
        status: str = "Disponível",
        observacoes: str | None = None
    ) -> Asset:
        """
        Atualiza dados de um patrimônio, garantindo que bens já baixados 
        não sejam modificados de forma indevida.
        """
        asset = self.asset_repo.get_by_id(asset_id)
        if not asset:
            raise BusinessRuleException("Patrimônio não encontrado.")

        # Regra de terminalidade: patrimônio baixado não pode ser modificado
        if asset.status == "Baixado":
            raise BusinessRuleException("Não é permitido editar patrimônios que já foram baixados.")

        nome = nome.strip()
        if not nome:
            raise BusinessRuleException("O nome do patrimônio não pode ser vazio.")

        # Validação de Categoria e Setor
        category = self.category_repo.get_by_id(categoria_id)
        if not category:
            raise BusinessRuleException("A categoria selecionada é inválida ou não existe.")
        if not self.sector_repo.get_by_id(setor_id):
            raise BusinessRuleException("O setor selecionado é inválido ou não existe.")

        valid_statuses = {"Disponível", "Em uso", "Em manutenção", "Baixado"}
        if status not in valid_statuses:
            raise BusinessRuleException(f"Status '{status}' é inválido.")

        # Validações de Status e Funcionário. Categorias em NO_RESPONSIBLE_CATEGORIES sao excecao: nao
        # tem um responsável individual, é um bem do setor/ambiente.
        if status == "Em uso" and category.nome not in NO_RESPONSIBLE_CATEGORIES:
            if not funcionario_id:
                raise BusinessRuleException("O funcionário responsável é obrigatório quando o status for 'Em uso'.")
            emp = self.employee_repo.get_by_id(funcionario_id)
            if not emp:
                raise BusinessRuleException("Funcionário selecionado é inválido.")
        else:
            funcionario_id = None

        if garantia_meses is not None and garantia_meses < 0:
            raise BusinessRuleException("O tempo de garantia em meses não pode ser negativo.")

        # Atualiza campos
        asset.nome = nome
        asset.categoria_id = categoria_id
        asset.setor_id = setor_id
        asset.funcionario_id = funcionario_id
        asset.data_compra = data_compra
        asset.nota_fiscal = nota_fiscal.strip() if nota_fiscal else None
        asset.garantia_meses = garantia_meses
        asset.status = status
        asset.observacoes = observacoes.strip() if observacoes else None

        return self.asset_repo.update(asset)

    def delete_asset(self, asset_id: int) -> None:
        """
        Remove o patrimônio fisicamente (para correção de erros por administradores),
        apagando em cascata seus registros e excluindo do disco os arquivos de anexo físicos.
        """
        asset = self.asset_repo.get_by_id(asset_id)
        if not asset:
            raise BusinessRuleException("Patrimônio não encontrado.")
            
        # Apaga os arquivos físicos locais do disco antes da deleção no banco
        for attachment in asset.attachments:
            if attachment.caminho_local and os.path.exists(attachment.caminho_local):
                try:
                    os.remove(attachment.caminho_local)
                except Exception as e:
                    # Apenas avisa ou loga, para não interromper a transação se o arquivo físico sumiu
                    print(f"[Warning] Falha ao excluir arquivo físico de anexo: {attachment.caminho_local}. Erro: {e}")

        self.asset_repo.delete(asset)

    def search_assets(
        self,
        query_text: str | None = None,
        category_id: int | None = None,
        sector_id: int | None = None,
        status: str | None = None
    ) -> List[Asset]:
        """Consulta patrimônios aplicando filtros via repositório."""
        return self.asset_repo.search_assets(query_text, category_id, sector_id, status)

    def get_asset_by_id(self, asset_id: int) -> Asset | None:
        """Busca um patrimônio pelo ID."""
        return self.asset_repo.get_by_id(asset_id)

    def get_dashboard_metrics(self) -> Dict[str, int]:
        """Métricas de contagem de status para exibição no Dashboard."""
        return self.asset_repo.get_dashboard_metrics()

    def get_assets_by_sector_summary(self) -> List[tuple]:
        """Resumo numérico por setor."""
        return self.asset_repo.get_assets_by_sector_summary()

    def get_assets_by_category_summary(self) -> List[tuple]:
        """Resumo numérico por categoria."""
        return self.asset_repo.get_assets_by_category_summary()
