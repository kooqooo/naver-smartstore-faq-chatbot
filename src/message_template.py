from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional


@dataclass
class Message:
    role: str
    content: str

    def __post_init__(self) -> None:
        if self.role not in ["system", "user", "assistant"]:
            raise ValueError("role은 'system', 'user','assistant' 중에 하나여야 합니다.")

    def __repr__(self) -> str:
        return f"Message(role='{self.role}', content='{self.content}')"

    def to_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}

    def render(self, context: dict) -> str:
        try:
            return self.content.format(**context)
        except KeyError as e:
            raise KeyError(f"키 에러: {e}가 context에 없습니다.") from e
        except Exception as e:
            raise e


class Messages:
    def __init__(self, system_prompt: Optional[str] = None) -> None:
        self.messages: list[Message] = []
        if system_prompt:
            self.add_message("system", system_prompt)

    def add_message(self, role: str, content: str):
        self.messages.append(Message(role=role, content=content))

    def add_messages(self, messages: List[tuple[str, str]]) -> None:
        for role, content in messages:
            self.add_message(role, content)

    def render_all(self, context: dict) -> "Messages":
        rendered_messages = Messages()
        for message in self.messages:
            rendered_content = message.render(context)
            rendered_messages.add_message(message.role, rendered_content)
        return rendered_messages
    
    @classmethod
    def from_prompt_file(cls, prompt_path: str) -> "Messages":
        path = Path(prompt_path)
        if not path.exists():
            raise FileNotFoundError(f"{path}에 프롬프트가 존재하지 않습니다.")
        
        prompt = path.read_text(encoding="utf-8-sig").strip()
        return cls(system_prompt=prompt)

    def to_dict(self) -> List[dict[str, str]]:
        return [
            {"role": message.role, "content": message.content}
            for message in self.messages
        ]

    def to_list(self) -> List[Tuple[str, str]]:
        return [f"{message.role}: {message.content}" for message in self.messages]

    def __add__(self, other) -> "Messages":
        result = Messages()
        result.messages = self.messages.copy()

        try:
            if isinstance(other, Messages):
                result.messages.extend(other.messages)
            elif isinstance(other, Message):
                result.messages.append(other)
        except Exception as e:
            raise e
        return result

    def __repr__(self) -> str:
        return f"MessageList(messages={self.messages})"

    def __str__(self) -> str:
        return str(self.to_dict())

    def __iter__(self):
        return iter(self.messages)

    def __len__(self) -> int:
        return len(self.messages)


if __name__ == "__main__":
    # Example usage
    messages = Messages()
    messages.add_message("assistant", "Hello, how can I help you?")

    messages.add_messages(
        [
            ("system", "You are a helpful assistant"),
            ("user", "Tell me a joke about {topic}"),
        ]
    )
    other_messages = Messages()
    other_messages.add_messages(
        [
            ("system", "더하기 연산자 테스트"),
            ("user", "이게 보인다면 성공입니다."),
            ("assistant", "__add__ 메서드를 사용했습니다."),
        ]
    )
    messages += other_messages

    messages.add_message("system", "add_mesage 테스트")
    messages.add_messages(
        [("user", "add_messages 테스트"), ("assistant", "add_messages 테스트2")]
    )
    messages = messages.render_all({"topic": "cats"})

    test_message = Messages()
    test_message = test_message.from_prompt_file("prompts/chat_system_prompt.txt")
    test_message.add_message("user", "내 이름은 {name}이야.")
    test_message.add_message("assistant", "안녕하세요, {name}님.")
    test_message = test_message.render_all({"reference": "주어진 정보", "name": "구희찬"})
    test_message = test_message.render_all({"reference": "주어진 정보2"}) # 당연하게도 한 번 렌더링되면 다시 렌더링 불가

    def pretty_print(messages: List[dict[str, str]]):
        role_width = max(len(message["role"]) for message in messages) + 2
        for message in messages:
            print(message["role"].ljust(role_width) + message["content"])

    pretty_print(messages.to_dict())
    print()
    pretty_print(test_message.to_dict())
