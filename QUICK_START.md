# ⚡ **QUICK START - DEPLOY EM 3 MINUTOS**

## **🎯 OPÇÃO MAIS RÁPIDA: MONOREPO**

### **PASSO 1: CRIAR PROJETO (1 min)**
1. **Abra**: https://railway.app
2. **Login** com GitHub  
3. **New Project** → **Deploy from GitHub repo**
4. **Selecione** seu repositório
5. **IMPORTANTE**: **NÃO configure Root Directory** (deixe vazio)

### **PASSO 2: CONFIGURAR VARIÁVEIS (1 min)**
No painel **Variables**, adicione:

**MONGO_URL:**
```
mongodb+srv://andressagomesadm:Nmd742GcPDmkDQUh@cluster0.kcgacfw.mongodb.net/starprint_crm?retryWrites=true&w=majority&appName=Cluster0
```

**DB_NAME:**
```
starprint_crm
```

### **PASSO 3: AGUARDAR DEPLOY (1 min)**
- **Railway.json** configura tudo automaticamente
- **Build**: Instala dependências Python
- **Start**: Inicia FastAPI na porta correta
- **Health Check**: Monitora `/api/health`

### **PASSO 4: TESTAR**
**Copie a URL gerada** e teste:

```
https://sua-url.up.railway.app/api/health
```

**Deve retornar:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-28T...",
  "version": "1.0.0"
}
```

---

## **✅ PRONTO!**

**Backend funcionando em ~3 minutos!** 🎉

**Para frontend, use qualquer hospedagem** (Vercel, Netlify) apontando para:
```
REACT_APP_BACKEND_URL=https://sua-url.up.railway.app
```

---

## **🆘 SE NÃO FUNCIONAR**

1. **Vá em Deployments** → Veja os logs
2. **Tente OPÇÃO 2** (serviços separados) 
3. **Me chame** para ajuda!

**SIMPLE ASSIM! 🚀**