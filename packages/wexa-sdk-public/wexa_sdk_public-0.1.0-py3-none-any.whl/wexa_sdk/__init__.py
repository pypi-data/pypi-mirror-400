from .core.http import HttpClient
from .agentflows import AgentFlows
from .executions import Executions
from .tables import Tables
from .connectors.core import Connectors
from .projects import Projects
from .skills import Skills
from .tasks import Tasks
from .inbox import Inbox
from .settings import Settings
from .marketplace import Marketplace
from .analytics import Analytics
from .connectors_mgmt import ConnectorsMgmt
from .files import Files
from .llm import Llm
from .knowledgebase import KnowledgeBase
from .tags import Tags
from .schedules import Schedules

class WexaClient:
    def __init__(self, base_url: str, api_key: str, user_agent: str | None = None, timeout: dict | None = None, retries: dict | None = None, polling: dict | None = None):
        self.http = HttpClient(base_url=base_url, api_key=api_key, user_agent=user_agent, timeout=timeout, retries=retries)
        self.agentflows = AgentFlows(self.http)
        self.executions = Executions(self.http, polling or {})
        self.tables = Tables(self.http)
        self.connectors = Connectors(self.http)
        self.projects = Projects(self.http)
        self.skills = Skills(self.http)
        self.tasks = Tasks(self.http)
        self.inbox = Inbox(self.http)
        self.settings = Settings(self.http)
        self.marketplace = Marketplace(self.http)
        self.analytics = Analytics(self.http)
        self.connectors_mgmt = ConnectorsMgmt(self.http)
        self.files = Files(self.http)
        self.llm = Llm(self.http)
        self.knowledgebase = KnowledgeBase(self.http)
        self.tags = Tags(self.http)
        self.schedules = Schedules(self.http)

    def _action(self, *args, **kwargs):
        # Kept for backward compatibility; delegate to connectors.action
        return self.connectors.action(*args, **kwargs)
