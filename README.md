# Challenge - Enrollment System

Este projeto simula um sistema de matrículas com **FastAPI**, **DynamoDB**, **SQS** e **Lambda** em ambiente local via **LocalStack**.

## Estrutura do Projeto

```
.
├── configuration-user     # API para configurar faixas etárias
├── final-user             # API para usuários finais solicitarem matrícula
├── lambda                 # Função Lambda para processar filas do SQS
├── scripts                # Scripts de setup (ex: criação de recursos no LocalStack)
├── docker-compose.yml     # Orquestra LocalStack e ambiente de desenvolvimento
└── README.md               # Este arquivo
```

## Tecnologias

- **FastAPI** – APIs rápidas e assíncronas
- **Pydantic** – Validação de dados
- **Task** – Gerenciamento de tarefas
- **LocalStack** – Emulação local dos serviços AWS
- **DynamoDB** – Banco de dados NoSQL para armazenar dados de matrícula e configuração
- **SQS** – Fila para comunicação entre APIs
- **Lambda** – Consumidor de fila que processa e aprova matrículas
- **Pytest** – Testes de integração com mocks

## Como Rodar

### Pré-requisitos

- Docker
- Python 3.12+
- Poetry (para gerenciar dependências)

### Subir o ambiente

```bash
docker-compose up -d
```

Após subir, as APIs estarão disponíveis nos seguintes endpoints:

| Serviço | URL Local             | Dentro do Docker              | Acessar o container      |
|-------|-----------------------|-------------------------------|--------------------------|
| FinalUser API  | http://localhost:8081 | http://finaluser:8081         | docker exec -it finaluser /bin/sh |
| ConfigUser API   | http://localhost:8082 | http://configurationuser:8082 | docker exec -it configurationuser /bin/sh           |
| LocalStack   | http://localhost:4566 | http://localstack:4566        | docker exec -it localstack /bin/bash         |


### Rodar as APIs localmente

```bash
# Terminal 1
cd configuration-user
poetry shell
task run

# Terminal 2
cd final-user
poetry shell
task run
```

## Testes

Para executar os testes:

```bash
# Configuration User
cd configuration-user
poetry shell
task test

# Final User
cd final-user
poetry shell
task test
```

## Fluxo da Aplicação

1. O usuário final solicita uma matrícula via API (`final-user`).
2. A matrícula é validada e enviada como mensagem para o **SQS** com status `pending`.
3. A função **Lambda** consome as mensagens, verifica se há grupo etário correspondente e atualiza o status para `approved` ou `rejected` no **DynamoDB**.
4. O usuário pode consultar o status posteriormente pela API.

## Endpoints

### Configuration User (porta 8082)

- `POST /api/v1/age-groups/` – Cadastrar nova faixa etária
- `GET /api/v1/age-groups/` – Listar faixas etárias
- `DELETE /api/v1/age-groups/{id}` – Excluir faixa etária

### Final User (porta 8081)

- `POST /api/v1/enrollments/` – Criar uma nova matrícula
- `GET /api/v1/enrollments/{id}` – Verificar status da matrícula

---

_Desenvolvido para um desafio técnico._
