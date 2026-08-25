class BusinessRuleException(Exception):
    """
    Exceção customizada usada para sinalizar violações de regras de negócio
    no sistema (ex: tentativa de excluir setor com patrimônios vinculados,
    status de patrimônio inválido, etc.).
    """
    pass
