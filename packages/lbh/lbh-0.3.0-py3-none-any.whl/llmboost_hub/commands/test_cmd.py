import click
import subprocess
import json
from llmboost_hub.commands.completions import complete_model_names
from llmboost_hub.utils.config import config


@click.command(name="test", context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("model", required=True, shell_complete=complete_model_names)
@click.option(
    "-q",
    "--query",
    "query_str",
    default="What is an LLM in simple terms?",
    show_default=True,
    help="User query prompt.",
)
@click.option(
    "-t", "--max_tokens", default=300, show_default=True, type=int, help="Max tokens in completion."
)
@click.option("--host", default="127.0.0.1", show_default=True, help="Host to call.")
@click.option(
    "--port", default=config.LBH_SERVE_PORT, show_default=True, type=int, help="Port to call."
)
@click.pass_context
def test_cmd(ctx: click.Context, model: str, query_str: str, max_tokens: int, host: str, port: int):
    """
    Call the running llmboost serve endpoint and print the raw JSON response.
    """
    # Build endpoint URL and JSON payload for OpenAI-compatible chat API
    url = f"http://{host}:{port}/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": query_str}],
        "max_tokens": max_tokens,
    }
    data_str = json.dumps(payload)

    # Use curl for simplicity; surface the full command in verbose mode
    cmd = ["curl", "-sS", url, "-H", "Content-Type: application/json", "-d", data_str]
    if ctx.obj.get("VERBOSE", False):
        click.echo("[test] " + " ".join(cmd))

    # Execute request and propagate errors with a clear message
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        response_text = result.stdout
        print(response_text)

        # Verify model name in response
        try:
            response_data = json.loads(response_text)
            response_model = response_data.get("model", "")
            if response_model != model:
                click.secho(
                    f"Warning: Response model '{response_model}' does not match requested model '{model}'",
                    fg="yellow",
                    err=True,
                )
        except (json.JSONDecodeError, KeyError):
            # Skip validation if response isn't valid JSON
            pass

        print()
    except subprocess.CalledProcessError as e:
        raise click.ClickException(f"curl failed (exit {e.returncode})")
