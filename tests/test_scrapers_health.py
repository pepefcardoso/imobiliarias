# tests/test_scrapers_health.py
import dataclasses
import logging
import time

from api.main import SCRAPER_REGISTRY
from config.settings import settings
from core.models import SearchQuery

# Reduzimos o nível de log padrão para evitar poluição visual durante o teste
logging.getLogger("scrapers").setLevel(logging.WARNING)
logging.getLogger("infrastructure").setLevel(logging.WARNING)


def run_health_check():
    print("=" * 60)
    print("🔍 Iniciando Health Check dos Scrapers (Busca sem filtros)")
    print("=" * 60)
    
    config_by_name = {cfg.name: cfg for cfg in settings.agencies}
    query = SearchQuery()  # Query vazia (sem filtros)
    results = []

    for name, scraper_cls in SCRAPER_REGISTRY.items():
        if name not in config_by_name:
            print(f"⚠️  {name:<25}: Ignorado (Sem configuração em settings.py)")
            continue
            
        # Forçamos max_pages=1 para não sobrecarregar os sites durante o teste
        original_config = config_by_name[name]
        test_config = dataclasses.replace(original_config, max_pages=1)
        
        scraper = scraper_cls(config=test_config)
        
        print(f"⏳ Testando {name:<22} ... ", end="", flush=True)
        start_time = time.perf_counter()
        
        try:
            properties = scraper.scrape(query)
            elapsed = time.perf_counter() - start_time
            
            if not properties:
                status = "❌ ZERADO"
                error_msg = "Retornou 0 imóveis na primeira página."
            else:
                status = f"✅ OK ({len(properties):02d} imóveis)"
                error_msg = None
                
            results.append({
                "name": name,
                "status": status,
                "elapsed": elapsed,
                "error": error_msg
            })
            print(f"{status} ({elapsed:.2f}s)")
            
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            status = "🚨 ERRO"
            results.append({
                "name": name,
                "status": status,
                "elapsed": elapsed,
                "error": str(e)
            })
            print(f"{status} ({elapsed:.2f}s)")

    # ---------------------------------------------------------
    # Geração do Relatório Final
    # ---------------------------------------------------------
    print("\n" + "=" * 60)
    print("📊 RESUMO DO TESTE")
    print("=" * 60)
    
    erros = [r for r in results if r["status"] == "🚨 ERRO"]
    zerados = [r for r in results if r["status"] == "❌ ZERADO"]
    sucessos = [r for r in results if "✅" in r["status"]]
    
    print(f"Total testados: {len(results)}")
    print(f"Sucessos:       {len(sucessos)}")
    print(f"Zerados:        {len(zerados)}")
    print(f"Com Erro:       {len(erros)}\n")
    
    if zerados:
        print("🛑 SCRAPERS RETORNANDO 0 IMÓVEIS (Possível mudança no HTML/API):")
        for r in zerados:
            print(f"  - {r['name']}")
            
    if erros:
        print("\n🚨 SCRAPERS COM ERRO (Falha de conexão, Timeout ou Crash):")
        for r in erros:
            print(f"  - {r['name']}: {r['error']}")


if __name__ == "__main__":
    run_health_check()