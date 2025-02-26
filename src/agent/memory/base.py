import json
from dataclasses import dataclass
from typing import List
from enum import StrEnum
from pathlib import Path

from src.agent.plan import Plan

SESSIONS_PATH = Path(Path.home() / '.aiops' / 'sessions')
if not SESSIONS_PATH.exists():
    SESSIONS_PATH.mkdir(parents=True, exist_ok=True)


class Role(StrEnum):
    SYS = 'system'
    USER = 'user'
    ASSISTANT = 'assistant'

    @staticmethod
    def from_str(item):
        if item == 'user':
            return Role.USER
        elif item == 'assistant':
            return Role.ASSISTANT
        elif item == 'system':
            return Role.SYS
        else:
            return None


@dataclass
class Message:
    role: Role
    content: str


@dataclass
class Session:
    name: str
    messages: List[Message]

    # plan

    def messages_to_dict_list(self):
        """Converts the message list into a format compatible with Ollama"""
        return [{'role': str(msg.role), 'content': msg.content} for msg in self.messages]

    @staticmethod
    def from_json(path: str):
        """Get a session from a JSON file"""
        with open(str(path), 'r', encoding='utf-8') as fp:
            data = json.load(fp)
            return data['id'], Session(
                name=data['name'],
                messages=[Message(Role.from_str(msg['role']), msg['content']) for msg in data['messages']]
            )


class Memory:
    """
    Contains the chat history for each session, it is bounded to the Agent class.
    """

    def __init__(self):
        self.sessions = {}
        self.load_sessions()

    def store_message(self, sid: int, message: Message):
        """Add a message to a session identified by session id or creates a new one"""
        if not isinstance(message, Message):
            raise ValueError(f'Not a message: {message}')
        if sid not in self.sessions:
            self.sessions[sid] = Session(name='New Session', messages=[])

        self.sessions[sid].messages.append(message)

    def store_plan(self, sid: int, plan: Plan):
        pass

    def get_session(self, sid: int) -> Session:
        """
        :return: a session identified by session id or None
        """
        return self.sessions[sid] if sid in self.sessions else None

    def get_sessions(self) -> dict:
        """Returns all loaded sessions as id: session"""
        return self.sessions

    def save_session(self, sid: int):
        """Saves the current session state to a JSON file at SESSION_PATH"""
        if sid not in self.sessions:
            raise ValueError(f'Session {sid} does not exist')

        session = self.sessions[sid]
        self.delete_session(sid)
        with open(f'{SESSIONS_PATH}/{sid}__{session.name}.json', 'w+', encoding='utf-8') as fp:
            data = {
                'id': sid,
                'name': session.name,
                'messages': session.messages_to_dict_list()
            }
            json.dump(data, fp)

    def delete_session(self, sid: int):
        """Deletes a session from SESSION_PATH"""
        if sid not in self.sessions:
            raise ValueError(f'Session {sid} does not exist')

        for path in SESSIONS_PATH.iterdir():
            if path.is_file() and path.suffix == '.json' and path.name.startswith(f'{sid}__'):
                path.unlink()

    def rename_session(self, sid: int, session_name: str):
        """Renames a session identified by session id or creates a new one"""
        if sid not in self.sessions:
            self.sessions[sid] = Session(name=session_name, messages=[])
        else:
            self.sessions[sid].name = session_name

    def load_sessions(self):
        """Loads the saved sessions at SESSION_PATH"""
        for path in SESSIONS_PATH.iterdir():
            if path.is_file() and path.suffix == '.json':
                sid, session = Session.from_json(str(path))
                self.sessions[sid] = session
