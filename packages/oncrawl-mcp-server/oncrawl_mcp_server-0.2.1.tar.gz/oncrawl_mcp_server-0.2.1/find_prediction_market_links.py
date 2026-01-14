"""Find all internal links to prediction market articles on sportshandle"""
import os
import json
os.environ['ONCRAWL_API_TOKEN'] = '04Q56SGGKZVXAZFKUR9JC0Q5GZCOAY1VA6O05POX'

from oncrawl_mcp_server.oncrawl_client import OnCrawlClient

client = OnCrawlClient()
CRAWL_ID = '69305abce86f3fc2bde3ab07'

# Step 1: Get schema to see what fields we can search
print("Step 1: Getting schema to find searchable fields...")
schema = client.get_fields(CRAWL_ID, data_type='pages')
text_fields = [f for f in schema.get('fields', [])
               if 'title' in f['name'].lower() or 'h1' in f['name'].lower()]
print(f"Found {len(text_fields)} text fields:")
for f in text_fields[:20]:
    print(f"  - {f['name']} (type: {f.get('type')}, actions: {f.get('actions', [])})")

# Step 2: Search for pages with "prediction market" in title
print("\n\nStep 2: Searching for pages with 'prediction market' in title...")
result = client.search_pages(
    CRAWL_ID,
    fields=['url', 'title', 'h1', 'status_code', 'follow_inlinks'],
    oql={'field': ['title', 'contains', 'prediction market']},
    limit=1000
)
print(f"Found {result.get('count', 0)} pages with 'prediction market' in title")

prediction_pages = result.get('rows', [])
if prediction_pages:
    print("\nPrediction market pages found:")
    for page in prediction_pages[:10]:
        print(f"  - {page['url']}")
        print(f"    Title: {page.get('title', 'N/A')}")
        print(f"    Inlinks: {page.get('follow_inlinks', 'N/A')}")
        print()

# Step 3: Get links schema
print("\n\nStep 3: Getting links schema...")
links_schema = client.get_fields(CRAWL_ID, data_type='links')
link_fields = [f['name'] for f in links_schema.get('fields', [])[:20]]
print(f"Available link fields: {link_fields}")

# Step 4: For each prediction market page, find all internal links pointing to it
if prediction_pages:
    print("\n\nStep 4: Finding all internal links to prediction market pages...")
    all_links = []

    for page in prediction_pages[:10]:  # Limit to first 10 for performance
        target_url = page['url']
        print(f"\nFinding links to: {target_url}")

        # Search for links where target_url matches
        links_result = client.search_links(
            CRAWL_ID,
            fields=['url', 'target_url', 'anchor', 'follow'],
            oql={'field': ['target_url', 'equals', target_url]},
            limit=1000
        )

        links = links_result.get('rows', [])
        print(f"  Found {len(links)} internal links")

        for link in links[:5]:  # Show first 5
            print(f"    From: {link['url']}")
            print(f"    Anchor: {link.get('anchor', 'N/A')}")
            print(f"    Follow: {link.get('follow', 'N/A')}")

        all_links.extend(links)

    # Summary
    print("\n\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total prediction market pages found: {len(prediction_pages)}")
    print(f"Total internal links analyzed: {len(all_links)}")

    # Group by source page
    source_counts = {}
    for link in all_links:
        source = link['url']
        source_counts[source] = source_counts.get(source, 0) + 1

    print(f"\nTop source pages linking to prediction market articles:")
    for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"  {count} links from: {source}")

    # Export results
    output = {
        'prediction_market_pages': prediction_pages,
        'internal_links': all_links,
        'summary': {
            'total_pm_pages': len(prediction_pages),
            'total_links': len(all_links),
            'unique_source_pages': len(source_counts)
        }
    }

    with open('prediction_market_links.json', 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n\nFull results saved to: prediction_market_links.json")
else:
    print("\nNo prediction market pages found. Trying alternative search...")
    # Try searching in URL instead
    result = client.search_pages(
        CRAWL_ID,
        fields=['url', 'title', 'status_code', 'follow_inlinks'],
        oql={'field': ['urlpath', 'contains', 'prediction']},
        limit=1000
    )
    print(f"Pages with 'prediction' in URL: {result.get('count', 0)}")
