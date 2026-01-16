#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEO Log Analyzer
Analisa logs de acesso web com foco em métricas de SEO
"""

import re
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path
import json


class SEOLogAnalyzer:
    """Analisador de logs com foco em SEO"""
    
    def __init__(self, log_file_path):
        self.log_file_path = Path(log_file_path)
        self.total_lines = 0
        self.parsed_lines = 0
        self.error_lines = 0
        
        # Dicionários para armazenar estatísticas
        self.bot_visits = defaultdict(int)
        self.bot_urls = defaultdict(list)
        self.bot_status_codes = defaultdict(lambda: defaultdict(int))
        
        # Novos rastreamentos para análise avançada
        self.url_last_crawl = {}  # URL -> datetime do último crawl
        self.url_first_crawl = {}  # URL -> datetime do primeiro crawl
        self.url_crawl_by_bot = defaultdict(lambda: defaultdict(int))  # URL -> {bot: count}
        self.bot_url_last_crawl = defaultdict(dict)  # bot -> {URL: datetime}
        self.urls_by_status = defaultdict(list)  # status_code -> [URLs]
        self.url_status_history = defaultdict(list)  # URL -> [(datetime, status)]
        
        # Separação de LLM bots
        self.llm_bots = ['GPTBot', 'ChatGPT-User', 'ClaudeBot']
        self.search_bots = ['Googlebot', 'Googlebot-Image', 'Googlebot-News', 
                           'Googlebot-Video', 'Google-InspectionTool', 'Bingbot', 
                           'YandexBot', 'Baiduspider', 'DuckDuckBot', 'Applebot']
        
        # Métricas SEO avançadas
        self.googlebot_crawl_depth = defaultdict(int)  # profundidade de URL
        self.error_urls = defaultdict(lambda: defaultdict(int))  # status_code -> {URL: count}
        self.bot_daily_visits = defaultdict(lambda: defaultdict(int))
        self.url_visits = Counter()
        self.status_codes = Counter()
        self.user_agents = Counter()
        
        # Padrões de bots conhecidos
        self.bot_patterns = {
            'Googlebot': re.compile(r'Googlebot', re.IGNORECASE),
            'Googlebot-Image': re.compile(r'Googlebot-Image', re.IGNORECASE),
            'Googlebot-News': re.compile(r'Googlebot-News', re.IGNORECASE),
            'Googlebot-Video': re.compile(r'Googlebot-Video', re.IGNORECASE),
            'Google-InspectionTool': re.compile(r'Google-InspectionTool', re.IGNORECASE),
            'GPTBot': re.compile(r'GPTBot', re.IGNORECASE),
            'ChatGPT-User': re.compile(r'ChatGPT-User', re.IGNORECASE),
            'Bingbot': re.compile(r'bingbot', re.IGNORECASE),
            'YandexBot': re.compile(r'YandexBot', re.IGNORECASE),
            'Baiduspider': re.compile(r'Baiduspider', re.IGNORECASE),
            'DuckDuckBot': re.compile(r'DuckDuckBot', re.IGNORECASE),
            'Slurp': re.compile(r'Slurp', re.IGNORECASE),  # Yahoo
            'facebookexternalhit': re.compile(r'facebookexternalhit', re.IGNORECASE),
            'LinkedInBot': re.compile(r'LinkedInBot', re.IGNORECASE),
            'Twitterbot': re.compile(r'Twitterbot', re.IGNORECASE),
            'Applebot': re.compile(r'Applebot', re.IGNORECASE),
            'AhrefsBot': re.compile(r'AhrefsBot', re.IGNORECASE),
            'SemrushBot': re.compile(r'SemrushBot', re.IGNORECASE),
            'MJ12bot': re.compile(r'MJ12bot', re.IGNORECASE),
            'DotBot': re.compile(r'DotBot', re.IGNORECASE),
            'PetalBot': re.compile(r'PetalBot', re.IGNORECASE),
            'ClaudeBot': re.compile(r'ClaudeBot', re.IGNORECASE),
        }
        
        # Padrão para parsear linha de log (Apache/Nginx Common/Combined format)
        self.log_pattern = re.compile(
            r'(?P<ip>[\d\.]+)\s+'
            r'(?P<identity>-|\S+)\s+'
            r'(?P<user>-|\S+)\s+'
            r'\[(?P<time>[^\]]+)\]\s+'
            r'"(?P<request>[^"]*)"\s+'
            r'(?P<status>\d{3})\s+'
            r'(?P<size>-|\d+)\s*'
            r'(?:"(?P<referer>[^"]*)")?\s*'
            r'(?:"(?P<user_agent>[^"]*)")?'
        )
    
    def identify_bot(self, user_agent):
        """Identifica o tipo de bot baseado no User-Agent"""
        if not user_agent or user_agent == '-':
            return None
        
        for bot_name, pattern in self.bot_patterns.items():
            if pattern.search(user_agent):
                return bot_name
        return None
    
    def parse_log_line(self, line):
        """Faz parse de uma linha do log"""
        match = self.log_pattern.match(line)
        if not match:
            return None
        
        data = match.groupdict()
        
        # Extrai URL da requisição
        request_parts = data.get('request', '').split()
        if len(request_parts) >= 2:
            data['method'] = request_parts[0]
            data['url'] = request_parts[1]
        else:
            data['method'] = ''
            data['url'] = ''
        
        # Parse da data
        try:
            # Formato: 10/Oct/2000:13:55:36 -0700
            time_str = data['time'].split()[0]
            data['datetime'] = datetime.strptime(time_str, '%d/%b/%Y:%H:%M:%S')
            data['date'] = data['datetime'].strftime('%Y-%m-%d')
        except:
            data['datetime'] = None
            data['date'] = None
        
        return data
    
    def analyze(self):
        """Analisa o arquivo de log"""
        print(f"🔍 Analisando arquivo: {self.log_file_path}")
        print(f"{'='*80}")
        
        if not self.log_file_path.exists():
            print(f"❌ Erro: Arquivo não encontrado!")
            return
        
        with open(self.log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                self.total_lines += 1
                
                # Mostra progresso
                if line_num % 10000 == 0:
                    print(f"   Processando linha {line_num:,}...")
                
                line = line.strip()
                if not line:
                    continue
                
                # Parse da linha
                data = self.parse_log_line(line)
                if not data:
                    self.error_lines += 1
                    continue
                
                self.parsed_lines += 1
                
                # Extrai informações
                user_agent = data.get('user_agent', '')
                url = data.get('url', '')
                status = data.get('status', '')
                date = data.get('date', '')
                
                # Identifica bot
                bot_name = self.identify_bot(user_agent)
                datetime_obj = data.get('datetime')
                
                # Estatísticas gerais
                self.url_visits[url] += 1
                self.status_codes[status] += 1
                if user_agent:
                    self.user_agents[user_agent] += 1
                
                # Rastreamento de último crawl por URL
                if datetime_obj:
                    if url not in self.url_last_crawl or datetime_obj > self.url_last_crawl[url]:
                        self.url_last_crawl[url] = datetime_obj
                    if url not in self.url_first_crawl:
                        self.url_first_crawl[url] = datetime_obj
                    
                    # Histórico de status por URL
                    self.url_status_history[url].append((datetime_obj, status))
                
                # URLs por código de status
                if status and url:
                    if status.startswith(('3', '4', '5')):
                        if url not in self.urls_by_status[status]:
                            self.urls_by_status[status].append(url)
                        self.error_urls[status][url] += 1
                
                # Estatísticas de bots
                if bot_name:
                    self.bot_visits[bot_name] += 1
                    self.bot_urls[bot_name].append(url)
                    self.bot_status_codes[bot_name][status] += 1
                    
                    # Rastreamento por bot
                    if url:
                        self.url_crawl_by_bot[url][bot_name] += 1
                        
                        if datetime_obj:
                            if url not in self.bot_url_last_crawl[bot_name] or \
                               datetime_obj > self.bot_url_last_crawl[bot_name][url]:
                                self.bot_url_last_crawl[bot_name][url] = datetime_obj
                    
                    if date:
                        self.bot_daily_visits[bot_name][date] += 1
                    
                    # Análise específica do Googlebot
                    if bot_name.startswith('Googlebot') and url:
                        depth = url.count('/')
                        self.googlebot_crawl_depth[depth] += 1
        
        print(f"\n✅ Análise concluída!")
        print(f"   Total de linhas: {self.total_lines:,}")
        print(f"   Linhas parseadas: {self.parsed_lines:,}")
        print(f"   Linhas com erro: {self.error_lines:,}")
    
    def generate_report(self):
        """Gera relatório completo"""
        report = []
        report.append("=" * 80)
        report.append("📊 RELATÓRIO DE ANÁLISE SEO - ACCESS LOG")
        report.append("=" * 80)
        report.append("")
        
        # Resumo
        report.append("📈 RESUMO GERAL")
        report.append("-" * 80)
        report.append(f"Total de requisições analisadas: {self.parsed_lines:,}")
        report.append(f"Total de URLs únicas: {len(self.url_visits):,}")
        report.append(f"Total de User-Agents únicos: {len(self.user_agents):,}")
        report.append("")
        
        # Análise de Bots
        report.append("🤖 ANÁLISE DE BOTS DE BUSCA E CRAWLERS")
        report.append("-" * 80)
        
        if self.bot_visits:
            total_bot_visits = sum(self.bot_visits.values())
            report.append(f"Total de visitas de bots: {total_bot_visits:,}")
            report.append(f"Porcentagem do tráfego total: {(total_bot_visits/self.parsed_lines)*100:.2f}%")
            report.append("")
            
            # Ranking de bots
            report.append("🏆 RANKING DE BOTS (por número de visitas)")
            report.append("-" * 80)
            for i, (bot_name, count) in enumerate(sorted(self.bot_visits.items(), 
                                                         key=lambda x: x[1], 
                                                         reverse=True), 1):
                percentage = (count / total_bot_visits) * 100
                report.append(f"{i:2d}. {bot_name:30s}: {count:8,} visitas ({percentage:6.2f}%)")
            report.append("")
            
            # Detalhes por bot
            report.append("🔍 DETALHES POR BOT")
            report.append("-" * 80)
            for bot_name in sorted(self.bot_visits.keys(), 
                                  key=lambda x: self.bot_visits[x], 
                                  reverse=True):
                report.append(f"\n{bot_name}")
                report.append(f"  Total de visitas: {self.bot_visits[bot_name]:,}")
                
                # Status codes
                report.append(f"  Status codes:")
                for status, count in sorted(self.bot_status_codes[bot_name].items()):
                    report.append(f"    {status}: {count:,}")
                
                # URLs mais visitadas por este bot
                url_counter = Counter(self.bot_urls[bot_name])
                top_urls = url_counter.most_common(10)
                if top_urls:
                    report.append(f"  Top 10 URLs visitadas:")
                    for url, count in top_urls:
                        url_display = url[:70] + "..." if len(url) > 70 else url
                        report.append(f"    [{count:4d}x] {url_display}")
                
                # Visitas por dia (últimos 30 dias)
                if bot_name in self.bot_daily_visits:
                    daily = self.bot_daily_visits[bot_name]
                    if daily:
                        sorted_dates = sorted(daily.keys(), reverse=True)[:30]
                        if sorted_dates:
                            report.append(f"  Visitas por dia (últimos 30 dias):")
                            for date in sorted_dates:
                                report.append(f"    {date}: {daily[date]:,}")
        else:
            report.append("Nenhum bot identificado no log.")
        
        report.append("")
        
        # URLs mais acessadas
        report.append("🔗 TOP 20 URLs MAIS ACESSADAS")
        report.append("-" * 80)
        for i, (url, count) in enumerate(self.url_visits.most_common(20), 1):
            url_display = url[:65] + "..." if len(url) > 65 else url
            report.append(f"{i:2d}. [{count:6,}x] {url_display}")
        report.append("")
        
        # Status codes
        report.append("📊 DISTRIBUIÇÃO DE STATUS CODES")
        report.append("-" * 80)
        for status, count in sorted(self.status_codes.items()):
            percentage = (count / self.parsed_lines) * 100
            report.append(f"{status}: {count:8,} ({percentage:6.2f}%)")
        report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_json_report(self, output_file):
        """Salva relatório em formato JSON para análise adicional"""
        data = {
            'summary': {
                'total_lines': self.total_lines,
                'parsed_lines': self.parsed_lines,
                'error_lines': self.error_lines,
                'unique_urls': len(self.url_visits),
                'unique_user_agents': len(self.user_agents)
            },
            'bots': {
                bot_name: {
                    'total_visits': count,
                    'status_codes': dict(self.bot_status_codes[bot_name]),
                    'daily_visits': dict(self.bot_daily_visits[bot_name]),
                    'top_urls': dict(Counter(self.bot_urls[bot_name]).most_common(50))
                }
                for bot_name, count in self.bot_visits.items()
            },
            'top_urls': dict(self.url_visits.most_common(100)),
            'status_codes': dict(self.status_codes)
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Relatório JSON salvo em: {output_file}")
    
    def generate_csv_url_ranking(self, output_file):
        """Gera CSV com ranking de URLs por frequência de rastreio"""
        import csv
        from datetime import datetime as dt
        
        now = dt.now()
        
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'URL', 
                'Total_Rastreios', 
                'Ultimo_Rastreio', 
                'Dias_Desde_Ultimo', 
                'Primeiro_Rastreio',
                'Bots_Diferentes',
                'Googlebot',
                'GPTBot',
                'ClaudeBot',
                'Bingbot'
            ])
            
            for url, count in self.url_visits.most_common():
                last_crawl = self.url_last_crawl.get(url)
                first_crawl = self.url_first_crawl.get(url)
                
                if last_crawl:
                    days_since = (now - last_crawl).days
                    last_crawl_str = last_crawl.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    days_since = 'N/A'
                    last_crawl_str = 'N/A'
                
                first_crawl_str = first_crawl.strftime('%Y-%m-%d %H:%M:%S') if first_crawl else 'N/A'
                
                bots_count = len(self.url_crawl_by_bot.get(url, {}))
                googlebot_count = self.url_crawl_by_bot.get(url, {}).get('Googlebot', 0)
                gptbot_count = self.url_crawl_by_bot.get(url, {}).get('GPTBot', 0)
                claudebot_count = self.url_crawl_by_bot.get(url, {}).get('ClaudeBot', 0)
                bingbot_count = self.url_crawl_by_bot.get(url, {}).get('Bingbot', 0)
                
                writer.writerow([
                    url,
                    count,
                    last_crawl_str,
                    days_since,
                    first_crawl_str,
                    bots_count,
                    googlebot_count,
                    gptbot_count,
                    claudebot_count,
                    bingbot_count
                ])
        
        print(f"💾 CSV de ranking de URLs salvo em: {output_file}")
    
    def generate_csv_error_urls(self, output_file):
        """Gera CSV com URLs que retornaram erros (3xx, 4xx, 5xx)"""
        import csv
        
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'URL',
                'Status_Code',
                'Tipo_Erro',
                'Ocorrencias',
                'Ultimo_Status',
                'Impacto_SEO'
            ])
            
            for status_code in sorted(self.error_urls.keys()):
                if status_code.startswith('3'):
                    tipo = 'Redirecionamento'
                    impacto = 'Médio - Verificar cadeia de redirects'
                elif status_code.startswith('4'):
                    tipo = 'Erro Cliente'
                    impacto = 'Alto - Página não encontrada ou não autorizada'
                elif status_code.startswith('5'):
                    tipo = 'Erro Servidor'
                    impacto = 'Crítico - Problema no servidor'
                else:
                    tipo = 'Outro'
                    impacto = 'Verificar'
                
                for url, count in sorted(self.error_urls[status_code].items(), 
                                        key=lambda x: x[1], reverse=True):
                    # Pega o último status conhecido dessa URL
                    history = self.url_status_history.get(url, [])
                    last_status = history[-1][1] if history else status_code
                    
                    writer.writerow([
                        url,
                        status_code,
                        tipo,
                        count,
                        last_status,
                        impacto
                    ])
        
        print(f"💾 CSV de URLs com erros salvo em: {output_file}")
    
    def generate_csv_googlebot_analysis(self, output_file):
        """Gera CSV com análise detalhada do Googlebot"""
        import csv
        
        googlebot_urls = defaultdict(int)
        for bot_name in ['Googlebot', 'Googlebot-Image', 'Googlebot-News', 
                        'Googlebot-Video', 'Google-InspectionTool']:
            if bot_name in self.bot_urls:
                for url in self.bot_urls[bot_name]:
                    googlebot_urls[url] += 1
        
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'URL',
                'Rastreios_Googlebot',
                'Ultimo_Rastreio',
                'Dias_Desde_Ultimo',
                'Profundidade_URL',
                'Status_Predominante',
                'Crawl_Priority'
            ])
            
            from datetime import datetime as dt
            now = dt.now()
            
            for url, count in sorted(googlebot_urls.items(), key=lambda x: x[1], reverse=True):
                last_crawl = None
                for bot in ['Googlebot', 'Googlebot-Image', 'Googlebot-News', 
                           'Googlebot-Video', 'Google-InspectionTool']:
                    if bot in self.bot_url_last_crawl and url in self.bot_url_last_crawl[bot]:
                        bot_last = self.bot_url_last_crawl[bot][url]
                        if last_crawl is None or bot_last > last_crawl:
                            last_crawl = bot_last
                
                if last_crawl:
                    days_since = (now - last_crawl).days
                    last_crawl_str = last_crawl.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    days_since = 'N/A'
                    last_crawl_str = 'N/A'
                
                depth = url.count('/')
                
                # Status predominante
                history = self.url_status_history.get(url, [])
                if history:
                    status_counts = Counter([s[1] for s in history])
                    predominant_status = status_counts.most_common(1)[0][0]
                else:
                    predominant_status = 'N/A'
                
                # Prioridade de crawl (baseado em frequência)
                if count > 100:
                    priority = 'Alta'
                elif count > 50:
                    priority = 'Média'
                elif count > 10:
                    priority = 'Normal'
                else:
                    priority = 'Baixa'
                
                writer.writerow([
                    url,
                    count,
                    last_crawl_str,
                    days_since,
                    depth,
                    predominant_status,
                    priority
                ])
        
        print(f"💾 CSV de análise do Googlebot salvo em: {output_file}")
    
    def generate_csv_llm_bots_comparison(self, output_file):
        """Gera CSV comparativo entre bots de LLM"""
        import csv
        
        # Coleta todas as URLs acessadas por LLM bots
        all_llm_urls = set()
        for bot in self.llm_bots:
            if bot in self.bot_urls:
                all_llm_urls.update(self.bot_urls[bot])
        
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'URL',
                'GPTBot',
                'ClaudeBot',
                'ChatGPT-User',
                'Total_LLM_Bots',
                'Googlebot_Comparativo',
                'Indexado_Por'
            ])
            
            for url in sorted(all_llm_urls):
                gptbot = self.url_crawl_by_bot.get(url, {}).get('GPTBot', 0)
                claudebot = self.url_crawl_by_bot.get(url, {}).get('ClaudeBot', 0)
                chatgpt = self.url_crawl_by_bot.get(url, {}).get('ChatGPT-User', 0)
                total_llm = gptbot + claudebot + chatgpt
                
                googlebot = self.url_crawl_by_bot.get(url, {}).get('Googlebot', 0)
                
                indexed_by = []
                if gptbot > 0:
                    indexed_by.append('GPTBot')
                if claudebot > 0:
                    indexed_by.append('ClaudeBot')
                if chatgpt > 0:
                    indexed_by.append('ChatGPT')
                
                writer.writerow([
                    url,
                    gptbot,
                    claudebot,
                    chatgpt,
                    total_llm,
                    googlebot,
                    ', '.join(indexed_by)
                ])
        
        print(f"💾 CSV de comparação de LLM bots salvo em: {output_file}")


def main():
    """Função principal"""
    import sys
    
    # Define caminho do arquivo de log
    log_file = Path(__file__).parent / 'acess.log'
    
    # Permite passar arquivo como argumento
    if len(sys.argv) > 1:
        log_file = Path(sys.argv[1])
    
    # Cria analisador
    analyzer = SEOLogAnalyzer(log_file)
    
    # Analisa o log
    analyzer.analyze()
    
    # Gera e exibe relatório
    print("\n")
    report = analyzer.generate_report()
    print(report)
    
    # Salva relatórios
    output_dir = log_file.parent
    
    # Relatório em texto
    txt_report_file = output_dir / 'relatorio_seo.txt'
    with open(txt_report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n💾 Relatório em texto salvo em: {txt_report_file}")
    
    # Relatório em JSON
    json_report_file = output_dir / 'relatorio_seo.json'
    analyzer.save_json_report(json_report_file)
    
    # CSVs
    print("\n📊 Gerando arquivos CSV...")
    
    csv_url_ranking = output_dir / 'urls_ranking.csv'
    analyzer.generate_csv_url_ranking(csv_url_ranking)
    
    csv_error_urls = output_dir / 'urls_com_erros.csv'
    analyzer.generate_csv_error_urls(csv_error_urls)
    
    csv_googlebot = output_dir / 'analise_googlebot.csv'
    analyzer.generate_csv_googlebot_analysis(csv_googlebot)
    
    csv_llm = output_dir / 'comparacao_llm_bots.csv'
    analyzer.generate_csv_llm_bots_comparison(csv_llm)
    
    print("\n✅ Análise completa!")
    print(f"\n📁 Arquivos gerados:")
    print(f"   📄 {txt_report_file}")
    print(f"   📄 {json_report_file}")
    print(f"   📊 {csv_url_ranking}")
    print(f"   📊 {csv_error_urls}")
    print(f"   📊 {csv_googlebot}")
    print(f"   📊 {csv_llm}")


if __name__ == '__main__':
    main()
