"""第1回: 会話履歴を保ちながらLLMに質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 講座に固有の質問から開始する

最初の質問のあとも、同じチャットセッションで続けて質問できる。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def ask(chat, question: str) -> tuple[str, int | None, int | None]:
    response = chat.send_message(question)
    usage = response.usage_metadata
    input_tokens = usage.prompt_token_count if usage else None
    output_tokens = usage.candidates_token_count if usage else None
    return response.text, input_tokens, output_tokens


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    client = genai.Client(api_key=get_api_key())
    chat = client.chats.create(model=MODEL)
    question = args.question
    try:
        while True:
            print(f"\n[質問] {question}\n")
            answer, input_tokens, output_tokens = ask(chat, question)
            print(answer)
            input_display = input_tokens if input_tokens is not None else "不明"
            output_display = output_tokens if output_tokens is not None else "不明"
            print(f"\n[tokens] input={input_display} output={output_display}")

            try:
                question = input("\n次の質問 (終了: exit / quit / 終了)> ").strip()
            except EOFError:
                print()
                break
            if question.casefold() in {"exit", "quit", "終了"}:
                break
            if not question:
                continue
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
