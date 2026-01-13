import json
from typing import TypedDict

import requests
from davidkhala.utils.http_request.stream import Request as StreamRequest, as_sse
from requests import Response, Session

from davidkhala.ai.agent.dify.api import API


class Feedbacks(API):
    def paginate_feedbacks(self, page=1, size=20):
        """
        when 'rating'='like', content=None
        when 'rating'='dislike', content can be filled by end user
        NOTE: for security reason, api cannot access conversation context associated with the feedback. End user should copy the conversation to comment by themselves.
        # waiting for https://github.com/langgenius/dify/issues/28067
        """
        response = requests.get(f"{self.base_url}/app/feedbacks", params={"page": page, "limit": size}, **self.options)
        if not response.ok:
            response.raise_for_status()
        else:
            return json.loads(response.text)

    def list_feedbacks(self):
        return self.paginate_feedbacks()['data']


class Conversation(API):
    """
    Note: The Service API does not share conversations created by the WebApp. Conversations created through the API are isolated from those created in the WebApp interface.
    It means you cannot get user conversation content from API, API call has only access to conversation created by API
    """

    def __init__(self, api_key: str, user: str):
        super().__init__(api_key)  # base_url need to be configured afterward if not default
        self.user = user  # user_id, from_end_user_id

    def paginate_messages(self, conversation_id):
        return self.request(f"{self.base_url}/messages", "GET", params={
            'conversation_id': conversation_id,
            'user': self.user,
        })

    def _chat_request_from(self, template: str, stream, **kwargs):
        """
        :param template:
        :param stream: Note: "Agent Chat App does not support blocking mode"
        :param kwargs:
        :return:
        """
        return {
            'url': f"{self.base_url}/chat-messages",
            'method': "POST",
            'json': {
                'query': template,
                'inputs': kwargs.pop('values', {}),  # to substitute query/template
                'response_mode': 'streaming' if stream else 'blocking',
                'conversation_id': kwargs.pop('conversation_id', None),
                'user': self.user,
                'files': kwargs.pop('files', [])
            },
            **kwargs
        }

    def async_chat(self, template: str, **kwargs) -> tuple[Response, Session]:
        s = StreamRequest(self)
        s.session = Session()
        return s.request(**self._chat_request_from(template, True, **kwargs)), s.session

    class ChatResult(TypedDict, total=False):
        thought: list[str]
        metadata: dict

    @staticmethod
    def reduce_chat_stream(response: Response) -> ChatResult:
        r: Conversation.ChatResult = {
            'thought': [],
        }
        for data in as_sse(response):
            match data['event']:
                case 'agent_thought':
                    r['thought'].append(data['thought'])
                case 'message_end':
                    r['metadata'] = data['metadata']
        return r

    def agent_chat(self, template: str, **kwargs) -> ChatResult:
        r, session = self.async_chat(template, **kwargs)
        reduced = Conversation.reduce_chat_stream(r)
        session.close()
        return reduced

    def bot_chat(self, template: str, **kwargs):
        r = self.request(**self._chat_request_from(template, False, **kwargs))
        assert r.pop('event') == 'message'
        assert r.pop('mode') == 'chat'
        return r
