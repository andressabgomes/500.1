#!/bin/bash

# 🚀 DEPLOY AUTOMÁTICO STARPRINT CRM
# Criado especificamente para andressagomes/500.1

echo "🚀 Iniciando deploy automático do StarPrint CRM..."
echo "📂 Repositório: andressagomes/500.1"
echo "🔑 Usando token Railway fornecido"
echo ""

# Verificar se Railway CLI está instalado
if ! command -v railway &> /dev/null; then
    echo "⚠️  Railway CLI não encontrado. Instalando..."
    npm install -g @railway/cli
    echo "✅ Railway CLI instalado!"
fi

# Login no Railway
echo "🔑 Fazendo login no Railway..."
railway login --token c0a7b1a9-54e5-45f8-97fa-f414751924fd

if [ $? -eq 0 ]; then
    echo "✅ Login no Railway realizado com sucesso!"
else
    echo "❌ Erro no login do Railway"
    exit 1
fi

# Verificar se já existe um projeto
echo "📋 Verificando projetos existentes..."
railway projects

# Criar novo projeto
echo "📁 Criando projeto StarPrint CRM..."
railway create starprint-crm-prod

if [ $? -eq 0 ]; then
    echo "✅ Projeto criado com sucesso!"
else
    echo "⚠️  Projeto pode já existir, continuando..."
fi

# Conectar ao repositório GitHub
echo "🔗 Conectando ao repositório GitHub..."
railway connect andressagomes/500.1

# Fazer deploy inicial
echo "🚀 Iniciando deploy..."
railway up

# Configurar variáveis de ambiente
echo "⚙️  Configurando variáveis de ambiente..."

# MongoDB
railway variables set MONGO_URL="mongodb+srv://andressagomesadm:Nmd742GcPDmkDQUh@cluster0.kcgacfw.mongodb.net/starprint_crm?retryWrites=true&w=majority&appName=Cluster0"
railway variables set DB_NAME="starprint_crm"

echo "✅ Variáveis configuradas!"

# Aguardar deploy
echo "⏳ Aguardando conclusão do deploy..."
sleep 30

# Obter URL do projeto
echo "🌐 Obtendo URL do projeto..."
PROJECT_URL=$(railway domain)

if [ -n "$PROJECT_URL" ]; then
    echo "🎉 DEPLOY CONCLUÍDO COM SUCESSO!"
    echo ""
    echo "📊 INFORMAÇÕES DO PROJETO:"
    echo "🌐 URL: $PROJECT_URL"
    echo "🔍 Health Check: $PROJECT_URL/api/health"
    echo "📚 API Docs: $PROJECT_URL/docs"
    echo ""
    
    # Testar endpoint
    echo "🧪 Testando endpoint de saúde..."
    HEALTH_RESPONSE=$(curl -s "$PROJECT_URL/api/health" || echo "erro")
    
    if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
        echo "✅ TESTE PASSOU! Backend funcionando perfeitamente!"
        echo "📋 Resposta: $HEALTH_RESPONSE"
    else
        echo "⚠️  Endpoint de saúde não respondeu como esperado"
        echo "📋 Resposta: $HEALTH_RESPONSE"
        echo "🔍 Verificando logs..."
        railway logs
    fi
    
else
    echo "⚠️  Não foi possível obter a URL do projeto"
    echo "🔍 Verificando status..."
    railway status
fi

echo ""
echo "🎯 COMANDOS ÚTEIS:"
echo "📊 Ver status: railway status"
echo "📋 Ver logs: railway logs"
echo "🌐 Ver domínio: railway domain"
echo "⚙️  Ver variáveis: railway variables"
echo ""
echo "🎉 SCRIPT CONCLUÍDO!"