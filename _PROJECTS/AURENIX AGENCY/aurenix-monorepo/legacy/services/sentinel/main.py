import time
import sys
import asyncio
from scanner import KnowledgeScanner
import asyncio
from scanner import KnowledgeScanner
from filter import ContentFilter
from database import ResearchDatabase


async def run_sentinel():
    print("Starting Sentinel Agent Cycle...")
    
    scanner = KnowledgeScanner()
    content_filter = ContentFilter()
    
    # Phase 1: Scan
    raw_intelligence = scanner.run_cycle()
    print(f"Found {len(raw_intelligence)} items.")
    
    # Phase 2: Filter
    high_value_intel = content_filter.filter_candidates(raw_intelligence)
    print(f"Selected {len(high_value_intel)} high-value items.")
    
    # Phase 3: Disseminate (Placeholder)
    for item in high_value_intel:
        print(f"REPORT: {item['title']} (Score: {item['score']}) - {item['link']}")
        await ResearchDatabase.save_item(item)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_sentinel())
