# Crawl

Crawl is a Scrapy-based project for crawling one or more domains and extracting
page metadata, headings, images, and links.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Command-Line Usage](#command-line-usage)
  - [Spider Arguments](#spider-arguments)
  - [Programmatic Usage](#programmatic-usage)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Command-Line Usage

```bash
scrapy crawl basic_spider -a start_urls=https://example.com -O output.json
```

Multiple start URLs (comma-separated or JSON list):

```bash
scrapy crawl basic_spider \
  -a start_urls=https://example.com,https://example.org \
  -O output.json
```

### Spider Arguments

- `start_urls` (required): Comma-separated URLs or a JSON list of URLs.
- `start_url` (optional): Alias for a single start URL.
- `allowed_domains` (optional): Comma-separated domains or JSON list. Defaults to
  domains derived from `start_urls`.
- `include_html` (optional): Set to `true` to include raw HTML in items.
- `download_delay` (optional): Override download delay for this run.
- `concurrent_requests` (optional): Override global concurrency for this run.
- `concurrent_requests_per_domain` (optional): Override per-domain concurrency.
- `autothrottle` (optional): Enable or disable AutoThrottle for this run.
- `autothrottle_target_concurrency` (optional): Override AutoThrottle target.

### SEO Fields

Each item includes SEO-focused metadata such as title and description lengths,
robots directives, canonical and AMP links, hreflang tags, Open Graph and
Twitter card data, JSON-LD schema types, heading distribution, word counts,
link classification, and image alt coverage.

### Settings

- `SEO_REQUEST_HEADERS`: Default headers injected by middleware.
- `SEO_PROXY_ENABLED`, `SEO_PROXY_LIST`, `SEO_PROXY_MODE`: Optional proxy rotation.
- `SEO_REQUIRED_FIELDS`, `SEO_MIN_WORD_COUNT`: Pipeline validation controls.
- `HTTPCACHE_ENABLED`: Enable HTTP cache for faster development runs.
- `RETRY_HTTP_CODES`, `RETRY_BACKOFF_BASE`, `RETRY_BACKOFF_MAX`: Retry policy.

### Programmatic Usage

```python
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from core.spiders.basic_spider import BasicSpider

process = CrawlerProcess(get_project_settings())
process.crawl(BasicSpider, start_urls=["https://example.com"])
process.start()
```

## Testing

```bash
python -m unittest discover -s tests
```

## Project Structure

- **scrapy.cfg**: Scrapy configuration file.
- **core/**: Scrapy project package.
  - **items.py**: Item definitions.
  - **middlewares.py**: Spider and downloader middlewares.
  - **pipelines.py**: Pipelines for processing scraped data.
  - **settings.py**: Scrapy configuration settings.
  - **spiders/basic_spider.py**: Basic spider implementation.
- **requirements.txt**: Python dependencies.
- **setup.py**: Setup script for installing the package.
- **MANIFEST.in**: Files included in package builds.
- **README.md**: Project documentation.

## Contributing

We welcome contributions! If you have an idea for a new feature or have found a
bug, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file
for details.
