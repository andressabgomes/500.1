# 🔧 **TROUBLESHOOTING - SOLUÇÕES RÁPIDAS**

## **❌ PROBLEMAS COMUNS E SOLUÇÕES**

### **🚂 BACKEND ISSUES**

#### **Erro: "Module not found"**
**Solução:**
1. Vá em Variables do backend
2. Adicione: `PYTHONPATH=/app/backend`
3. Redeploy

#### **Erro: "Database connection failed"**
**Solução:**
1. Verifique se `MONGO_URL` está correto
2. Confirme se MongoDB Atlas permite IPs: 0.0.0.0/0
3. Teste a connection string em: https://mongodbcompass.com

#### **Erro: "Port binding failed"**
**Solução:**
1. Railway define PORT automaticamente
2. NÃO adicione variável PORT manualmente
3. Nixpacks configura automaticamente

---

### **⚡ FRONTEND ISSUES**

#### **Erro: "Build failed"**
**Solução:**
1. Verifique se Root Directory = `frontend`
2. Confirme se `REACT_APP_BACKEND_URL` está correto
3. Redeploy

#### **Erro: "White screen"**
**Solução:**
1. Abra DevTools (F12)
2. Veja erros no Console
3. Geralmente é problema de variável `REACT_APP_BACKEND_URL`

#### **Erro: "API calls failing"**
**Solução:**
1. Confirme se backend está funcionando
2. Teste: `https://SEU_BACKEND.up.railway.app/api/health`
3. Verifique CORS no backend (variável `FRONTEND_URL`)

---

### **🔗 INTEGRATION ISSUES**

#### **Erro: CORS**
**Solução:**
1. Confirme variável `FRONTEND_URL` no backend
2. Valor deve ser a URL completa do frontend
3. Aguarde redeploy automático

#### **Erro: 502 Bad Gateway**
**Solução:**
1. Backend provavelmente crashed
2. Vá em Deployments → Logs
3. Veja o erro específico
4. Geralmente problema de variáveis

---

## **🆘 SOLUÇÕES EXTREMAS**

### **RESET COMPLETO**
Se nada funcionar:
1. Delete os dois serviços
2. Comece novamente com o guia
3. Total: 7 minutos novo

### **REDEPLOY FORÇADO**
1. Vá em Deployments
2. Clique nos 3 pontinhos (...)
3. "Redeploy"
4. Aguarde

### **VERIFICAR LOGS DETALHADOS**
1. Clique no serviço
2. Aba "Logs"
3. Veja erros em tempo real
4. Compartilhe comigo se precisar

---

## **📞 CONTATO RÁPIDO**

**Se precisar de ajuda:**
1. **Me diga qual erro** está aparecendo
2. **Copie os logs** do Railway
3. **Informe qual passo** parou de funcionar

**Vamos resolver rapidinho! 💪**