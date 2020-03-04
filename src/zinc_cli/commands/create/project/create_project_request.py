class CreateProjectRequest:
    def __init__(self, project_name: str, domain_name: str, bucket_name: str, dry_run: bool):
        self.project_name: str = project_name
        self.bucket_name: str = bucket_name
        self.domain_name: str = domain_name
        self.dry_run: bool = dry_run
