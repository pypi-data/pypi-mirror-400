from time import sleep

from davidkhala.ai.agent.dify.ops.console import API
from davidkhala.ai.agent.dify.ops.console.session import ConsoleUser


class ConsolePlugin(API):
    def __init__(self, context: ConsoleUser):
        super().__init__()
        self.base_url = f"{context.base_url}/workspaces/current/plugin"
        self.session.cookies = context.session.cookies
        self.options = context.options

    def upgrade(self, *plugin_names: str) -> list[dict]:
        versions = self.latest_version(*plugin_names)
        self.async_install(*versions)

        current = []
        while len(current) < len(versions):
            current = self.get(*plugin_names)
            sleep(1)
        return current

    def async_install(self, *plugin_versioned_names: str) -> str | None:
        url = f"{self.base_url}/install/marketplace"
        r = self.request(url, method="POST", json={
            'plugin_unique_identifiers': plugin_versioned_names,
        })
        if r['all_installed']:
            # plugins exist, no need to install
            return None

        return r['task_id']

    def plugins(self, *, page=1, size=100):
        url = f"{self.base_url}/list?page={page}&page_size={size}"
        r = self.request(url, method="GET")
        _ = r['plugins']
        assert r['total'] == len(_)
        return _

    def get(self, *plugin_names: str) -> list[dict]:
        "inspect installed plugins"
        url = f"{self.base_url}/list/installations/ids"
        r = self.request(url, method="POST", json={
            'plugin_ids': plugin_names,
        })
        return r['plugins']

    def latest_version(self, *plugin_names: str) -> dict:
        url = f"{self.base_url}/list/latest-versions"
        r = self.request(url, method="POST", json={
            'plugin_ids': plugin_names,
        })
        return [r['versions'][name]['unique_identifier'] for name in plugin_names]

    def uninstall(self, id: str):
        url = f"{self.base_url}/uninstall"

        r = self.request(url, method="POST", json={
            'plugin_installation_id': id
        })
        assert r['success'] is True

    def uninstall_by(self, *plugin_names: str):
        for name in plugin_names:
            r = self.get(name)
            self.uninstall(r[0]['id'])
