# 📊 SEO Log Analyzer

**Ferramenta profissional de análise de logs de acesso web com foco em métricas de SEO e identificação de bots de busca.**

🎨 **Disponível em 2 versões:**
- 🌐 **Interface Web (Streamlit)** - Fácil de usar, ideal para compartilhar
- 💻 **Linha de Comando (CLI)** - Para automação e processamento em massa

## 🚀 Início Rápido

### Opção 1: Interface Web (Recomendado)

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
streamlit run app.py
```

A aplicação abrirá automaticamente no navegador em `http://localhost:8501`

### Opção 2: Linha de Comando

```bash
# Executar análise
python seo_log_analyzer.py

# Ou especificar arquivo
python seo_log_analyzer.py caminho/para/arquivo.log
```

---

## 🎯 Funcionalidades

### 🌐 Interface Web (Streamlit)
- ✅ Upload de arquivos de log (suporta arquivos grandes até 500MB)
- ✅ Processamento com barra de progresso em tempo real
- ✅ Dashboard interativo com métricas principais
- ✅ Visualização de rankings de bots
- ✅ Download de todos os relatórios (TXT, JSON, CSVs)
- ✅ Análise visual de erros SEO
- ✅ Design responsivo e profissional

### 💻 Análises Geradas

#### 📄 Relatórios Textuais
1. **`relatorio_seo.txt`** - Relatório completo em texto
   - Resumo geral da análise
   - Ranking de bots por número de visitas
   - Detalhes por bot (status codes, URLs visitadas, visitas diárias)
   - Top URLs mais acessadas
   - Distribuição de status codes

2. **`relatorio_seo.json`** - Dados estruturados
   - Todos os dados em formato JSON
   - Ideal para integração com outras ferramentas

#### 📊 Arquivos CSV Especializados

1. **`urls_ranking.csv`** - Ranking Completo de URLs
   - URL
   - Total de rastreios
   - Data do último rastreio
   - **Dias desde o último rastreio**
   - Data do primeiro rastreio
   - Número de bots diferentes que acessaram
   - Contagem por bot (Googlebot, GPTBot, ClaudeBot, Bingbot)

2. **`urls_com_erros.csv`** - URLs com Problemas SEO
   - URLs com status **3xx** (Redirecionamentos)
   - URLs com status **4xx** (Erro do cliente - 404, etc.)
   - URLs com status **5xx** (Erro do servidor)
   - Tipo de erro e impacto SEO
   - Número de ocorrências

3. **`analise_googlebot.csv`** - Análise Detalhada do Googlebot
   - URLs rastreadas pelo Googlebot
   - Frequência de rastreio
   - Dias desde último rastreio
   - Profundidade da URL
   - Status predominante
   - Prioridade de crawl (Alta/Média/Normal/Baixa)

4. **`comparacao_llm_bots.csv`** - Comparativo de LLM Bots
   - Comparação entre **GPTBot** (ChatGPT) e **ClaudeBot** (Claude)
   - URLs indexadas por cada LLM
   - Comparativo com Googlebot
   - Quais LLMs indexaram cada URL

## 🤖 Bots Identificados

### Bots de Busca Principais
- **Googlebot** - Crawler principal do Google
- **Googlebot-Image** - Crawler de imagens do Google
- **Googlebot-News** - Crawler de notícias do Google
- **Googlebot-Video** - Crawler de vídeos do Google
- **Google-InspectionTool** - Ferramenta de inspeção do Google
- **GPTBot** - Crawler do ChatGPT/OpenAI
- **ChatGPT-User** - User agent do ChatGPT
- **Bingbot** - Crawler do Bing/Microsoft
- **YandexBot** - Crawler do Yandex
- **Baiduspider** - Crawler do Baidu

### Outros Bots Relevantes
- **DuckDuckBot** - DuckDuckGo
- **Slurp** - Yahoo
- **Applebot** - Apple
- **ClaudeBot** - Anthropic Claude

### Bots de Redes Sociais
- **facebookexternalhit** - Facebook
- **LinkedInBot** - LinkedIn
- **Twitterbot** - Twitter/X

### Bots de SEO Tools
- **AhrefsBot** - Ahrefs
- **SemrushBot** - Semrush
- **MJ12bot** - Majestic
- **DotBot** - SEO tools
- **PetalBot** - Aspiegel

## 📋 Requisitos

- Python 3.6 ou superior
- Streamlit (para interface web)

