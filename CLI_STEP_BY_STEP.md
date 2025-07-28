# ⚡ **RAILWAY CLI - PASSO A PASSO**

## **🔧 PASSO 1: INSTALAR RAILWAY CLI**

### **Se você tem Node.js:**
```bash
npm install -g @railway/cli
```

### **Se não tem Node.js (Linux/Mac):**
```bash
curl -fsSL https://railway.app/install.sh | sh
```

### **Windows (PowerShell):**
```powershell
iwr https://railway.app/install.ps1 | iex
```

**➡️ Execute um dos comandos acima e me diga: "CLI instalado"**

---

## **🔑 PASSO 2: LOGIN COM SEU TOKEN**

```bash
railway login --token c0a7b1a9-54e5-45f8-97fa-f414751924fd
```

**➡️ Copie e cole este comando. Me diga: "Login feito"**

---

## **📁 PASSO 3: NAVEGAR PARA O PROJETO**

```bash
cd /app
```

**➡️ Execute este comando (ou navegue para a pasta do seu projeto)**

---

## **🚀 PASSO 4: CRIAR PROJETO RAILWAY**

```bash
railway create starprint-crm
```

**➡️ Execute e me diga: "Projeto criado"**

---

## **📤 PASSO 5: FAZER DEPLOY**

```bash
railway up
```

**➡️ Este comando vai fazer o deploy usando seu railway.json. Aguarde terminar (~2-3 minutos)**

---

## **⚙️ PASSO 6: CONFIGURAR VARIÁVEIS**

### **Variável 1 - MongoDB:**
```bash
railway variables set MONGO_URL="mongodb+srv://andressagomesadm:Nmd742GcPDmkDQUh@cluster0.kcgacfw.mongodb.net/starprint_crm?retryWrites=true&w=majority&appName=Cluster0"
```

### **Variável 2 - Database Name:**
```bash
railway variables set DB_NAME="starprint_crm"
```

**➡️ Execute os dois comandos acima**

---

## **🌐 PASSO 7: OBTER URL**

```bash
railway domain
```

**➡️ Este comando vai mostrar a URL do seu projeto. COPIE a URL e me envie!**

---

## **✅ PASSO 8: TESTAR**

Substitua `SUA_URL` pela URL que o comando anterior mostrou:

```bash
curl https://SUA_URL/api/health
```

**Se retornar `{"status": "healthy"}` = SUCESSO! 🎉**

---

## **📞 COMUNICAÇÃO COMIGO:**

**Use estas frases para eu saber onde você está:**

- ✅ "CLI instalado"
- ✅ "Login feito" 
- ✅ "Projeto criado"
- ✅ "Deploy concluído"
- ✅ "Variáveis configuradas"
- ✅ "URL obtida: [sua-url]"
- ✅ "Teste funcionou" ou "Teste falhou"

---

## **🆘 SE DER ERRO:**

**Me envie a mensagem de erro exata e eu te ajudo!**

---

## **🚀 COMEÇAR AGORA:**

**1. Execute o PASSO 1 (instalar CLI)**
**2. Me diga "CLI instalado"**
**3. Sigo te guiando!**

**VAMOS LÁ! 💪**