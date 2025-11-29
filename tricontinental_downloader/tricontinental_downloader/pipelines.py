import re
import os
from urllib.parse import urlparse
from scrapy.pipelines.files import FilesPipeline
from scrapy import Request


class EnglishPDFPipeline(FilesPipeline):

    def get_media_requests(self, item, info):
        for url in item.get("file_urls", []):
            yield Request(url, meta=item)

    def file_path(self, request, response=None, info=None, *, item=None):
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
