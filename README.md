# LEBLOCA Reviews

Aplicação web para centralizar o gerenciamento de avaliações de múltiplas contas do Google Business Profile. Inclui autenticação com JWT, cadastro de contas do Google, sincronização simulada de avaliações e painel moderno para visualização das métricas principais.

## Principais funcionalidades

- Cadastro e login de usuários com senha criptografada.
- CRUD completo das contas do Google vinculadas ao usuário logado.
- Armazenamento das configurações individuais de cada conta (JSON).
- Sincronização simulada das avaliações com estrutura pronta para conectar à API oficial do Google.
- Painel responsivo com visual moderno (TailwindCSS + Glassmorphism) para acompanhar avaliações.

## Tecnologias

- Python 3.11+
- Flask 3
- SQLite (via SQLAlchemy)
- JWT para autenticação de APIs
- TailwindCSS (CDN) para o frontend

## Configuração do ambiente

1. **Criar e ativar o ambiente virtual**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Instalar dependências**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variáveis de ambiente (opcional)**

   ```bash
   export SECRET_KEY="sua-chave-secreta"
   export JWT_SECRET_KEY="outra-chave-secreta"
   export DATABASE_URL="sqlite:///instance/app.db"
   ```

4. **Executar a aplicação**

   ```bash
   flask --app wsgi run --debug
   ```

   O comando acima cria o banco automaticamente (SQLite) e inicia o servidor em `http://127.0.0.1:5000`.

## Estrutura do código

- `app/__init__.py`: factory da aplicação e registro dos blueprints.
- `app/models.py`: modelos do banco (usuários, contas Google e avaliações).
- `app/auth.py`: endpoints de autenticação (registro/login).
- `app/google_accounts.py`: endpoints para CRUD das contas e sincronização das avaliações.
- `app/google_reviews.py`: integração simulada com a API do Google, pronta para ser adaptada para a API real.
- `app/templates/index.html`: página inicial com o dashboard moderno.
- `app/static/js/app.js`: lógica do frontend (auth, CRUD e renderização).
- `app/static/css/style.css`: estilos complementares.

## Próximos passos

- Implementar a chamada real à API Google Business Profile dentro de `GoogleReviewsClient`.
- Salvar tokens de atualização de forma segura (por exemplo, Vault/KMS).
- Adicionar notificações e respostas automáticas às avaliações.
- Criar testes automatizados para os endpoints principais.
