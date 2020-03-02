class CreateStaticSiteRequest:
    def __init__(self, project_name: str, domain_name: str, bucket_name: str):
        self.project_name: str = project_name
        self.domain_name: str = domain_name
        self.bucket_name: str = bucket_name
