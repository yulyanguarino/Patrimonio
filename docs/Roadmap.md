# Roadmap de Desenvolvimento - Sistema de Controle Patrimonial

O desenvolvimento do sistema será realizado de forma incremental, dividida em fases lógicas. Ao término de cada fase, o estado atual será documentado, a árvore do projeto será apresentada e o desenvolvedor aguardará a aprovação antes de passar para a próxima etapa.

---

## 🛠️ Fase 1: Infraestrutura Básica e Conexão (Ponto de Partida)
**Objetivo**: Montar a estrutura de pastas do projeto, configurar o ambiente virtual, criar o arquivo `requirements.txt`, estabelecer a conexão com o PostgreSQL e criar as configurações básicas do SQLAlchemy e do Alembic.

* **Arquivos Criados/Modificados**:
  - `requirements.txt`
  - `config/settings.py`, `config/database.py`
  - `database/connection.py`
  - `main.py` (teste de conexão simples)
  - `README.md` (instruções iniciais)
* **Entregável**: Conexão com o banco PostgreSQL validada e rodando com sucesso.

---

## 💾 Fase 2: Modelos SQLAlchemy e Migrações Alembic
**Objetivo**: Implementar as classes mapeadas do SQLAlchemy (`Base`, `Sector`, `Category`, `Employee`, `Asset`, `Maintenance`, `Attachment`) e configurar as migrações automáticas com o Alembic.

* **Arquivos Criados/Modificados**:
  - `models/base.py`, `models/sector.py`, `models/category.py`, `models/employee.py`, `models/asset.py`, `models/maintenance.py`, `models/attachment.py`
  - Configuração do `alembic.ini` e `migrations/env.py`
  - Script de sementes inicial (`database/seed.py`)
* **Entregável**: Banco de dados estruturado e populado com setores/categorias padrões (Admin, Financeiro, TI; Notebook, Monitor, etc.).

---

## 🧩 Fase 3: Repositórios e Testes de Integração
**Objetivo**: Criar a camada de acesso a dados (`Repositories`) para isolar as consultas e escritas em banco. Escrever os testes básicos para atestar o funcionamento correto do CRUD.

* **Arquivos Criados/Modificados**:
  - `repositories/base_repository.py`
  - `repositories/sector_repository.py`, `repositories/category_repository.py`, `repositories/employee_repository.py`
  - `repositories/asset_repository.py`, `repositories/maintenance_repository.py`, `repositories/attachment_repository.py`
  - `tests/test_repositories/`
* **Entregável**: Operações de persistência testadas e validadas de ponta a ponta.

---

## 🧠 Fase 4: Camada de Serviços e Regras de Negócio
**Objetivo**: Implementar as validações e comportamentos específicos do sistema nos `Services`. É nesta etapa que implementaremos o algoritmo de geração automática de códigos e as restrições de exclusão e status.

* **Arquivos Criados/Modificados**:
  - `services/sector_service.py`, `services/category_service.py`, `services/employee_service.py`
  - `services/asset_service.py` (inclui gerador de plaquetas `PAT-YYYY-XXXX`)
  - `services/maintenance_service.py`, `services/attachment_service.py`
  - `tests/test_services/`
* **Entregável**: Regras de negócio completamente cobertas por testes automatizados sem dependência visual.

---

## 🎨 Fase 5: Estrutura Base da UI e Componentes Reutilizáveis (Flet)
**Objetivo**: Criar a interface principal, menu lateral (sidebar), controle de rotas internas (navegação), gerenciamento de tema claro/escuro e componentes de UI comuns (tabelas personalizadas e modais).

* **Arquivos Criados/Modificados**:
  - `app.py` (gerenciador de rotas e layout mestre do Flet)
  - `components/sidebar.py`
  - `components/custom_table.py`
  - `components/dialogs.py`
  - `utils/formatters.py`, `utils/validators.py`
* **Entregável**: Aplicação executando com menu de navegação funcional e troca de temas ativa.

---

## 📂 Fase 6: Cadastros Auxiliares (Setores, Categorias e Funcionários)
**Objetivo**: Construir as telas simples para gerenciamento das tabelas auxiliares que alimentam o cadastro de patrimônios.

* **Arquivos Criados/Modificados**:
  - `views/sector_view.py`
  - `views/category_view.py`
  - `views/employee_view.py`
  - `controllers/sector_controller.py`, `controllers/category_controller.py`, `controllers/employee_controller.py`
* **Entregável**: Telas de cadastro, edição e listagem para Setores, Categorias e Funcionários prontas e integradas.

---

## 🖥️ Fase 7: Módulo de Patrimônios (Cadastro, Listagem e Filtros)
**Objetivo**: Desenvolver a tela principal de consulta patrimonial contendo buscas textuais, filtros avançados por setor/categoria/status e a tela para inclusão de novos bens (com numeração autogerada).

* **Arquivos Criados/Modificados**:
  - `views/asset_list_view.py`
  - `controllers/asset_controller.py`
* **Entregável**: Pesquisa, filtragem, inserção e exclusão de patrimônios funcionando.

---

## 🔍 Fase 8: Tela de Detalhes, Manutenção e Upload de Anexos
**Objetivo**: Criar a página de detalhes exclusiva de cada patrimônio, contendo histórico de manutenções, seção para registrar manutenções e o seletor de arquivos físicos para Nota Fiscal, manuais e fotos.

* **Arquivos Criados/Modificados**:
  - `views/asset_detail_view.py`
  - `views/maintenance_view.py`
  - `controllers/maintenance_controller.py`
  - `components/file_uploader.py`
  - `services/attachment_service.py` (gravação de arquivo local com UUID)
* **Entregável**: Painel do patrimônio detalhado contendo anexos e histórico completo de manutenção integrado com gravação física de arquivos.

---

## 📊 Fase 9: Dashboard e Indicadores Visuais
**Objetivo**: Construir a página inicial com métricas consolidadas (quantidade de patrimônios, bens baixados, em manutenção) e gráficos de distribuição por setor e categoria.

* **Arquivos Criados/Modificados**:
  - `views/dashboard_view.py`
  - `controllers/dashboard_controller.py`
  - `components/stat_card.py`
* **Entregável**: Painel gerencial gráfico com indicadores em tempo real.

---

## 🏁 Fase 10: Polimento Final, Revisão de Código e Testes de Aceitação
**Objetivo**: Revisar todos os padrões PEP8, garantir a tipagem estática (`Type Hints`), limpar logs, verificar bugs visuais e finalizar o arquivo `README.md` com guia passo a passo.

* **Arquivos Criados/Modificados**:
  - Ajustes de usabilidade e estilização
  - Atualização final de toda a documentação
* **Entregável**: Produto final pronto para entrega e uso interno na empresa.
