from davidkhala.ai.agent.dify.ops.db import DB


class Info(DB):
    @property
    def accounts(self): return self.get_dict("select name, email from accounts where status = 'active'")