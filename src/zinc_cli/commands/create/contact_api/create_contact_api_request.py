class CreateContactApiRequest:
    def __init__(self, project_name: str, forwarding_email: str):
        self.project_name: str = project_name
        self.forwarding_email: str = forwarding_email
