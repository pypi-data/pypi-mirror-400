import re
from urllib.parse import urlparse


def extract_notion_page_id(url: str) -> str:
    """extract notion page id from notion page url.
    page id is UUIDv4 includes the hyphen or not.

    example url:
    - https://www.notion.so/Some-Title-1234567890abcdef1234567890abcdef
    - https://www.notion.so/Some-Title-12345678-90ab-cdef-1234-567890abcdef

    Args:
        url (str): notion page url

    Returns:
        str: notion page id
    """
    path = urlparse(url).path
    pattern = re.compile(
        r"([0-9a-fA-F]{32})|"  # 하이픈 없는 32자리
        r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{12})"
    )
    match = pattern.search(path)
    if match:
        page_id = match.group(1) if match.group(1) else match.group(2)
        return transform_block_id_to_uuidv4(page_id)
        # return page_id.replace("-", "")
    else:
        raise ValueError(
            f"Invalid notion page url. The page id is not formatted as UUIDv4: {url}"
        )


def transform_block_id_to_uuidv4(object_id: str) -> str:
    """convert notion block id without hyphens to with hyphens.

    Args:
        object_id (str): notion block object id

    Returns:
        str: notion block id with hyphens (format: 8-4-4-4-12)
    """
    # First remove any existing hyphens
    clean_id = object_id.replace("-", "")

    # Insert hyphens in UUID format (8-4-4-4-12)
    return f"{clean_id[:8]}-{clean_id[8:12]}-{clean_id[12:16]}-{clean_id[16:20]}-{clean_id[20:]}"


def validate_page_id(page_id: str) -> bool:
    """validate the page id format is valid UUIDv4 or not."""

    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )

    result = uuid_pattern.match(page_id)

    return result is not None
