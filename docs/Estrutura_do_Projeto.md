# Estrutura do Projeto - Sistema de Controle Patrimonial

Este documento detalha a estrutura de pastas do sistema, definindo as responsabilidades de cada diretório.

## Árvore de Diretórios

O projeto seguirá a seguinte organização:

```
PATRIMONIO/
├── main.py                # Ponto de entrada do sistema (inicializa o Flet)
├── app.py                 # Classe principal da aplicação (rotas, estado global, tema)
├── requirements.txt       # Dependências do Python (Flet, SQLAlchemy, Alembic, psycopg2-binary, etc.)
├── README.md              # Instruções de instalação e execução do projeto
│
├── config/                # Configurações globais e de ambiente
│   ├── __init__.py
│   ├── settings.py        # Variáveis de ambiente e constantes (DB_URL, caminhos)
│   └── database.py        # Configuração do Engine e Session do SQLAlchemy
│
├── database/              # Conexões e ciclo de vida das transações
│   ├── __init__.py
│   └── connection.py      # Gerenciamento de sessões com context managers
│
├── models/                # Entidades e mapeamento ORM (SQLAlchemy)
│   ├── __init__.py
│   ├── base.py            # Classe base declarativa
│   ├── sector.py          # Modelo do Setor
│   ├── category.py        # Modelo da Categoria
│   ├── employee.py        # Modelo do Funcionário
│   ├── asset.py           # Modelo do Patrimônio
│   ├── maintenance.py     # Modelo da Manutenção
│   └── attachment.py      # Modelo do Anexo (caminho físico do arquivo no disco)
│
├── repositories/          # Interface com o Banco de Dados (CRUD e Consultas Específicas)
│   ├── __init__.py
│   ├── base_repository.py # Repositório genérico com operações CRUD comuns
│   ├── sector_repository.py
│   ├── category_repository.py
│   ├── employee_repository.py
│   ├── asset_repository.py
│   ├── maintenance_repository.py
│   └── attachment_repository.py
│
├── services/              # Camada de Negócios e Validações
│   ├── __init__.py
│   ├── sector_service.py      # Regras de negócio de Setores
│   ├── category_service.py    # Regras de negócio de Categorias
│   ├── employee_service.py    # Regras de negócio de Funcionários
│   ├── asset_service.py       # Regras de negócio de Patrimônios (ex: geração de código)
│   ├── maintenance_service.py # Regras de negócio de Manutenções
│   └── attachment_service.py  # Regras de salvamento físico de anexos e validações
│
├── controllers/           # Ponte entre Views (UI) e Services (Negócios)
│   ├── __init__.py
│   ├── base_controller.py     # Controlador base
│   ├── dashboard_controller.py
│   ├── sector_controller.py
│   ├── category_controller.py
│   ├── employee_controller.py
│   ├── asset_controller.py
│   └── maintenance_controller.py
│
├── views/                 # Telas da Aplicação (Flet Views)
│   ├── __init__.py
│   ├── base_view.py           # Classe base para telas (gerenciamento de estado local)
│   ├── dashboard_view.py      # Tela inicial (indicadores e gráficos)
│   ├── sector_view.py         # Tela de cadastro/listagem de Setores
│   ├── category_view.py       # Tela de cadastro/listagem de Categorias
│   ├── employee_view.py       # Tela de cadastro/listagem de Funcionários
│   ├── asset_list_view.py     # Tela de consulta, pesquisa, filtro e deleção de Patrimônios
│   ├── asset_detail_view.py   # Tela de detalhes de um Patrimônio (com anexos e manutenções)
│   └── maintenance_view.py    # Tela de histórico e registro de manutenções
│
├── components/            # Componentes visuais customizados e reutilizáveis (Flet)
│   ├── __init__.py
│   ├── sidebar.py             # Menu lateral de navegação
│   ├── custom_table.py        # Tabela genérica paginada e ordenável
│   ├── stat_card.py           # Card de indicador numérico para o Dashboard
│   ├── file_uploader.py       # Componente de arrastar/selecionar arquivos (anexos)
│   └── dialogs.py             # Modais de confirmação e alertas
│
├── utils/                 # Funções utilitárias e ajudantes
│   ├── __init__.py
│   ├── formatters.py          # Formatadores de moeda, data e número patrimonial
│   ├── validators.py          # Validadores comuns de campos
│   └── logger.py              # Utilitário de logging do sistema
│
├── assets/                # Arquivos estáticos da aplicação
│   ├── icons/                 # Ícones adicionais (caso necessário)
│   ├── images/                # Imagens/logos do sistema
│   └── attachments/           # Pasta onde serão salvos os arquivos físicos dos anexos
│
├── docs/                  # Documentações técnicas e de negócio do projeto
│
├── migrations/            # Arquivos de migração de banco de dados (Alembic)
│
├── logs/                  # Arquivos de log de execução em produção/desenvolvimento
│
└── tests/                 # Testes automatizados (Unitários e de Integração)
    ├── __init__.py
    ├── test_services/
    └── test_repositories/
```

## Diretrizes de Responsabilidade

1. **Modelos (`models/`)**: Devem conter apenas a definição da tabela, colunas, relacionamentos e tipos do SQLAlchemy. Nenhuma regra de negócio deve residir nos modelos.
2. **Repositórios (`repositories/`)**: Toda a sintaxe SQL e chamadas ao SQLAlchemy ficam aqui. Os repositórios retornam objetos do Python ou do SQLAlchemy. Eles não validam regras de negócio.
3. **Serviços (`services/`)**: É o cérebro do sistema. Valida se um funcionário pertence a um setor ativo, calcula valores, gera códigos automatizados, formata regras de integridade e abre/fecha transações de banco.
4. **Controladores (`controllers/`)**: Recebem as interações do Flet, repassam para os serviços adequados, capturam exceções e convertem o resultado para um formato que a View possa renderizar.
5. **Views (`views/`) e Componentes (`components/`)**: Construção visual e layout usando Flet. Devem ser o mais burros possível, delegando eventos e validações de dados para os controladores.
