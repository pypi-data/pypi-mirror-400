import os
os.environ['ONCRAWL_API_TOKEN'] = '04Q56SGGKZVXAZFKUR9JC0Q5GZCOAY1VA6O05POX'

from oncrawl_mcp_server.oncrawl_client import OnCrawlClient

client = OnCrawlClient()
result = client.export_pages(
    '6952431a3d6fc5e120f87470',
    fields=['url', 'status_code', 'follow_inlinks', 'depth', 'gsc_clicks', 'title', 'urlpath'],
    oql={'field': ['status_code', 'equals', 202]},
    file_type='csv'
)

with open('action_network_soft_404_pages.csv', 'w', encoding='utf-8') as f:
    f.write(result)

print(f'Exported {len(result.splitlines()) - 1} soft 404 pages to action_network_soft_404_pages.csv')
