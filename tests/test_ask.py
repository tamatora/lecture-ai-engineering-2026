from types import SimpleNamespace

from app import ask as ask_module


def test_main_keeps_chat_history_for_follow_up_questions(monkeypatch, capsys):
    class FakeChat:
        def __init__(self):
            self.history = []

        def send_message(self, question):
            self.history.append(question)
            return SimpleNamespace(
                text=f"answer {len(self.history)}",
                usage_metadata=None,
            )

    chat = FakeChat()
    client = SimpleNamespace(
        chats=SimpleNamespace(create=lambda model: chat),
    )
    monkeypatch.setattr(ask_module.genai, "Client", lambda api_key: client)
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    monkeypatch.setattr("sys.argv", ["app.ask", "最初の質問"])
    questions = iter(["続けて質問", ""])
    monkeypatch.setattr("builtins.input", lambda prompt: next(questions))

    ask_module.main()

    output = capsys.readouterr().out
    assert chat.history == ["最初の質問", "続けて質問"]
    assert "answer 1" in output
    assert "answer 2" in output
