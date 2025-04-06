# API Configuration User

Esta API permite que usuários de configuração criem, listem e excluam **grupos de idade** usados para validar matrículas de usuários finais.

---

## Autenticação

Todos os endpoints requerem autenticação via HTTP Basic Auth:

```
Authorization: Basic <base64(username:password)>
```

Exemplo (usando `curl`):

```bash
curl -u admin:admin123 http://localhost:8000/api/v1/age-groups/
```

---

## Endpoints

### Criar Grupo de Idade

**POST** `/api/v1/age-groups/`

Cria um novo grupo de idade com idade mínima e máxima. O intervalo não pode sobrepor outros já existentes.

#### Request Body (JSON)

```json
{
  "min_age": 18,
  "max_age": 25
}
```

#### Respostas

- `201 Created` – Grupo criado com sucesso.
- `409 Conflict` – Já existe um grupo com faixa de idade sobreposta.
- `500 Internal Server Error` – Erro interno ao tentar salvar.

#### Exemplo de resposta

```json
{
  "id": "uuid-do-grupo",
  "min_age": 18,
  "max_age": 25
}
```

---

### Listar Grupos de Idade

**GET** `/api/v1/age-groups/`

Lista todos os grupos de idade existentes.

#### Respostas

- `200 OK` – Lista de grupos retornada com sucesso.
- `500 Internal Server Error` – Erro ao buscar os dados.

#### Exemplo de resposta

```json
[
  {
    "id": "uuid-1",
    "min_age": 0,
    "max_age": 17
  },
  {
    "id": "uuid-2",
    "min_age": 18,
    "max_age": 25
  }
]
```

---

### Deletar Grupo de Idade

**DELETE** `/api/v1/age-groups/{id}`

Remove um grupo de idade a partir do seu ID.

#### Respostas

- `204 No Content` – Grupo removido com sucesso.
- `404 Not Found` – Grupo não encontrado.
- `500 Internal Server Error` – Erro interno ao tentar excluir.

---

## Schemas

### `AgeGroupIn`

| Campo   | Tipo | Obrigatório | Descrição              |
|---------|------|-------------|-------------------------|
| min_age | int  | Sim         | Idade mínima do grupo   |
| max_age | int  | Sim         | Idade máxima do grupo   |

---

### `AgeGroupOut`

| Campo   | Tipo | Descrição              |
|---------|------|-------------------------|
| id      | str  | UUID do grupo de idade |
| min_age | int  | Idade mínima           |
| max_age | int  | Idade máxima           |

---

## Regras de Negócio

- Os grupos de idade não podem se sobrepor (ex: um grupo `18-25` e outro `22-30` não são permitidos).
- Apenas usuários autenticados podem acessar a API.
- Os dados são armazenados no **DynamoDB** via **LocalStack**.

---