# 🎯 **DEPLOY DIRETO COM SEU TOKEN RAILWAY**

## **🔑 TOKEN IDENTIFICADO: c0a7b1a9-54e5-45f8-97fa-f414751924fd**

---

# **🚀 OPÇÃO 1: DEPLOY VIA CLI (MAIS RÁPIDO)**

## **PASSO 1: INSTALAR RAILWAY CLI**
```bash
# No seu terminal local:
npm install -g @railway/cli

# Ou se preferir:
curl -fsSL https://railway.app/install.sh | sh
```

## **PASSO 2: FAZER LOGIN COM SEU TOKEN**
```bash
railway login --token c0a7b1a9-54e5-45f8-97fa-f414751924fd
```

## **PASSO 3: DEPLOY BACKEND**
```bash
# Navegar para o projeto
cd /app

# Fazer deploy do backend
railway deploy --service backend --start "cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT"

# Adicionar variáveis
railway variables set MONGO_URL="mongodb+srv://andressagomesadm:Nmd742GcPDmkDQUh@cluster0.kcgacfw.mongodb.net/starprint_crm?retryWrites=true&w=majority&appName=Cluster0"
railway variables set DB_NAME="starprint_crm"
```

---

# **🚀 OPÇÃO 2: DEPLOY VIA WEB (RECOMENDADO)**

## **ACESSO DIRETO COM SEU TOKEN:**
1. **Abra**: https://railway.app/dashboard
2. **Já deve estar logado** com seu token
3. **Siga as instruções** do arquivo `DEPLOY_ASSISTIDO.md`

---

# **🎯 CONFIGURAÇÕES PRONTAS PARA SEU PROJETO:**

## **BACKEND SERVICE:**
```json
{
  "name": "starprint-backend",
  "source": {
    "type": "github",
    "repo": "seu-repo",
    "branch": "main"
  },
  "rootDirectory": "backend",
  "buildCommand": "pip install -r requirements.txt",
  "startCommand": "uvicorn server:app --host 0.0.0.0 --port $PORT",
  "variables": {
    "MONGO_URL": "mongodb+srv://andressagomesadm:Nmd742GcPDmkDQUh@cluster0.kcgacfw.mongodb.net/starprint_crm?retryWrites=true&w=majority&appName=Cluster0",
    "DB_NAME": "starprint_crm"
  }
}
```

## **FRONTEND SERVICE:**
```json
{
  "name": "starprint-frontend", 
  "source": {
    "type": "github",
    "repo": "seu-repo",
    "branch": "main"
  },
  "rootDirectory": "frontend",
  "buildCommand": "yarn install && yarn build",
  "startCommand": "yarn preview --host 0.0.0.0 --port $PORT",
  "variables": {
    "REACT_APP_BACKEND_URL": "https://SEU_BACKEND_URL.up.railway.app"
  }
}
```

---

# **⚡ DEPLOY AUTOMÁTICO**

Se você me der acesso ao seu GitHub repo (público), posso te dar comandos diretos para usar com seu token!

## **COMANDOS RAILWAY CLI PRONTOS:**

```bash
# 1. Login
railway login --token c0a7b1a9-54e5-45f8-97fa-f414751924fd

# 2. Criar projeto
railway create starprint-crm

# 3. Deploy backend
railway service create backend
railway link [PROJECT_ID] --service backend
railway up --service backend --start "cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT"

# 4. Configurar variáveis backend
railway variables set MONGO_URL="mongodb+srv://andressagomesadm:Nmd742GcPDmkDQUh@cluster0.kcgacfw.mongodb.net/starprint_crm?retryWrites=true&w=majority&appName=Cluster0" --service backend
railway variables set DB_NAME="starprint_crm" --service backend

# 5. Deploy frontend
railway service create frontend
railway link [PROJECT_ID] --service frontend  
railway up --service frontend --start "cd frontend && yarn preview --host 0.0.0.0 --port $PORT"

# 6. Configurar variável frontend
railway variables set REACT_APP_BACKEND_URL="[BACKEND_URL]" --service frontend
```

---

# **🎯 QUAL OPÇÃO VOCÊ PREFERE?**

## **A) CLI (Terminal)** - Mais automático
- Instalar Railway CLI
- Usar comandos prontos
- Deploy em ~2 minutos

## **B) Web (Navegador)** - Mais visual  
- Usar dashboard Railway
- Seguir guia assistido
- Deploy em ~3 minutos

**Me diga qual prefere e eu te guio!** 🚀

---

# **📞 PRÓXIMO PASSO:**

**Digite uma dessas opções:**
- "Quero usar CLI" 
- "Quero usar Web"
- "Faça pelo mais rápido"

**E eu te dou as instruções específicas!** 💪