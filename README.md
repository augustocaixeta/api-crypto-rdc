# Crypto Dashboard

Dashboard web para visualização de dados de criptomoedas em tempo real, consumindo APIs públicas do CoinGecko e CoinMarketCap.

## Sobre o Projeto

Este projeto foi desenvolvido como uma aplicação prática de consumo de APIs REST, implementando um servidor HTTP em Python e uma interface web responsiva. O sistema busca e exibe informações atualizadas sobre criptomoedas, incluindo preços, variações e históricos.

## Funcionalidades

- **Top 10 Criptomoedas**: Ranking das principais moedas por capitalização de mercado
- **Lista Completa**: Visualização de até 100 criptomoedas com filtros
- **Detalhes Individuais**: Informações detalhadas de cada moeda (preço, market cap, variação 24h)
- **Histórico de Preços**: Dados históricos com período configurável (7, 30 ou 90 dias)
- **Interface Responsiva**: Design dark minimalista que funciona em desktop e mobile

## Tecnologias Utilizadas

### Backend
- **Python 3**: Linguagem principal
- **http.server**: Servidor HTTP nativo (sem frameworks externos)
- **urllib**: Requisições HTTP para APIs externas
- **json**: Manipulação de dados

### Frontend
- **HTML5**: Estrutura da página
- **CSS3**: Estilização (dark theme, grid layout)
- **JavaScript (ES6+)**: Lógica de interação e consumo da API
- **Fetch API**: Requisições assíncronas

### APIs Externas
- **CoinGecko API**: Fonte principal (gratuita, sem limite)
- **CoinMarketCap API**: Fonte alternativa (limite de 333 req/dia no plano free)

## Estrutura do Projeto

```
crypto-dashboard/
│
├── script.py           # Servidor HTTP + API Gateway
├── public/
│   └── index.html      # Interface web (HTML + CSS + JS)
│
└── README.md
```

## API Endpoints

O servidor expõe os seguintes endpoints:

| Método | Endpoint | Descrição | Parâmetros |
|--------|----------|-----------|------------|
| GET | `/api/top10` | Top 10 criptomoedas | - |
| GET | `/api/crypto` | Lista de moedas | `?limit=20` |
| GET | `/api/details/:id` | Detalhes de uma moeda | `:id` (ex: bitcoin) |
| GET | `/api/history/:id` | Histórico de preços | `:id`, `?days=7` |

### Exemplos de Uso

```bash
# Top 10 moedas
curl http://localhost:3000/api/top10

# Detalhes do Bitcoin
curl http://localhost:3000/api/details/bitcoin

# Histórico de 7 dias do Ethereum
curl http://localhost:3000/api/history/ethereum?days=7
```

## Arquitetura

### Fluxo de Dados

```
[Navegador] 
    ↓ Requisição HTTP
[script.py - Servidor Python]
    ↓ Requisição às APIs
[CoinGecko / CoinMarketCap]
    ↓ Resposta JSON
[script.py - Processa dados]
    ↓ Resposta JSON
[index.html - Renderiza interface]
```

### Tratamento de Erros

- **Timeout de 10 segundos** para requisições externas
- **Fallback automático**: Se CoinMarketCap falhar, usa CoinGecko
- **Tratamento de conexões abortadas** pelo cliente
- **Mensagens de erro amigáveis** na interface

## Características Técnicas

### Backend (script.py)
- Servidor HTTP puro sem dependências externas
- CORS habilitado para desenvolvimento local
- Timeout configurado para evitar travamentos
- Cache simples em memória (pode ser implementado)

### Frontend (index.html)
- Single Page Application (SPA)
- Async/await para requisições
- Grid CSS responsivo
- Formatação automática de números (K, M, B, T)
- Indicadores visuais de alta/baixa

## Limitações Conhecidas

- Dados não persistem (sem banco de dados)
- Cache básico (dados sempre buscados ao vivo)
- API CoinMarketCap tem limite de requisições
- Servidor single-threaded (uma requisição por vez)
