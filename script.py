from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import urllib.parse
from datetime import datetime
import socket

# Configurações
COINMARKETCAP_API_KEY = '3f640653-8b8f-4bf3-acad-5d5b20c6e1dc'
COINMARKETCAP_URL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
COINGECKO_BASE = 'https://api.coingecko.com/api/v3'

# Timeout 10 segundos
socket.setdefaulttimeout(10)

class CryptoAPIHandler(BaseHTTPRequestHandler):
    
    def _set_headers(self, status=200, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers()
    
    def do_GET(self):
        # Parse URL
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query = urllib.parse.parse_qs(parsed_path.query)
        
        try:
            # Servir HTML
            if path == '/' or path == '/index.html':
                try:
                    self._set_headers(200, 'text/html')
                    with open('public/index.html', 'rb') as f:
                        self.wfile.write(f.read())
                except (ConnectionAbortedError, BrokenPipeError):
                    pass  # Cliente desconectou, ignorar
                return

            elif path == '/api/top10':
                print('📊 Buscando top 10 criptomoedas...')
                data = self.get_top10_coingecko()
                self._set_headers(200)
                try:
                    self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
                except (ConnectionAbortedError, BrokenPipeError):
                    pass  # Cliente desconectou, ignorar

            elif path == '/api/crypto':
                print('💰 Buscando lista de criptomoedas...')
                limit = query.get('limit', ['100'])[0]
                data = self.get_crypto_list(limit)
                self._set_headers(200)
                try:
                    self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
                except (ConnectionAbortedError, BrokenPipeError):
                    pass

            elif path.startswith('/api/details/'):
                crypto_id = path.split('/')[-1]
                print(f'🔍 Buscando detalhes de {crypto_id}...')
                data = self.get_crypto_details(crypto_id)
                self._set_headers(200)
                try:
                    self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
                except (ConnectionAbortedError, BrokenPipeError):
                    pass

            elif path.startswith('/api/history/'):
                crypto_id = path.split('/')[-1]
                days = query.get('days', ['30'])[0]
                print(f'📈 Buscando histórico de {crypto_id}...')
                data = self.get_history(crypto_id, days)
                self._set_headers(200)
                try:
                    self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
                except (ConnectionAbortedError, BrokenPipeError):
                    pass
            
            else:
                self._set_headers(404)
                try:
                    self.wfile.write(json.dumps({'error': 'Rota não encontrada'}).encode())
                except (ConnectionAbortedError, BrokenPipeError):
                    pass
        
        except (ConnectionAbortedError, BrokenPipeError):
            pass
        except Exception as e:
            print(f'Erro: {str(e)}')
            try:
                self._set_headers(500)
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': str(e)
                }).encode())
            except (ConnectionAbortedError, BrokenPipeError):
                pass
    
    def get_top10_coingecko(self):
        """Busca top 10 criptomoedas usando CoinGecko (GRÁTIS)"""
        try:
            url = f'{COINGECKO_BASE}/coins/markets'
            params = urllib.parse.urlencode({
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 10,
                'page': 1,
                'sparkline': 'false'
            })
            
            req = urllib.request.Request(f'{url}?{params}')
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
        except Exception as e:
            print(f'Erro ao buscar CoinGecko: {e}')
            # Retornar dados de exemplo se falhar
            return {'success': False, 'error': str(e), 'data': []}
        
        result = []
        for crypto in data:
            result.append({
                'id': crypto['id'],
                'name': crypto['name'],
                'symbol': crypto['symbol'].upper(),
                'image': crypto['image'],
                'current_price': crypto['current_price'],
                'market_cap': crypto['market_cap'],
                'price_change_24h': crypto.get('price_change_percentage_24h', 0),
                'rank': crypto['market_cap_rank']
            })
        
        return {'success': True, 'data': result}
    
    def get_crypto_list(self, limit):
        """Busca lista de cryptos do CoinMarketCap"""
        try:
            url = f'{COINMARKETCAP_URL}?limit={limit}&convert=USD'
            
            req = urllib.request.Request(url)
            req.add_header('X-CMC_PRO_API_KEY', COINMARKETCAP_API_KEY)
            req.add_header('Accept', 'application/json')
            
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
            
            result = []
            for crypto in data['data']:
                result.append({
                    'id': crypto['id'],
                    'name': crypto['name'],
                    'symbol': crypto['symbol'],
                    'slug': crypto['slug'],
                    'price': f"{crypto['quote']['USD']['price']:.2f}",
                    'change_24h': f"{crypto['quote']['USD']['percent_change_24h']:.2f}",
                    'change_7d': f"{crypto['quote']['USD'].get('percent_change_7d', 0):.2f}",
                    'market_cap': f"{crypto['quote']['USD']['market_cap']:.0f}",
                    'volume_24h': f"{crypto['quote']['USD']['volume_24h']:.0f}",
                    'rank': crypto['cmc_rank']
                })
            
            return {
                'success': True,
                'data': result,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            # Se falhar, usar CoinGecko como fallback
            print(f'CoinMarketCap falhou, usando CoinGecko: {e}')
            return self.get_top10_coingecko()
    
    def get_crypto_details(self, crypto_id):
        """Busca detalhes de uma cripto no CoinGecko"""
        url = f'{COINGECKO_BASE}/coins/{crypto_id}'
        params = urllib.parse.urlencode({
            'localization': 'false',
            'tickers': 'false',
            'community_data': 'false',
            'developer_data': 'false'
        })
        
        req = urllib.request.Request(f'{url}?{params}')
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
        
        return {
            'success': True,
            'data': {
                'id': data['id'],
                'name': data['name'],
                'symbol': data['symbol'].upper(),
                'description': data['description']['en'][:500] + '...',
                'image': data['image']['large'],
                'current_price': data['market_data']['current_price']['usd'],
                'market_cap': data['market_data']['market_cap']['usd'],
                'high_24h': data['market_data']['high_24h']['usd'],
                'low_24h': data['market_data']['low_24h']['usd'],
                'price_change_24h': data['market_data']['price_change_percentage_24h']
            }
        }
    
    def get_history(self, crypto_id, days):
        url = f'{COINGECKO_BASE}/coins/{crypto_id}/market_chart'
        params = urllib.parse.urlencode({
            'vs_currency': 'usd',
            'days': days
        })
        
        req = urllib.request.Request(f'{url}?{params}')
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
        
        result = []
        for timestamp, price in data['prices']:
            result.append({
                'timestamp': datetime.fromtimestamp(timestamp/1000).isoformat(),
                'price': f'{price:.2f}'
            })
        
        return {
            'success': True,
            'data': result,
            'crypto': crypto_id,
            'days': days
        }
    
    def log_message(self, format, *args):
        """Log personalizado"""
        print(f"{self.address_string()} - {format % args}")


def run_server(port=3000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, CryptoAPIHandler)

    print(f'\nServidor rodando em: http://localhost:{port}')
    print('\nEndpoints disponíveis:')
    print(f'  • GET  http://localhost:{port}/api/crypto')
    print(f'  • GET  http://localhost:{port}/api/top10')
    print(f'  • GET  http://localhost:{port}/api/history/bitcoin')
    print(f'  • GET  http://localhost:{port}/api/details/bitcoin')
    print('\nAPIs Usadas:')
    print(f'  • CoinMarketCap (com limite)')
    print(f'  • CoinGecko (GRÁTIS, sem limite!)')

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n\nServiço encerrado!')
        httpd.server_close()

if __name__ == '__main__':
    run_server()