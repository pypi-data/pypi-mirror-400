from typing import Literal

from pydantic import BaseModel


class DataSourceTypeAware(BaseModel):
    datasource_type: Literal["local_file", "online_document", "website_crawl"]