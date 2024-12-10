from typing import List, Tuple, Union



class Message:
    def __init__(self, role: str, content: str) -> None:
        self.role = role
        self.content = content

    def __repr__(self) -> str:
        return f"Message(role='{self.role}', content='{self.content}')"

    def render(self, context: dict) -> str:
        return self.content.format(**context)


class Messages:
    def __init__(self) -> None:
        self.messages: list[Message | None] = []

    def validate_role(self, role: str):
        assert role in [
            "system",
            "user",
            "assistant",
        ], "Role must be 'system', 'user', or 'assistant'"

    def add_message(self, role: str, content: str):
        self.validate_role(role)
        self.messages.append(Message(role, content))

    def add_messages(
        self, messages: Union[List[Union[List, Tuple]], Tuple[Union[List, Tuple]]]
    ):
        for message in messages:
            self.validate_role(message[0])
            self.messages.append(Message(message[0], message[1]))

    def render(self, context: dict) -> None:
        for message in self.messages:
            message.content = message.render(context)

    def to_dict(self) -> List[dict[str, str]]:
        return [
            {"role": message.role, "content": message.content}
            for message in self.messages
        ]

    def to_list(self) -> List[Tuple[str, str]]:
        return [f"{message.role}: {message.content}" for message in self.messages]

    def __add__(self, other) -> "Messages":
        if isinstance(other, Messages):
            self.messages.extend(other.messages)
        elif isinstance(other, Message):
            self.messages.append(other)
        else:
            raise TypeError(f"'{type(self)}' + '{type(other)}'")
        return self

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
    messages.render({"topic": "cats"})

    def pretty_print(messages: List[dict[str, str]]):
        role_width = max(len(message["role"]) for message in messages) + 2
        content_width = max(len(message["content"]) for message in messages) + 2
        for message in messages:
            print(
                message["role"].ljust(role_width)
                + message["content"].ljust(content_width)
            )

    pretty_print(messages.to_dict())
