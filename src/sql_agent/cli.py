import argparse
import sys

from .agent import build_agent
from .config import Settings
from .database import seed_demo_database


CYAN = "\033[96m"
DIM = "\033[2m"
GREEN = "\033[92m"
RESET = "\033[0m"


def _response_text(result: dict) -> str:
    output = result.get("output", "")
    if isinstance(output, str):
        return output
    if isinstance(output, list):
        # LangChain may return a list of message-like entries instead of a single string.
        return "\n".join(
            item.get("text", "") if isinstance(item, dict) else str(item)
            for item in output
        ).strip()
    return str(output)


def _chat(agent) -> None:
    print(f"{CYAN}SQL Agent{RESET} {DIM}| Gemini + LangChain{RESET}")
    print(f"{DIM}Ask a question about your database. Type 'exit' to quit.{RESET}\n")

    while True:
        try:
            question = input(f"{GREEN}you > {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return

        if not question:
            continue
        # Support a few simple terminal controls so the prompt stays usable in a shell.
        if question.lower() in {"exit", "quit", ":q"}:
            print("Goodbye.")
            return
        if question.lower() == "clear":
            print("\033[2J\033[H", end="")
            continue

        try:
            result = agent.invoke({"input": question})
            print(f"\n{CYAN}agent >{RESET} {_response_text(result)}\n")
        except Exception as error:
            print(f"\n{DIM}error > {error}{RESET}\n", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask questions about a SQL database.")
    parser.add_argument("question", nargs="*", help="Optional one-shot question")
    parser.add_argument("--seed-demo", action="store_true", help="Create the example SQLite database")
    args = parser.parse_args()

    settings = Settings.from_env()
    if args.seed_demo:
        seed_demo_database(settings.database_url)
        print(f"Demo database ready at {settings.database_url}")
        return

    try:
        agent = build_agent(settings)
    except Exception as error:
        parser.error(str(error))

    question = " ".join(args.question).strip()
    if question:
        try:
            print(_response_text(agent.invoke({"input": question})))
        except Exception as error:
            parser.error(str(error))
    else:
        _chat(agent)


if __name__ == "__main__":
    main()
