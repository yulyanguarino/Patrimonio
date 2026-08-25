# Arquitetura do Projeto - Sistema de Controle Patrimonial

Este documento descreve as decisões arquiteturais adotadas no projeto para garantir que o sistema seja robusto, escalável, testável e de fácil manutenção.

## Padrão Arquitetural: Camadas (Clean / Layered Architecture)

O sistema é dividido em camadas bem delimitadas, onde a dependência aponta sempre da camada de apresentação para a de infraestrutura de dados:

```
[ Camada de Apresentação (UI) ]
       Views & Components (Flet)
               │
               ▼
[ Camada de Mediação ]
       Controllers
               │
               ▼
[ Camada de Domínio / Regras de Negócio ]
       Services (Validações, Lógica de Negócio)
               │
               ▼
[ Camada de Infraestrutura / Acesso a Dados ]
       Repositories (SQLAlchemy ORM) ──► PostgreSQL DB
```

### Detalhamento das Camadas

1. **Apresentação (`Views` & `Components`)**:
   - Desenvolvida usando a biblioteca **Flet** (baseada em Flutter).
   - Não conhece o SQLAlchemy nem se comunica diretamente com o banco de dados.
   - Comunica-se exclusivamente com a camada de **Controllers** para enviar comandos do usuário (clique em botões, digitação de texto) e obter dados formatados para exibição.
   
2. **Mediação (`Controllers`)**:
   - Atua como uma ponte.
   - Captura eventos do Flet (por exemplo, `on_click`, `on_change`).
   - Gerencia o estado da tela (exibição de indicadores de carregamento, diálogos de erro).
   - Invoca a camada de **Services** para a execução de regras de negócio.
   - Converte os dados brutos de domínio em modelos de exibição amigáveis para a interface gráfica.

3. **Negócio (`Services`)**:
   - Concentra toda a inteligência do negócio (regras de status, verificação de dependências, geração do código do patrimônio, upload físico de anexos).
   - Abre e gerencia transações de banco de dados por meio da injeção de sessão do SQLAlchemy.
   - Não depende de nenhuma biblioteca gráfica (independente de Flet), facilitando testes unitários isolados.

4. **Acesso a Dados (`Repositories`)**:
   - Implementa o padrão *Repository*.
   - Encapsula as consultas SQL e interações do ORM SQLAlchemy.
   - Isolando o ORM na camada de persistência, facilitamos a troca de banco de dados ou da tecnologia de persistência no futuro.

---

## Fluxo de Dados e Controle

Para exemplificar o fluxo de dados no sistema, veja o diagrama de sequência abaixo para o cadastro de um novo patrimônio:

```
[ View (UI) ]      [ Controller ]         [ Service ]         [ Repository ]      [ Banco de Dados ]
     │                   │                     │                    │                     │
     │──1. clique cadastrar ──►                │                    │                     │
     │                   │──2. validar campos ─►                    │                     │
     │                   │                     │──3. gerar número ──►                     │ (Busca max)
     │                   │                     │   patrimonial      │                     │
     │                   │                     │                    │                     │
     │                   │                     │──4. persistir ────►│                     │
     │                   │                     │    patrimônio      │──5. INSERT / COMMIT ─►
     │                   │                     │                    │◄──6. Retorna Objeto──
     │                   │                     │◄──7. Retorna Ativo─│                     │
     │                   │◄──8. Sucesso (Ativo)│                    │                     │
     │◄──9. Atualizar UI ──│                     │                    │                     │
```

---

## Injeção de Dependências

Para evitar acoplamento forte entre as classes, utilizaremos injeção de dependências via construtores. 
Por exemplo, o `AssetController` recebe o `AssetService` em seu construtor, que por sua vez recebe o `AssetRepository` e a sessão do banco.

```python
# Exemplo conceitual de acoplamento fraco:
db_session = get_db_session()
asset_repository = AssetRepository(db_session)
asset_service = AssetService(asset_repository)
asset_controller = AssetController(asset_service)
```

Essa abordagem facilita a criação de mocks durante os testes de unidade da camada de serviços.

---

## Gerenciamento de Estado no Flet

O Flet gerencia a interface em termos de árvores de componentes (`Controls`). No nosso projeto:
- Cada tela é representada por uma classe que estende a estrutura do Flet (como `ft.Container` ou `ft.Column`).
- O estado de cada campo (por exemplo, dropdowns com lista de funcionários ou setores) é populado através do Controller no momento em que a tela é montada (`on_mount` ou inicialização).
- Operações assíncronas (como salvar no banco) utilizarão um indicador de carregamento (`ft.ProgressRing`) para manter a interface responsiva.

---

## Tratamento de Erros e Exceções

O sistema implementa uma estratégia de captura em camadas:
- **Exceções de Domínio**: Exceções customizadas (ex: `BusinessRuleException`) são levantadas na camada de `Services` quando uma regra de negócio é violada.
- **Exceções de Banco**: Tratadas na camada de `Repository` ou `Service` para reverter transações (`rollback`) em caso de erros no PostgreSQL.
- **Exceções na UI**: O `Controller` captura as exceções e interage com a View para exibir modais informativos amigáveis (usando `ft.AlertDialog` ou `SnackBar`), evitando falhas catastróficas ou fechamento inesperado do aplicativo.

---

## Logging

As operações críticas, como transações financeiras (manutenção), baixas de patrimônio e erros de conexão com o banco de dados, serão registradas no diretório `logs/` utilizando a biblioteca padrão `logging` do Python, com rotação diária de arquivos.
