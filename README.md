# Sistema de Controle Patrimonial

Sistema desktop de Controle Patrimonial interno desenvolvido em Python com a biblioteca Flet (front-end reativo) e banco de dados PostgreSQL (com SQLAlchemy e Alembic).

## 🚀 Como Executar o Projeto

### Pré-requisitos
* Python 3.11 ou superior instalado
* PostgreSQL instalado e rodando em sua máquina ou servidor

### Passo 1: Clonar/Acessar a Pasta do Projeto
Abra o terminal no diretório do projeto:
```bash
cd C:\Users\Tidimar\Desktop\PATRIMONIO
```

### Passo 2: Criar e Ativar o Ambiente Virtual (Recomendado)
No terminal:
```powershell
# Criar ambiente virtual (.venv)
python -m venv .venv

# Ativar ambiente virtual no Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

### Passo 3: Instalar as Dependências
Com o ambiente virtual ativo, instale as dependências contidas no arquivo `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Passo 4: Configurar as Variáveis de Ambiente (.env)
Crie um arquivo chamado `.env` na raiz do projeto contendo as credenciais de acesso ao seu PostgreSQL. Exemplo:
```env
DB_USER=postgres
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432
DB_NAME=patrimonio_db
```

*Nota: Certifique-se de que o banco de dados especificado em `DB_NAME` existe no PostgreSQL.*

### Passo 5: Executar o Aplicativo
Execute o arquivo `main.py` para abrir a interface gráfica do sistema:
```bash
python main.py
```

---

## 📁 Estrutura de Pastas do Projeto

Consulte o documento técnico [Estrutura_do_Projeto.md](docs/Estrutura_do_Projeto.md) para entender a função de cada diretório.
