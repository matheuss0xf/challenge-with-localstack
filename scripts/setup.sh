#!/bin/bash

if [ ! -f .env ]; then
    echo "❌ ERRO: Arquivo .env não encontrado!"
    exit 1
fi
set -a
source .env
set +a

for var in AGE_GROUPS_TABLE ENROLLMENTS_TABLE QUEUE_NAME ZIP_FILE LAMBDA_NAME LAMBDA_HANDLER; do
    if [ -z "${!var}" ]; then
        echo "❌ ERRO: Variável $var não definida no .env!"
        exit 1
    fi
done

if ! command -v zip &> /dev/null; then
    echo "❌ ERRO: O comando 'zip' não está instalado. Instale com 'sudo apt install zip' ou 'sudo yum install zip'."
    exit 1
fi

# Criar tabela AGE_GROUPS
if aws dynamodb list-tables --endpoint-url="$AWS_ENDPOINT_URL" --output json | grep -q "\"$AGE_GROUPS_TABLE\""; then
    echo "⚠️  Tabela '$AGE_GROUPS_TABLE' já existe."
else
    echo "🔹 Criando tabela DynamoDB: $AGE_GROUPS_TABLE..."
    aws dynamodb create-table \
        --table-name "$AGE_GROUPS_TABLE" \
        --attribute-definitions AttributeName=id,AttributeType=S \
        --key-schema AttributeName=id,KeyType=HASH \
        --billing-mode PAY_PER_REQUEST \
        --endpoint-url="$AWS_ENDPOINT_URL" || { echo "❌ Falha ao criar tabela $AGE_GROUPS_TABLE"; exit 1; }
    aws dynamodb wait table-exists --table-name "$AGE_GROUPS_TABLE" --endpoint-url="$AWS_ENDPOINT_URL"
fi

if aws dynamodb list-tables --endpoint-url="$AWS_ENDPOINT_URL" --output json | grep -q "\"$ENROLLMENTS_TABLE\""; then
    echo "⚠️  Tabela '$ENROLLMENTS_TABLE' já existe."
else
    echo "🔹 Criando tabela DynamoDB: $ENROLLMENTS_TABLE..."
    aws dynamodb create-table \
        --table-name "$ENROLLMENTS_TABLE" \
        --attribute-definitions AttributeName=id,AttributeType=S AttributeName=cpf,AttributeType=S \
        --key-schema AttributeName=id,KeyType=HASH \
        --global-secondary-indexes "[
            {
                \"IndexName\": \"CpfIndex\",
                \"KeySchema\": [
                    {\"AttributeName\": \"cpf\", \"KeyType\": \"HASH\"}
                ],
                \"Projection\": {\"ProjectionType\": \"ALL\"}
            }
        ]" \
        --billing-mode PAY_PER_REQUEST \
        --endpoint-url="$AWS_ENDPOINT_URL" || { echo "❌ Falha ao criar tabela $ENROLLMENTS_TABLE"; exit 1; }
    aws dynamodb wait table-exists --table-name "$ENROLLMENTS_TABLE" --endpoint-url="$AWS_ENDPOINT_URL"
fi

if aws sqs list-queues --endpoint-url="$AWS_ENDPOINT_URL" --output json | grep -q "$QUEUE_NAME"; then
    echo "⚠️  Fila '$QUEUE_NAME' já existe."
else
    echo "🔹 Criando fila SQS..."
    aws sqs create-queue --queue-name "$QUEUE_NAME" --endpoint-url="$AWS_ENDPOINT_URL" || { echo "❌ Falha ao criar fila $QUEUE_NAME"; exit 1; }
fi

QUEUE_URL=$(aws sqs get-queue-url --queue-name "$QUEUE_NAME" --endpoint-url="$AWS_ENDPOINT_URL" --output text) || { echo "❌ Falha ao obter URL da fila"; exit 1; }
echo $QUEUE_URL

echo "🔹 Criando pacote Lambda..."
ZIP_FILE="/scripts/lambda_function.zip"
[ -f "$ZIP_FILE" ] && rm -f "$ZIP_FILE"
if [ -f "/lambda/consumer_enrollment.py" ]; then
    zip -j "$ZIP_FILE" /lambda/consumer_enrollment.py || { echo "❌ Falha ao criar ZIP"; exit 1; }
else
    echo "❌ ERRO: Arquivo 'consumer_enrollment.py' não encontrado!"
    exit 1
fi

if aws lambda get-function --function-name "$LAMBDA_NAME" --endpoint-url="$AWS_ENDPOINT_URL" > /dev/null 2>&1; then
    echo "⚠️  Lambda '$LAMBDA_NAME' já existe."
else
    echo "🔹 Criando função Lambda..."
    aws lambda create-function \
        --function-name "$LAMBDA_NAME" \
        --runtime python3.12 \
        --role "arn:aws:iam::$AWS_ACCOUNT_ID:role/execution_role" \
        --handler "$LAMBDA_HANDLER" \
        --package-type Zip \
        --zip-file "fileb://$ZIP_FILE" \
        --timeout 2 \
        --memory-size 256 \
        --environment "Variables={AWS_ENDPOINT_URL=$AWS_ENDPOINT_URL,AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION,SQS_ENROLLMENT_QUEUE_URL=$QUEUE_URL,DB_ENROLLMENTS_TABLE_NAME=$ENROLLMENTS_TABLE}" \
        --endpoint-url="$AWS_ENDPOINT_URL" || { echo "❌ Falha ao criar Lambda"; exit 1; }
    sleep 2
fi

echo "🔹 Configurando concorrência na Lambda..."
aws lambda put-function-concurrency \
    --function-name "$LAMBDA_NAME" \
    --reserved-concurrent-executions 5 \
    --endpoint-url="$AWS_ENDPOINT_URL" || { echo "❌ Falha ao configurar concorrência"; exit 1; }

if aws lambda get-policy --function-name "$LAMBDA_NAME" --endpoint-url="$AWS_ENDPOINT_URL" 2>/dev/null | grep -q "AllowSQSInvoke"; then
    echo "⚠️  Permissão já existe."
else
    echo "🔹 Criando permissão para Lambda consumir mensagens do SQS..."
    aws lambda add-permission \
        --function-name "$LAMBDA_NAME" \
        --statement-id AllowSQSInvoke \
        --action "lambda:InvokeFunction" \
        --principal "sqs.amazonaws.com" \
        --source-arn "arn:aws:sqs:$AWS_DEFAULT_REGION:$AWS_ACCOUNT_ID:$QUEUE_NAME" \
        --endpoint-url="$AWS_ENDPOINT_URL" || { echo "❌ Falha ao adicionar permissão"; exit 1; }
fi

if aws lambda list-event-source-mappings --function-name "$LAMBDA_NAME" --endpoint-url="$AWS_ENDPOINT_URL" --output json | grep -q "$QUEUE_NAME"; then
    echo "⚠️  Evento já associado."
else
    echo "🔹 Associando SQS à Lambda..."
    aws lambda create-event-source-mapping \
        --function-name "$LAMBDA_NAME" \
        --event-source-arn "arn:aws:sqs:$AWS_DEFAULT_REGION:$AWS_ACCOUNT_ID:$QUEUE_NAME" \
        --batch-size 10 \
        --endpoint-url="$AWS_ENDPOINT_URL" || { echo "❌ Falha ao associar SQS à Lambda"; exit 1; }
fi


echo "✅ Setup concluído no LocalStack!"