from pydantic import BaseModel, model_validator
from typing import Dict, List


class From(BaseModel):
    email: str
    name: str


class Sender(BaseModel):
    from_address: From
    nickname: str
    reply_to: From
    address: str
    address_2: str
    city: str
    state: str
    zip: str


class UnSubscribeGroup(BaseModel):
    id: int


class EmailTemplate(BaseModel):
    id: str
    name: str
    variables: List[str]

class IpPool(BaseModel):
    name: str

class Config(BaseModel):
    api_key: str
    senders: Dict[str, Sender]
    ip_pools: Dict[str, IpPool]
    unsubscribe_groups: Dict[str, UnSubscribeGroup]
    email_templates: Dict[str, EmailTemplate]

    @model_validator(mode='before')
    def check_default_key(cls, values):
        if 'DEFAULT' not in values['senders']:
            raise ValueError("Senders missing a default")
        if 'DEFAULT' not in values['ip_pools']:
            raise ValueError("ip_pools missing a default")
        if 'DEFAULT' not in values['unsubscribe_groups']:
            raise ValueError("unsubscribe_groups missing a default")
        if 'DEFAULT' not in values['email_templates']:
            raise ValueError("email_templates missing a default")
        return values