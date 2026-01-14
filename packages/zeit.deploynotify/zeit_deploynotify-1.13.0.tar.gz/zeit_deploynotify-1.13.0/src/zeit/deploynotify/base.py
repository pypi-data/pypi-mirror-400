class Notification:
    def __init__(self, environment, project, version, previous_version):
        self.environment = environment
        self.project = project
        self.version = version
        self.previous_version = previous_version
