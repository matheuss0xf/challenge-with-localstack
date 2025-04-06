# Documentação da API Final User

Esta API permite que usuários finais realizem solicitações de matrícula e consultem o status de suas matrículas.

## Endpoints

### Criar Matrícula

**POST** `/api/v1/enrollments/`

Cria uma nova solicitação de matrícula. Se houver um grupo de idade correspondente, o status será `pending`. Caso contrário, o status será `rejected`.

#### Request Body (JSON)

```json
{
  "name": "Teste",
  "cpf": "123.456.789-00",
  "age": 25
}
```

#### Respostas

- `201 Created` – Matrícula criada com sucesso.
- `400 Bad request` – Não foram encontrados grupos de idade compatíveis.
- `500 Internal Server Error` – Erro ao publicar no SQS ou outro erro interno.

#### Exemplo de resposta

```json
{
  "id": "uuid-gerado",
  "name": "Teste",
  "cpf": "123.456.789-00",
  "age": 25,
  "status": "pending",
  "age_group_id": "grupo-de-idade-id"
}
```

---

### Buscar Matrícula por ID

**GET** `/api/v1/enrollments/{id}`

Busca uma matrícula existente pelo ID.

#### Respostas

- `200 OK` – Matrícula encontrada.
- `404 Not Found` – Matrícula não encontrada.

#### Exemplo de resposta

```json
{
  "id": "uuid-da-matricula",
  "name": "Teste",
  "cpf": "123.456.789-00",
  "age": 25,
  "status": "pending",
  "age_group_id": "grupo-de-idade-id"
}
```

---

## 📦 Schemas

### `EnrollmentIn`

| Campo | Tipo  | Obrigatório | Descrição              |
|-------|-------|-------------|-------------------------|
| name  | str   | Sim         | Nome completo do usuário |
| cpf   | str   | Sim         | CPF do usuário           |
| age   | int   | Sim         | Idade do usuário         |

---

### `EnrollmentOut`

| Campo         | Tipo  | Descrição                              |
|---------------|-------|-----------------------------------------|
| id            | str   | UUID da matrícula                      |
| name          | str   | Nome do usuário                        |
| cpf           | str   | CPF do usuário                         |
| age           | int   | Idade do usuário                       |
| status        | str   | `pending`, `approved`, `rejected`      |
| age_group_id  | str   | ID do grupo de idade associado (se houver) |

---

## ⚙️ Regras de Negócio

- Se não existir um grupo de idade compatível, a matrícula será criada com status `rejected`.
- Se existir, será criada com status `pending` e enviada ao SQS para processamento posterior.
- Caso o CPF já exista com status `rejected`, e agora haja grupo de idade válido, a matrícula pode ser reprocessada para `pending`.

---

