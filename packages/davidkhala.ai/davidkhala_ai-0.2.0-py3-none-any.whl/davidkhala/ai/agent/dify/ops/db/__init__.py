from typing import Any

from davidkhala.data.base.pg import Postgres


class DB(Postgres):

    def __init__(self, connection_string: str):
        super().__init__(connection_string)
        self.connect()

    def get_dict(self,
                 template: str,
                 values: dict[str, Any] | None = None,
                 request_options: dict[str, Any] | None = None
                 ) -> list[dict]:
        return Postgres.rows_to_dicts(self.query(template, values, request_options))
