# Safe agent scaffolding (sanitized). See README for notes.
from dataclasses import dataclass

@dataclass
class AgentConfig:
    name: str
    role: str
    description: str

financial_analyst = AgentConfig(name='financial_analyst', role='Financial Analyst (Neutral)', description='Assist in extracting structured fields. Do not fabricate facts or provide investment advice.')
