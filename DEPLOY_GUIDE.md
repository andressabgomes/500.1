# 🚀 StarPrint CRM - Guia de Deploy

## 📋 **VISÃO GERAL**
- **Backend**: Railway (FastAPI + MongoDB)
- **Frontend**: Vercel (React + TypeScript)
- **Database**: MongoDB Atlas (recomendado para produção)

---

## **PART 1: DEPLOY DO BACKEND NO RAILWAY** 🚂

### **1.1 Preparação**
✅ **Arquivos já criados:**
- `Procfile` - Comando de inicialização
- `railway.json` - Configuração do Railway
- `backend/requirements.txt` - Dependências otimizadas
- Variáveis de ambiente flexíveis no código

### **1.2 Deploy no Railway**
1. **Acesse**: https://railway.app
2. **Faça login** com GitHub
3. **Clique em "New Project"**
4. **Selecione "Deploy from GitHub repo"**
5. **Conecte este repositório**
6. **Selecione a pasta raiz** (não a pasta backend)

### **1.3 Variáveis de Ambiente no Railway**
Configure as seguintes variáveis:

```bash
# Database (OBRIGATÓRIO)
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=starprint_crm

# Frontend URL (será configurado após deploy do Vercel)
FRONTEND_URL=https://seu-projeto.vercel.app

# Opcional - Railway define automaticamente
PORT=8001
```

### **1.4 MongoDB Atlas Setup**
1. **Acesse**: https://cloud.mongodb.com
2. **Crie um cluster gratuito**
3. **Configure Network Access**: 0.0.0.0/0 (todas as IPs)
4. **Crie um usuário do banco**
5. **Copie a connection string** para MONGO_URL

---

## **PART 2: DEPLOY DO FRONTEND NO VERCEL** ⚡

### **2.1 Preparação**
✅ **Arquivos já criados:**
- `frontend/vercel.json` - Configuração do Vercel
- `frontend/vite.config.ts` - Output para 'dist'

### **2.2 Deploy no Vercel**
1. **Acesse**: https://vercel.com
2. **Faça login** com GitHub
3. **Clique em "New Project"**
4. **Selecione este repositório**
5. **Configure:**
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `yarn build`
   - **Output Directory**: `dist`

### **2.3 Variáveis de Ambiente no Vercel**
Configure:

```bash
# URL do seu backend no Railway
REACT_APP_BACKEND_URL=https://seu-projeto.up.railway.app
```

---

## **PART 3: CONFIGURAÇÃO FINAL** 🔧

### **3.1 Conectar Frontend e Backend**
1. **Após deploy do Railway**, copie a URL gerada
2. **No Vercel**, adicione a URL na variável `REACT_APP_BACKEND_URL`
3. **No Railway**, adicione a URL do Vercel na variável `FRONTEND_URL`
4. **Redeploy ambos os serviços**

### **3.2 Teste da Aplicação**
- **Frontend**: https://seu-projeto.vercel.app
- **Backend API**: https://seu-projeto.up.railway.app/api/health
- **Documentação**: https://seu-projeto.up.railway.app/docs

---

## **📊 CHECKLIST DE DEPLOY**

### **Railway (Backend)**
- [ ] Projeto criado e conectado ao GitHub
- [ ] MONGO_URL configurado (MongoDB Atlas)
- [ ] DB_NAME configurado
- [ ] Build executado com sucesso
- [ ] Health check respondendo: `/api/health`

### **Vercel (Frontend)**
- [ ] Projeto criado com root directory `frontend`
- [ ] REACT_APP_BACKEND_URL configurado
- [ ] Build executado com sucesso
- [ ] Site carregando corretamente

### **Integração**
- [ ] Frontend consegue fazer chamadas para o backend
- [ ] CORS configurado corretamente
- [ ] Database conectado e funcionando
- [ ] Todas as seções do CRM funcionando

---

## **🔍 TROUBLESHOOTING**

### **Problema: CORS Error**
**Solução**: Verifique se a FRONTEND_URL está configurada no Railway

### **Problema: Database Connection Error**
**Solução**: 
1. Verifique MONGO_URL no Railway
2. Confirme IP whitelist no MongoDB Atlas (0.0.0.0/0)
3. Teste conexão manualmente

### **Problema: Build Failed**
**Solução**:
1. Verifique logs no Railway/Vercel
2. Confirme se todas as dependências estão no requirements.txt/package.json
3. Teste build local primeiro

---

## **📝 URLs IMPORTANTES**

Após o deploy, você terá:

- **Frontend**: https://starprint-crm.vercel.app
- **Backend**: https://starprint-crm.up.railway.app
- **API Docs**: https://starprint-crm.up.railway.app/docs
- **Health Check**: https://starprint-crm.up.railway.app/api/health

---

## **🚀 PRÓXIMOS PASSOS**

1. **SSL/HTTPS**: Automático no Vercel e Railway
2. **Custom Domain**: Configurar domínio próprio
3. **Monitoring**: Adicionar logs e métricas
4. **Backup**: Configurar backup automático do MongoDB
5. **CI/CD**: Configurar deploy automático

---

**🎉 Pronto! Seu StarPrint CRM estará rodando em produção!**