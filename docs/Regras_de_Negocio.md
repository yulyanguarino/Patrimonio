# Regras de Negócio - Sistema de Controle Patrimonial

Este documento define as regras de negócio operacionais, validações de consistência e restrições que o sistema deve impor obrigatoriamente.

## 1. Ciclo de Vida e Estados do Patrimônio (`status`)

Os bens patrimoniais podem passar por quatro estados. A transição e os requisitos de cada estado são:

```
                  ┌───────────────┐
                  │  Disponível   │ ◄─────────────────────────┐
                  └──────┬────────┘                           │
                         │                                    │
               (Alocação de Funcionário)              (Fim Manutenção)
                         │                                    │
                         ▼                                    │
                  ┌───────────────┐                           │
                  │    Em Uso     │                           │
                  └──────┬────────┘                           │
                         │                                    │
               (Envio para Manutenção)                        │
                         │                                    │
                         ▼                                    │
                  ┌───────────────┐                           │
                  │ Em Manutenção ├───────────────────────────┘
                  └──────┬────────┘
                         │
                      (Baixa)
                         │
                         ▼
                  ┌───────────────┐
                  │    Baixado    │ (Estado Terminal)
                  └───────────────┘
```

### Regras de Validação por Status
* **Status `Disponível`**: 
  - O patrimônio está guardado ou sem alocação direta.
  - O campo `funcionario_id` (Funcionário Responsável) **deve ser nulo (vazio)**.
  - Se um patrimônio for alterado para `Disponível`, qualquer funcionário anteriormente vinculado deve ser desvinculado.
* **Status `Em uso`**:
  - O patrimônio está ativamente com um colaborador.
  - O campo `funcionario_id` **é obrigatório** e deve apontar para um funcionário válido cadastrado.
* **Status `Em manutenção`**:
  - O patrimônio está indisponível devido a defeito ou revisão.
  - O funcionário responsável pode ser mantido ou desvinculado (opcional), mas o bem é bloqueado para novas alocações de uso direto.
* **Status `Baixado`**:
  - O patrimônio foi vendido, doado, quebrado sem reparo ou descartado.
  - Este é um **estado terminal**. Um patrimônio `Baixado` **não pode** retornar para nenhum outro status.
  - Não é permitido editar nenhuma informação de um patrimônio baixado, exceto ler seus dados e seu histórico (modo somente leitura).
  - O funcionário responsável é removido automaticamente no momento da baixa.

---

## 2. Geração Automática do Número Patrimonial

O número patrimonial serve como a plaqueta de identificação física do bem e deve ser gerado de forma previsível e sequencial.
* **Formato**: Sequencial global contínuo preenchido com zeros à esquerda (mínimo de 3 dígitos), por exemplo: `001`, `002`, `003`, ..., `099`, `100`, `101`, etc.
* **Garantia de Não Reutilização**:
  - Uma vez gerado e atribuído a um patrimônio, o número patrimonial **nunca poderá ser reutilizado**, mesmo que o patrimônio correspondente seja excluído.
  - Para implementar isso de forma segura contra concorrência e falhas de deleção, utilizaremos uma **Sequence (sequência) no banco de dados PostgreSQL** (`numero_patrimonial_seq`). Cada novo patrimônio obterá seu número chamando o próximo valor da sequência (`nextval`), garantindo que o número nunca retroceda ou se repita.
* **Algoritmo de Geração**:
  1. No momento do cadastro do patrimônio, o sistema chama a Sequence do PostgreSQL para obter o próximo número inteiro.
  2. O número é formatado no Python como uma string preenchida com zeros à esquerda para ter no mínimo 3 dígitos (ex: `1` vira `001`, `99` vira `099`, `100` vira `100`, `1005` vira `1005`).
  3. Essa string é persistida na coluna `numero_patrimonial`.

---

## 3. Integridade e Restrições de Exclusão

Para evitar órfãos no banco de dados (inconsistência referencial):
* **Setores**: Não é possível excluir um Setor se houver qualquer **Funcionário** ou **Patrimônio** vinculado a ele.
* **Categorias**: Não é possível excluir uma Categoria se houver qualquer **Patrimônio** vinculado a ela.
* **Funcionários**: Não é possível excluir um Funcionário se ele for o responsável atual por algum patrimônio ativo (status `Em uso`). O patrimônio deve ser devolvido (mudar para `Disponível`) ou transferido antes da exclusão.
* **Patrimônios**: 
  - A **exclusão física** de um patrimônio deve ser restrita e permitida **apenas para corrigir erros de cadastro por usuários administradores**.
  - O descarte operacional de bens patrimoniais deve obrigatoriamente seguir o fluxo de alteração de status para `Baixado` (preservando todo o histórico de movimentações, manutenções e anexos para auditoria).
  - Caso um patrimônio seja fisicamente excluído (correção de erro), o sistema deve limpar em cascata seu histórico de manutenções e registros de anexos no banco, além de apagar os arquivos físicos correspondentes na pasta `assets/attachments/` para liberar espaço em disco. O número patrimonial associado ao patrimônio deletado **nunca será liberado ou reutilizado**, pois a sequência do banco de dados continuará incremental.

---

## 4. Manutenções e Custos

* **Custos**: O campo `valor_gasto` deve ser maior ou igual a zero (`>= 0.00`). Não é permitido registrar valores negativos.
* **Vínculo de Status**: Ao registrar uma manutenção do tipo **Corretiva**, o sistema deve perguntar amigavelmente ao usuário se ele deseja alterar o status do patrimônio para `Em manutenção` imediatamente (caso ainda não esteja).
* **Data da Próxima Manutenção**: Se informada, deve ser obrigatoriamente posterior à `data_manutencao`.

---

## 5. Gerenciamento e Upload de Anexos

* **Diretório de Armazenamento**: Os arquivos serão gravados localmente em uma pasta interna do sistema, localizada em `assets/attachments/`.
* **Segurança de Nomes**: Para evitar que arquivos com o mesmo nome se sobrescrevam (ex: dois patrimônios anexando um arquivo chamado `nota.pdf`), o sistema implementará a seguinte lógica:
  1. O arquivo original é selecionado pelo Flet FilePicker.
  2. O sistema gera um UUID v4 único (ex: `f81d4fae-7dec-11d0-a765-00a0c91e6bf6`).
  3. Extrai a extensão do arquivo original (ex: `.pdf`, `.jpg`).
  4. Salva o arquivo fisicamente na pasta de anexos com o nome `{UUID}{extensao}`.
  5. Grava no banco de dados (`anexos`):
     - `nome_arquivo`: O nome original enviado (ex: `nota.pdf`) para exibição amigável na interface.
     - `caminho_local`: O caminho relativo ou absoluto do arquivo gerado UUID (ex: `assets/attachments/f81d4fae-7dec-11d0-a765-00a0c91e6bf6.pdf`).
     - `tipo_documento`: Classificação selecionada pelo usuário ('Foto', 'Nota Fiscal', etc.).