```bash
pip install -r requirements.txt
```

## 🔍 Formato de Log Suportado

O script suporta os formatos de log mais comuns:

- **Apache Common Log Format**
- **Apache Combined Log Format**
- **Nginx Access Log Format**

Exemplo de linha de log:
```
192.168.1.1 - - [15/Jan/2026:10:30:45 -0300] "GET /page.html HTTP/1.1" 200 1234 "https://google.com" "Mozilla/5.0 (compatible; Googlebot/2.1)"
```

## 💡 Casos de Uso

### 🎯 Para SEO
- Identifique quais páginas o Googlebot está rastreando
- Descubra URLs órfãs ou esquecidas
- Encontre erros que prejudicam o SEO
- Monitore a frequência de crawl
- Otimize o crawl budget

### 🤖 Para Indexação em LLMs
- Verifique se GPTBot está rastreando seu site
- Compare indexação entre diferentes LLMs
- Identifique oportunidades para aparecer em respostas de IA

### 🔧 Para Manutenção
- Encontre páginas com erro 404 ou 500
- Identifique cadeias de redirecionamento
- Monitore saúde técnica do site

## 📈 Deploy no GitHub

### 1. Criar Repositório

```bash
# Inicializar repositório
git init
git add .
git commit -m "Initial commit: SEO Log Analyzer"

# Adicionar repositório remoto
git remote add origin https://github.com/seu-usuario/seo-log-analyzer.git
git push -u origin main
```

### 2. Deploy no Streamlit Cloud

1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Conecte seu repositório GitHub
3. Selecione:
   - **Main file path**: `app.py`
   - **Python version**: 3.10+
4. Clique em "Deploy"

Sua aplicação estará disponível em: `https://seu-app.streamlit.app`

## 🛠️ Personalização

Para adicionar novos bots, edite o dicionário `bot_patterns` em `seo_log_analyzer.py`:

```python
self.bot_patterns = {
    'NomeDoBot': re.compile(r'pattern', re.IGNORECASE),
    # ... adicione mais bots aqui
}
```

## 📊 Métricas SEO Importantes

- **Frequência de crawl**: Bots visitando frequentemente indica site saudável
- **Coverage**: Quais URLs estão sendo crawleadas
- **Status codes**: 200 é bom, 404/500 são problemas
- **GPTBot**: Importante para indexação em ferramentas de IA
- **Googlebot**: Principal indicador de visibilidade no Google
- **Dias desde último rastreio**: URLs não visitadas há muito tempo podem precisar de atenção

## 🎓 Entendendo os Resultados

### Status Codes
- **2xx**: Sucesso - bot conseguiu acessar o conteúdo
- **3xx**: Redirecionamento - verifique se está correto
- **4xx**: Erro do cliente - página não encontrada ou não autorizada
- **5xx**: Erro do servidor - problemas que precisam correção urgente

### Bots mais Importantes para SEO
1. **Googlebot**: Principal bot para ranking no Google
2. **GPTBot**: Para aparecer em respostas do ChatGPT
3. **ClaudeBot**: Para aparecer em respostas do Claude
4. **Bingbot**: Para Bing e outros produtos Microsoft
5. **Social bots**: Para compartilhamento e preview em redes sociais

### Prioridade de Crawl
- **Alta** (>100 rastreios): URLs muito importantes para os bots
- **Média** (50-100 rastreios): URLs relevantes
- **Normal** (10-50 rastreios): URLs com importância padrão
- **Baixa** (<10 rastreios): URLs com pouco interesse

## 📝 Notas

- O script ignora linhas vazias ou malformadas
- Erros de parse são contabilizados mas não interrompem a análise
- Suporta arquivos de log grandes (testado com milhões de linhas)
- Case-insensitive para identificação de bots
- Interface Streamlit suporta arquivos até 500MB

## 🚀 Arquivos do Projeto

```
LOGSEO/
├── app.py                      # Interface Streamlit
├── seo_log_analyzer.py         # Motor de análise (CLI)
├── requirements.txt            # Dependências
├── executar.bat               # Atalho Windows (CLI)
├── README.md                  # Esta documentação
├── .streamlit/
│   └── config.toml            # Configuração Streamlit
└── .gitignore                 # Git ignore
```

---

**Desenvolvido para análise profissional de SEO e monitoramento de crawlers** 🚀

**Ideal para:** SEO Specialists, Desenvolvedores, Analistas de Dados, Gerentes de Marketing Digital
