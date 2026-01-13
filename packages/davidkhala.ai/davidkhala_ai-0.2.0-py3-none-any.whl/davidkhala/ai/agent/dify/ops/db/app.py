from davidkhala.ai.agent.dify.ops.db import DB
from davidkhala.ai.agent.dify.ops.db.orm import AppModelConfig
from sqlalchemy.orm import Session
from sqlalchemy import desc

class Studio(DB):
    user_feedbacks_sql = """SELECT mf.conversation_id,
                        mf.content,
                        m.query,
                        m.answer
                 FROM message_feedbacks mf
                          LEFT JOIN messages m ON mf.message_id = m.id
                 WHERE mf.from_source = 'user'"""

    @property
    def apps(self): return self.get_dict("select id, name, mode from apps where status = 'normal'")

    def app_config(self, app_id) -> AppModelConfig | None:
        with Session(self.client) as session:
            return (
                session.query(AppModelConfig)
                .filter(AppModelConfig.app_id == app_id)
                .order_by(desc(AppModelConfig.created_at))
                .first()
            )

    def update_app_config(self, record: AppModelConfig, refresh: bool = False) -> AppModelConfig | None:
        with Session(self.client) as session:
            session.add(record)
            session.commit()
            if refresh:
                session.refresh(record)
                return record
            return None