# Scrape

Types:

```python
from scrapengine.types import ScrapeCreateResponse, ScrapeGetStatusResponse
```

Methods:

- <code title="post /scrape">client.scrape.<a href="./src/scrapengine/resources/scrape.py">create</a>(\*\*<a href="src/scrapengine/types/scrape_create_params.py">params</a>) -> <a href="./src/scrapengine/types/scrape_create_response.py">ScrapeCreateResponse</a></code>
- <code title="get /scrape/{jobId}">client.scrape.<a href="./src/scrapengine/resources/scrape.py">get_status</a>(job_id) -> <a href="./src/scrapengine/types/scrape_get_status_response.py">ScrapeGetStatusResponse</a></code>

# Google

Types:

```python
from scrapengine.types import GoogleSearchResponse
```

Methods:

- <code title="get /google/search">client.google.<a href="./src/scrapengine/resources/google.py">search</a>(\*\*<a href="src/scrapengine/types/google_search_params.py">params</a>) -> <a href="./src/scrapengine/types/google_search_response.py">GoogleSearchResponse</a></code>

# Bing

Types:

```python
from scrapengine.types import BingSearchResponse
```

Methods:

- <code title="get /bing/search">client.bing.<a href="./src/scrapengine/resources/bing.py">search</a>(\*\*<a href="src/scrapengine/types/bing_search_params.py">params</a>) -> <a href="./src/scrapengine/types/bing_search_response.py">BingSearchResponse</a></code>

# Amazon

Types:

```python
from scrapengine.types import AmazonSearchResponse
```

Methods:

- <code title="get /amazon/search">client.amazon.<a href="./src/scrapengine/resources/amazon.py">search</a>(\*\*<a href="src/scrapengine/types/amazon_search_params.py">params</a>) -> <a href="./src/scrapengine/types/amazon_search_response.py">AmazonSearchResponse</a></code>

# Lazada

Types:

```python
from scrapengine.types import LazadaSearchResponse
```

Methods:

- <code title="get /lazada/search">client.lazada.<a href="./src/scrapengine/resources/lazada.py">search</a>(\*\*<a href="src/scrapengine/types/lazada_search_params.py">params</a>) -> <a href="./src/scrapengine/types/lazada_search_response.py">LazadaSearchResponse</a></code>
