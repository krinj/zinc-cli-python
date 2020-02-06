from typing import Union


class CreateStaticSiteRequest:
    def __init__(self, project_name: str, domain_name: str, sub_domain: Union[str, None], with_https: bool=True):
        self.project_name: str = project_name
        self.domain_name: str = domain_name
        self.sub_domain: str = sub_domain
        self.with_https: bool = with_https
