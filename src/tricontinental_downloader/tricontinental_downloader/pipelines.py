"""Pipelines for processing downloaded files (PDFs) from the crawler.

This pipeline derives from Scrapy's FilesPipeline and provides a
small customization to normalise output filenames (date + slug).
"""

import os
import re
from urllib.parse import urlparse

from scrapy import Request
from scrapy.pipelines.files import FilesPipeline


class EnglishPDFPipeline(FilesPipeline):
    """Pipeline that stores English PDFs with a normalized filename.

    The pipeline leaves download handling to FilesPipeline but rewrites the
    output filename to a predictable pattern: {date}_{slug}_EN_Web.pdf
    where ``date`` is extracted from the original filename when present.
    """

    def get_media_requests(self, item, _info):
        """Yield File Requests for item file_urls.

        The request ``meta`` carries the original item so downstream
        processors can access the referring page or other metadata.
        """
        for url in item.get("file_urls", []):
            yield Request(url, meta=item)

    def file_path(self, request, _response=None, _info=None, *, _item=None):
        """Return the storage path for the downloaded file.

        The returned filename uses a date-based prefix when the original
        filename contained an 8-digit date; otherwise a placeholder is
        used.
        """
        url = request.url
        filename = os.path.basename(urlparse(url).path)

        # Get date from filename
        date_match = re.search(r"(20\d{6})", filename)
        date = date_match.group(1) if date_match else "00000000"

        # Title part
        name_no_ext = re.sub(r"\.pdf$", "", filename, flags=re.I)
        name_no_date = re.sub(r"20\d{6}[_-]?", "", name_no_ext)
        name_no_date = re.sub(r"[^A-Za-z0-9_-]+", "_", name_no_date)
        name_no_date = re.sub(r"_+", "_", name_no_date).strip("_")

        return f"{date}_{name_no_date}_EN_Web.pdf"
