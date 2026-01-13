# zmp-notion-exporter

![Platform Badge](https://img.shields.io/badge/platform-zmp-red)
![Component Badge](https://img.shields.io/badge/component-exporter-red)
![CI Badge](https://img.shields.io/badge/ci-github_action-green)
![License Badge](https://img.shields.io/badge/license-MIT-green)
![PyPI - Version](https://img.shields.io/pypi/v/zmp-notion-exporter)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/zmp-notion-exporter)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/zmp-notion-exporter)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/zmp-notion-exporter)

<!-- ![Language Badge](https://img.shields.io/badge/language-python-blue)
![Version Badge](https://img.shields.io/badge/version-^3.12-blue) -->
# Goals

A utility library for exporting Notion pages to Markdown, HTML, and PDF formats. This project was developed to support the Cloud Z MP manual system.

# Key Features

- Export Notion pages to Markdown format
- Support for including subpages
- Automatic image download and path conversion
- Automatic document structure generation

# Installation

```bash
pip install zmp-notion-exporter
```

Or if you're using Poetry:

```bash
poetry add zmp-notion-exporter
```

# Usage

## Basic Setup

1. Configure Notion API Token
```python
import os
from dotenv import load_dotenv
from zmp_notion_exporter import NotionPageExporter, extract_notion_page_id

load_dotenv()
notion_token = os.environ.get("NOTION_TOKEN")
```

## Export All Pages using the CLI Command

The package provides a command-line interface for easy exporting. You can use it in the following ways:
```bash
$ zmp-notion-exporter --help
usage: zmp-notion-exporter [-h] [-t] -r  [-c] -o  [-i] [-f]

Notion Page Export Tool

options:
  -h, --help            show this help message and exit
  -t , --notion-token   Notion API Token. You can set it by NOTION_TOKEN environment variable.
  -r , --root-page-id   Root page ID to start export. You can set it by ROOT_PAGE_ID environment variable.
  -c , --child-page-id
                        Child page ID to start export. You can set it by CHILD_PAGE_ID environment variable.
  -o , --output-dir     Directory path for export results. You can set it by OUTPUT_DIR environment variable.
  -i , --include-subpages
                        Include subpages in the export(default: True)
  -f , --file-type      File type for export(default: mdx). support: md, mdx, html
```

```bash
$ zmp-notion-exporter -r 19ab7135d33b803b8ea7ff3e366f707d -o /Users/kks/IdeaProjects/aiops/zmp-documents-ui -c ""
>>> Starting Notion export with following parameters
--------------------------------------------------------
@ --notion-token: ntn_4...xJ27u
@ --root-page-id: 19ab7135d33b803b8ea7ff3e366f707d
@ --child-page-id:
@ --output-dir: /zmp-documents-ui
@ --include-subpages: True
@ --file-type: mdx
--------------------------------------------------------
>>> Exporting root page: 19ab7135d33b803b8ea7ff3e366f707d
Progress: [██████████████████████████████████████████████████] 100% (26/26)
- Result (Total pages / Exported pages): (26, 26)
- Progress: 100%
>>> Export completed successfully in 95.78 seconds
Do you want to show output nodes? (y/n): n
```

### CLI Options

- `--notion-token`: Your Notion API token (can be set via `NOTION_TOKEN` env var)
- `--root-page-id`: Root page ID or URL to start export (can be set via `ROOT_PAGE_ID` env var)
- `--output-dir`: Directory path for export results (can be set via `OUTPUT_DIR` env var)
- `--include-subpages`: Include subpages in the export (default: True)
- `--file-type`: Export file type (default: mdx, supports: md, mdx, html)


## Export All Pages

```python
exporter = NotionPageExporter(
    notion_token=notion_token,
    root_page_id=extract_notion_page_id("YOUR_NOTION_PAGE_URL"),
    root_output_dir=".output"
)

path = exporter.markdownx(include_subpages=True)
```

## Sample code to export in markdown files
include all sub pages of the root notion page
```python
import logging
import os
import time

from dotenv import load_dotenv

from zmp_notion_exporter import NotionPageExporter, extract_notion_page_id

load_dotenv()

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logging.getLogger("zmp_notion_exporter.page_exporter").setLevel(logging.INFO)
logging.getLogger("httpcore").setLevel(logging.INFO)


notion_token = os.environ.get("NOTION_TOKEN", "")

if not notion_token:
    raise ValueError("NOTION_TOKEN is not set")


root_page_zcp_url = (
    "https://www.notion.so/cloudzcp/Cloud-Z-CP-19ab7135d33b803b8ea7ff3e366f707d?pvs=4"
)

output_dir = ".output"

exporter = NotionPageExporter(
    notion_token=notion_token,
    root_page_id=extract_notion_page_id(root_page_zcp_url),
    root_output_dir=output_dir,
)

start_time = time.time()

path = exporter.markdownx(include_subpages=True)

print(path)

docs_node, static_image_node = exporter.get_output_nodes()
docs_node.print_pretty(include_leaf_node=True)
static_image_node.print_pretty(include_leaf_node=False)


end_time = time.time()

print("-" * 100)
print(f"Export took {end_time - start_time:.2f} seconds")
print("-" * 100)


# Output sample
.output
.output/
└── docs/
    └── cloud-z-cp/
        └── introduction/
            └── product-overview
            └── glossary
            └── release-notes
            └── application-modernization
            └── cloud-application-architecture
        └── introduction-2/
            └── release-notes-2
            └── release-notes-1
.output/
└── static/
    └── img/
        └── cloud-z-cp/
            └── introduction/
            └── introduction-2/
----------------------------------------------------------------------------------------------------
Export took 27.57 seconds
----------------------------------------------------------------------------------------------------

# double check using the os command
$ tree .output
├── docs
│   └── cloud-z-cp
│       ├── _category_.json
│       ├── introduction
│       │   ├── _category_.json
│       │   ├── application-modernization.mdx
│       │   ├── cloud-application-architecture.mdx
│       │   ├── glossary.mdx
│       │   ├── product-overview.mdx
│       │   └── release-notes.mdx
│       └── introduction-2
│           ├── _category_.json
│           ├── release-notes-1.mdx
│           └── release-notes-2.mdx
└── static
    └── img
        └── cloud-z-cp
            ├── introduction
            │   ├── 19fb7135-d33b-800a-8e85-f4be38bdeb0d.png
            │   ├── 19fb7135-d33b-8010-b82a-c1a9e182a45d.png
            │   ├── 19fb7135-d33b-8029-9cb0-e38b61df0c4b.png
            │   ├── 19fb7135-d33b-8044-b4b0-dd8150f553d0.png
            │   ├── 19fb7135-d33b-8092-893e-e2e92070f50b.png
            │   ├── 19fb7135-d33b-80a2-960b-e6d91fb708ba.png
            │   └── 19fb7135-d33b-80dc-97ed-c9960713e0c3.png
            └── introduction-2

9 directories, 17 files
```

## Export to markdown files of the specific page
```python
import logging
import os
import time

from dotenv import load_dotenv

from zmp_notion_exporter import NotionPageExporter, extract_notion_page_id

load_dotenv()

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logging.getLogger("zmp_notion_exporter.page_exporter").setLevel(logging.INFO)
logging.getLogger("httpcore").setLevel(logging.INFO)


notion_token = os.environ.get("NOTION_TOKEN", "")

if not notion_token:
    raise ValueError("NOTION_TOKEN is not set")


root_page_zcp_url = (
    "https://www.notion.so/cloudzcp/Cloud-Z-CP-19ab7135d33b803b8ea7ff3e366f707d?pvs=4"
)

target_page_urls = [
    "https://www.notion.so/cloudzcp/Getting-Started-Sample-Page-193b7135d33b80e0954fc9e52d94291a?pvs=4",  # Getting Started Sample Page
]

output_dir = ".output"

exporter = NotionPageExporter(
    notion_token=notion_token,
    root_page_id=extract_notion_page_id(root_page_zcp_url),
    root_output_dir=output_dir,
)

start_time = time.time()
path = exporter.markdownx(
    page_id=extract_notion_page_id(target_page_urls[-1]), include_subpages=True
)

# Output sample
.output/docs/cloud-z-cp/introduction/release-notes
.output/
└── docs/
    └── cloud-z-cp/
        └── introduction/
            └── product-overview
            └── glossary
            └── release-notes
            └── application-modernization
            └── cloud-application-architecture
        └── introduction-2/
            └── release-notes-2
            └── release-notes-1
.output/
└── static/
    └── img/
        └── cloud-z-cp/
            └── introduction/
            └── introduction-2/
----------------------------------------------------------------------------------------------------
Export took 10.21 seconds
----------------------------------------------------------------------------------------------------

# double check using the os command
$ tree .output
.output
├── docs
│   └── cloud-z-cp
│       ├── introduction
│       │   └── release-notes.mdx
│       └── introduction-2
└── static
    └── img
        └── cloud-z-cp
            ├── introduction
            └── introduction-2

9 directories, 1 file
```


# Project Structure

```
.
├── docs/          # Exported document files
└── static/        # Static files like images
    └── img/
```

# Development Setup

## Requirements

- Python 3.11 or higher
- Poetry 1.8.5
- Notion API Token

# Getting Started

```bash
# Clone the repository
git clone https://github.com/yourusername/zmp-notion-exporter.git
cd zmp-notion-exporter

# Install dependencies
poetry install

# Set up environment variables
cp .env.example .env
# Add your NOTION_TOKEN to the .env file
```

# Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

# License

This project is distributed under the MIT License. See the [LICENSE](LICENSE) file for more information.

# Contact

Project Maintainer - [@kilsoo75](https://github.com/kilsoo75)

Project Link: [https://github.com/yourusername/zmp-notion-exporter](https://github.com/yourusername/zmp-notion-exporter)
