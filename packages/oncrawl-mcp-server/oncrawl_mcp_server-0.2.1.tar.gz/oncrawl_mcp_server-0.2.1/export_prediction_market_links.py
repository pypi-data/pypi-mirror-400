"""
Export all internal links pointing to prediction market content on actionnetwork
Outputs CSV with: Source URL, Target URL, Anchor Text
"""
import os
import csv
os.environ['ONCRAWL_API_TOKEN'] = '04Q56SGGKZVXAZFKUR9JC0Q5GZCOAY1VA6O05POX'

from oncrawl_mcp_server.oncrawl_client import OnCrawlClient

# Initialize client
client = OnCrawlClient()

# Workspace ID (based on previous scripts)
WORKSPACE_ID = '5c015889451c956baf7ab7a9'

print("Step 1: Finding Action Network project...")
projects = client.list_projects(WORKSPACE_ID, limit=100)
project_list = projects.get('projects', [])

# Find actionnetwork project
actionnetwork_project = None
for proj in project_list:
    domain = proj.get('domain', '').lower()
    if 'actionnetwork' in domain or 'action network' in domain.replace('.', ' '):
        actionnetwork_project = proj
        print(f"Found: {proj.get('name')} - {domain}")
        break

if not actionnetwork_project:
    print("\nNo Action Network project found. Available projects:")
    for proj in project_list[:20]:
        print(f"  - {proj.get('name')} ({proj.get('domain')})")
    exit(1)

# Get project details for latest crawl
# The project ID might be in different fields, let's check
project_id = actionnetwork_project.get('project_id') or actionnetwork_project.get('_id') or actionnetwork_project.get('id')
if not project_id:
    print(f"Available keys in project: {list(actionnetwork_project.keys())}")
    print(f"Project data: {actionnetwork_project}")
    exit(1)

print(f"\nStep 2: Getting latest crawl for project {project_id}...")
project_details = client.get_project(project_id)
project_data = project_details.get('project', project_details)

crawl_id = project_data.get('last_crawl_id')
print(f"Latest crawl ID: {crawl_id}")
print(f"Domain: {project_data.get('domain')}")

# Step 3: Search for prediction market pages
print("\nStep 3: Searching for prediction market pages...")
# Try searching in title first - NOTE: API returns 'urls' not 'rows'
prediction_pages = []
search_attempts = [
    ('title', 'prediction market'),
    ('title', 'betting market'),
    ('title', 'futures'),
    ('title', 'prop bet'),
    ('title', 'prop pick'),
    ('title', 'odds market'),
    ('url', 'prediction'),
    ('url', 'futures'),
]

for field_name, search_term in search_attempts:
    result = client.search_pages(
        crawl_id,
        fields=['url', 'title', 'h1', 'status_code', 'follow_inlinks'],
        oql={'field': [field_name, 'contains', search_term]},
        limit=10000
    )
    found = result.get('urls', [])  # API returns 'urls' not 'rows'
    if found:
        print(f"  Found {len(found)} pages with '{search_term}' in {field_name}")
        # Add to list, avoiding duplicates
        for page in found:
            if page['url'] not in [p['url'] for p in prediction_pages]:
                prediction_pages.append(page)

if not prediction_pages:
    print("\nNo prediction market pages found with initial searches.")
    print("Trying URL pattern search...")

    # Get the schema to see what fields are available
    schema = client.get_fields(crawl_id, data_type='pages')

    # Try searching in URL patterns
    url_patterns = [
        'prediction',
        'betting-odds',
        'odds-market',
        'betting-market',
        'futures',
        'prop-bet',
        'betting-line'
    ]

    for pattern in url_patterns:
        result = client.search_pages(
            crawl_id,
            fields=['url', 'title', 'h1', 'status_code', 'follow_inlinks'],
            oql={'field': ['url', 'contains', pattern]},
            limit=1000
        )
        found = result.get('rows', [])
        if found:
            print(f"  Found {len(found)} pages with '{pattern}' in URL")
            for page in found:
                if page['url'] not in [p['url'] for p in prediction_pages]:
                    prediction_pages.append(page)

    if not prediction_pages:
        print("\nStill no results. Let me sample pages to understand the site structure...")
        result = client.search_pages(
            crawl_id,
            fields=['url', 'title', 'h1'],
            oql=None,  # Get all pages
            limit=100
        )
        print(f"\nAPI Response keys: {result.keys()}")
        print(f"Total count: {result.get('count', 'N/A')}")
        print(f"Number of rows returned: {len(result.get('rows', []))}")

        if result.get('rows'):
            print(f"\nSample pages from site:")
            for page in result.get('rows', [])[:20]:
                print(f"  - {page['url']}")
                print(f"    Title: {page.get('title', 'N/A')}")

            print("\nPlease check the URLs above and let me know what pattern identifies prediction market pages.")
        else:
            print("\nNo rows returned from API. This might indicate:")
            print("  1. The crawl is empty or still processing")
            print("  2. There's an issue with the field names")
            print("  3. The API requires different parameters")
            print(f"\nFull API response: {result}")
        exit(1)

print(f"\nTotal unique prediction market pages found: {len(prediction_pages)}")
print("\nSample pages:")
for page in prediction_pages[:5]:
    print(f"  - {page['url']}")
    print(f"    Title: {page.get('title', 'N/A')}")
    print(f"    Inlinks: {page.get('follow_inlinks', 'N/A')}")

# Step 4: For each prediction market page, find all internal links pointing to it
print("\nStep 4: Finding all internal links pointing to prediction market pages...")
all_links = []

for i, page in enumerate(prediction_pages, 1):
    target_url = page['url']
    print(f"\n[{i}/{len(prediction_pages)}] Finding links to: {target_url}")

    # Search for links where target_url matches
    links_result = client.search_links(
        crawl_id,
        fields=['url', 'target_url', 'anchor', 'follow'],
        oql={'field': ['target_url', 'equals', target_url]},
        limit=10000  # Get all links to this page
    )

    links = links_result.get('rows', [])
    print(f"  Found {len(links)} internal links")

    # Add target page info to each link
    for link in links:
        link['target_title'] = page.get('title', '')
        link['target_h1'] = page.get('h1', '')

    all_links.extend(links)

# Step 5: Export to CSV
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Total prediction market pages: {len(prediction_pages)}")
print(f"Total internal links found: {len(all_links)}")

# Group by source page
source_counts = {}
for link in all_links:
    source = link['url']
    source_counts[source] = source_counts.get(source, 0) + 1

print(f"Unique source pages: {len(source_counts)}")

if source_counts:
    print(f"\nTop 10 source pages linking to prediction market content:")
    for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {count} links from: {source}")

# Export to CSV
csv_filename = 'actionnetwork_prediction_market_links.csv'
print(f"\n\nExporting to {csv_filename}...")

with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['source_url', 'target_url', 'anchor_text', 'is_followed', 'target_title', 'target_h1']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for link in all_links:
        writer.writerow({
            'source_url': link['url'],
            'target_url': link['target_url'],
            'anchor_text': link.get('anchor', ''),
            'is_followed': link.get('follow', ''),
            'target_title': link.get('target_title', ''),
            'target_h1': link.get('target_h1', '')
        })

print(f"✓ Export complete! {len(all_links)} links written to {csv_filename}")
print("\nColumns:")
print("  - source_url: Where the link is located")
print("  - target_url: Where the link points to (prediction market page)")
print("  - anchor_text: The clickable text of the link")
print("  - is_followed: Whether the link is followed (for SEO)")
print("  - target_title: Title of the target page")
print("  - target_h1: H1 of the target page")
