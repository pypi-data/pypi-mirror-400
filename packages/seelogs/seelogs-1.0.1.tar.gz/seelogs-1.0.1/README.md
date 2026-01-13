# 🧠 SeeLogs Python Client

SeeLogs é uma biblioteca leve e eficiente para captura, estruturação e envio de logs de aplicações Python. Oferece suporte a:

- Envio **imediato ou em lotes**
- Detecção automática de métricas do sistema (CPU, memória, uptime, etc.)
- Logs **críticos**, **informativos**, **debug** e **erros**
- Integração fácil com sistemas de monitoramento
- Geolocalização e IPs de origem para rastreio
- Detecção opcional de **infraestrutura** (sistema, host, arquitetura, etc.)

[![Conheça o See Logs - 7 dias grátis](https://img.shields.io/badge/🚀_Conhecer_See_Logs-7_dias_GRÁTIS-brightgreen?style=for-the-badge&logo=rocket)](https://seelogs.com)

---

⚡ **Alertas automáticos na versão PRO:**
- 🖥️ **Alertas na Tela** - Notificações em tempo real no dashboard
- 📧 **Alertas por Email** - Envio imediato para responsáveis técnicos
- 🔗 **Alertas por Webhook** - Integração com sistemas externos
- 📱 **Alertas por Telegram** - Mensagens individuais ou em grupos

### 🎯 Códigos de Evento Personalizados

É possível enviar códigos de evento (`event_code`) para rastreamento específico e alertas customizados:

```ts
logger.info("Falha de conexao", { event_code: "fail_connect_to_rabbit" });
```

⚡ **Personalização de alertas na versão PRO:**
- 🎨 Alertas customizados por level debug, info, warn, error, critical // opcional
- 🎨 Alertas customizados por `event_code` // opcional
- 🖥️ Notificações segmentadas na tela
- 📧 Alertas de email
- 🔗 Webhooks específicos por tipo de evento
- 📱 Grupos do Telegram direcionados por categoria

🧾 Saída no servidor:
```json
{
  "level": "info",
  "service": "api",
  "message": "Erro no banco de dados",
  "event_code": "fail_connect_to_rabbit"
}
```

---
## 🧹 Finalização Segura

O See Logs garante que nenhum log seja perdido ao encerrar a aplicação:

## 🚀 Instalação

```bash
pip install seelogs