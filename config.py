import yaml
import os
from dataclasses import dataclass, field


@dataclass
class NtfyConfig:
    server: str
    topic: str


@dataclass
class EmailAuthentication:
    token_name: str
    token: str


@dataclass
class EmailConfig:
    to: str
    from_address: str | None = None
    subject: str | None = None
    api_url: str | None = None
    message_stream: str | None = None
    smtp_server: str | None = None
    smtp_port: int | None = None
    smtp_url: str | None = None
    username: str | None = None
    password: str | None = None
    authentication: EmailAuthentication | None = None


@dataclass
class Rule:
    name: str
    regex: str
    modes: list[str]
    once: bool = False
    every_n_matches: int | None = None
    cooldown: int | None = None
    alert_if_missing_for_seconds: int | None = None
    lines_after: int | None = None


@dataclass
class Config:
    rules: list[Rule]
    ntfy: NtfyConfig | None = None
    email: EmailConfig | None = None


def load_config(path: str | None = None) -> Config:
    if path is None:
        path = os.path.join(os.getcwd(), "my_notifier.yaml")

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    ntfy = NtfyConfig(**data["ntfy"]) if "ntfy" in data else None

    email = None
    if "email" in data:
        email_data = dict(data["email"])
        auth_data = email_data.pop("authentication", None)
        authentication = EmailAuthentication(**auth_data) if auth_data else None
        email = EmailConfig(**email_data, authentication=authentication)

    rules = [Rule(**rule) for rule in data.get("rules", [])]

    return Config(ntfy=ntfy, email=email, rules=rules)
