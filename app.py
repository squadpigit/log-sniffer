import streamlit as st
import sys
from pathlib import Path
import tempfile
import io

# Adiciona o diretório atual ao path para importar o analisador
sys.path.insert(0, str(Path(__file__).parent))
from seo_log_analyzer import SEOLogAnalyzer


# Configuração da página
st.set_page_config(
    page_title="SEO Log Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stDownloadButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">Conversion Log Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Análise avançada de logs de acesso com foco em SEO e identificação de bots</p>', unsafe_allow_html=True)

# Sidebar com informações
with st.sidebar:
    st.header("📊 Sobre a Ferramenta")
    st.markdown("""
    Esta ferramenta analisa arquivos de log de servidores web e gera relatórios detalhados sobre:
    
    **🤖 Bots Identificados:**
    - Googlebot (e variantes)
    - GPTBot & ChatGPT
    - ClaudeBot
    - Bingbot, YandexBot
    - E mais 15+ bots
    
    **📈 Análises Geradas:**
    - Ranking de URLs
    - Frequência de rastreio
    - Dias desde último rastreio
    - URLs com erros (3xx, 4xx, 5xx)
    - Comparativo LLM bots
    - Análise detalhada Googlebot
    """)
    
    st.divider()
    
    st.header("💡 Formatos Suportados")
    st.markdown("""
    - Apache Common Log
    - Apache Combined Log
    - Nginx Access Log
    
    **⚠️ Arquivos Grandes:**
    A ferramenta suporta arquivos de qualquer tamanho. 
    O processamento pode levar alguns minutos para logs com milhões de linhas.
    """)

# Upload do arquivo
st.header("📁 Upload de Arquivos de Log")

uploaded_files = st.file_uploader(
    "Selecione um ou múltiplos arquivos de log (access.log, access.log.1, access.log.2, etc.)",
    type=None,  # Aceita qualquer tipo de arquivo
    accept_multiple_files=True,
    help="📝 Aceita logs rotacionados (.1, .2, .3, etc). Você pode selecionar múltiplos arquivos de uma vez. O processamento mostrará progresso em tempo real."
)

if uploaded_files:
    # Informações dos arquivos
    total_size_mb = sum(f.size for f in uploaded_files) / (1024 * 1024)
    num_files = len(uploaded_files)
    
    if num_files == 1:
        st.info(f"📊 Arquivo carregado: **{uploaded_files[0].name}** ({total_size_mb:.2f} MB)")
    else:
        st.info(f"📊 **{num_files} arquivos** carregados ({total_size_mb:.2f} MB total)")
        with st.expander("Ver lista de arquivos"):
            for f in uploaded_files:
                st.text(f"• {f.name} ({f.size / (1024*1024):.2f} MB)")
    
    # Botão para iniciar análise
    if st.button("🚀 Iniciar Análise", type="primary", use_container_width=True):
        try:
            # Combina múltiplos arquivos em um temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix='.log', mode='w', encoding='utf-8') as tmp_file:
                tmp_file_path = tmp_file.name
                
                # Escreve conteúdo de todos os arquivos
                for i, uploaded_file in enumerate(uploaded_files):
                    content = uploaded_file.getvalue().decode('utf-8', errors='ignore')
                    tmp_file.write(content)
                    if i < len(uploaded_files) - 1:
                        tmp_file.write('\n')  # Adiciona quebra de linha entre arquivos
            
            # Container para progresso
            progress_container = st.container()
            
            with progress_container:
                if num_files == 1:
                    st.subheader(f"⚙️ Processando {uploaded_files[0].name}...")
                else:
                    st.subheader(f"⚙️ Processando {num_files} arquivos...")
                
                # Barra de progresso
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Analisa o arquivo
                status_text.text("Iniciando análise dos logs...")
                progress_bar.progress(10)
                
                analyzer = SEOLogAnalyzer(tmp_file_path)
                
                status_text.text("Parseando linhas do log...")
                progress_bar.progress(30)
                
                analyzer.analyze()
                
                status_text.text("Gerando relatórios...")
                progress_bar.progress(60)
                
                # Gera relatório texto
                report = analyzer.generate_report()
                
                progress_bar.progress(80)
                status_text.text("Gerando CSVs...")
                
                # Gera arquivos em memória
                output_dir = Path(tmp_file_path).parent
                
                # TXT Report
                txt_file = output_dir / 'relatorio_seo.txt'
                with open(txt_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                
                # JSON Report
                json_file = output_dir / 'relatorio_seo.json'
                analyzer.save_json_report(json_file)
                
                # CSVs
                csv_url_ranking = output_dir / 'urls_ranking.csv'
                analyzer.generate_csv_url_ranking(csv_url_ranking)
                
                csv_error_urls = output_dir / 'urls_com_erros.csv'
                analyzer.generate_csv_error_urls(csv_error_urls)
                
                csv_googlebot = output_dir / 'analise_googlebot.csv'
                analyzer.generate_csv_googlebot_analysis(csv_googlebot)
                
                csv_llm = output_dir / 'comparacao_llm_bots.csv'
                analyzer.generate_csv_llm_bots_comparison(csv_llm)
                
                progress_bar.progress(100)
                status_text.text("✅ Análise concluída!")
            
            # Armazena resultados na sessão
            st.session_state['analysis_complete'] = True
            st.session_state['analyzer'] = analyzer
            st.session_state['txt_file'] = txt_file
            st.session_state['json_file'] = json_file
            st.session_state['csv_url_ranking'] = csv_url_ranking
            st.session_state['csv_error_urls'] = csv_error_urls
            st.session_state['csv_googlebot'] = csv_googlebot
            st.session_state['csv_llm'] = csv_llm
            st.session_state['report'] = report
            
            if num_files == 1:
                st.success(f"🎉 Análise de **{uploaded_files[0].name}** completa! Role para baixo para ver os resultados.")
            else:
                st.success(f"🎉 Análise de **{num_files} arquivos** completa! Role para baixo para ver os resultados.")
            
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {str(e)}")
            st.exception(e)

# Exibe resultados se a análise foi completa
if st.session_state.get('analysis_complete', False):
    st.divider()
    
    # Métricas principais
    st.header("📊 Métricas Principais")
    
    analyzer = st.session_state['analyzer']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Requisições", f"{analyzer.parsed_lines:,}")
    
    with col2:
        total_bots = sum(analyzer.bot_visits.values())
        st.metric("Visitas de Bots", f"{total_bots:,}")
    
    with col3:
        st.metric("URLs Únicas", f"{len(analyzer.url_visits):,}")
    
    with col4:
        bot_percentage = (total_bots / analyzer.parsed_lines * 100) if analyzer.parsed_lines > 0 else 0
        st.metric("% Tráfego de Bots", f"{bot_percentage:.1f}%")
    
    st.divider()
    
    # Ranking de Bots
    st.header("🏆 Ranking de Bots")
    
    if analyzer.bot_visits:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔍 Bots de Busca")
            search_bots_data = {bot: count for bot, count in analyzer.bot_visits.items() 
                               if bot in analyzer.search_bots}
            if search_bots_data:
                for bot, count in sorted(search_bots_data.items(), key=lambda x: x[1], reverse=True)[:10]:
                    percentage = (count / total_bots * 100) if total_bots > 0 else 0
                    st.metric(bot, f"{count:,}", f"{percentage:.1f}%")
        
        with col2:
            st.subheader("🤖 LLM Bots")
            llm_bots_data = {bot: count for bot, count in analyzer.bot_visits.items() 
                            if bot in analyzer.llm_bots}
            if llm_bots_data:
                for bot, count in sorted(llm_bots_data.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total_bots * 100) if total_bots > 0 else 0
                    st.metric(bot, f"{count:,}", f"{percentage:.1f}%")
            else:
                st.info("Nenhum LLM bot detectado no log")
    
    st.divider()
    
    # URLs mais acessadas
    st.header("🔗 Top 20 URLs Mais Acessadas")
    
    top_urls_data = []
    for url, count in analyzer.url_visits.most_common(20):
        top_urls_data.append({
            'URL': url,
            'Acessos': count
        })
    
    if top_urls_data:
        st.dataframe(top_urls_data, use_container_width=True)
    
    st.divider()
    
    # Relatório completo
    st.header("📄 Relatório Completo")
    
    with st.expander("Ver Relatório em Texto", expanded=False):
        st.text(st.session_state['report'])
    
    st.divider()
    
    # Downloads
    st.header("📥 Baixar Relatórios")
    
    st.markdown("### Escolha os arquivos para download:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📄 Relatórios Textuais")
        
        # TXT Download
        with open(st.session_state['txt_file'], 'r', encoding='utf-8') as f:
            txt_content = f.read()
        st.download_button(
            label="📄 Download TXT",
            data=txt_content,
            file_name="relatorio_seo.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        # JSON Download
        with open(st.session_state['json_file'], 'r', encoding='utf-8') as f:
            json_content = f.read()
        st.download_button(
            label="📊 Download JSON",
            data=json_content,
            file_name="relatorio_seo.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        st.subheader("📊 CSVs - URLs")
        
        # CSV URL Ranking
        with open(st.session_state['csv_url_ranking'], 'r', encoding='utf-8') as f:
            csv_ranking = f.read()
        st.download_button(
            label="📊 Ranking de URLs",
            data=csv_ranking,
            file_name="urls_ranking.csv",
            mime="text/csv",
            help="URLs com frequência de rastreio e dias desde último acesso",
            use_container_width=True
        )
        
        # CSV Error URLs
        with open(st.session_state['csv_error_urls'], 'r', encoding='utf-8') as f:
            csv_errors = f.read()
        st.download_button(
            label="⚠️ URLs com Erros",
            data=csv_errors,
            file_name="urls_com_erros.csv",
            mime="text/csv",
            help="URLs com status 3xx, 4xx, 5xx para análise SEO",
            use_container_width=True
        )
    
    with col3:
        st.subheader("🤖 CSVs - Bots")
        
        # CSV Googlebot
        with open(st.session_state['csv_googlebot'], 'r', encoding='utf-8') as f:
            csv_google = f.read()
        st.download_button(
            label="🔍 Análise Googlebot",
            data=csv_google,
            file_name="analise_googlebot.csv",
            mime="text/csv",
            help="Análise detalhada do rastreamento do Googlebot",
            use_container_width=True
        )
        
        # CSV LLM Bots
        with open(st.session_state['csv_llm'], 'r', encoding='utf-8') as f:
            csv_llm_content = f.read()
        st.download_button(
            label="🤖 Comparação LLM Bots",
            data=csv_llm_content,
            file_name="comparacao_llm_bots.csv",
            mime="text/csv",
            help="Comparativo entre GPTBot, ClaudeBot e outros LLM bots",
            use_container_width=True
        )
    
    st.divider()
    
    # Análise de Erros
    st.header("⚠️ Análise de Erros SEO")
    
    if analyzer.error_urls:
        error_summary = []
        for status_code in sorted(analyzer.error_urls.keys()):
            count = sum(analyzer.error_urls[status_code].values())
            unique_urls = len(analyzer.error_urls[status_code])
            error_summary.append({
                'Status Code': status_code,
                'Total de Erros': count,
                'URLs Únicas': unique_urls
            })
        
        st.dataframe(error_summary, use_container_width=True)
        
        st.warning("⚠️ Atenção: URLs com erros podem impactar negativamente seu SEO. Baixe o CSV 'URLs com Erros' para análise detalhada.")
    else:
        st.success("✅ Nenhum erro encontrado nos logs!")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>🚀 <strong>SEO Log Analyzer</strong> - Análise profissional de logs para SEO</p>
    <p>Desenvolvido para análise de Googlebot, LLM Bots (GPTBot, ClaudeBot)</p>
</div>
""", unsafe_allow_html=True)
