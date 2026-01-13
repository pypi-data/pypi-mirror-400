import click
import pandas as pd
import tabulate
from llmboost_hub.commands.list import do_list
from llmboost_hub.commands.completions import complete_model_names


@click.command(name="status", context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("model", required=False, default="", shell_complete=complete_model_names)
@click.pass_context
def status_cmd(ctx: click.Context, model: str | None):
    """
    Show a compact status table for models.
    """
    verbose = ctx.obj.get("VERBOSE", False)
    data = do_list(query=model or "", verbose=verbose)
    df = data.get("images_df")
    if not isinstance(df, pd.DataFrame) or df.empty:
        click.echo("Found 0 models")
        return

    # Keep only desired columns if available; bail out if none found
    cols = [c for c in ["status", "model"] if c in df.columns]
    if not cols:
        click.echo("No status information available.")
        return
    df = df[cols].reset_index(drop=True)
    df.index += 1
    click.echo(f"Found {len(df)} models")
    click.echo(
        tabulate.tabulate(
            df.values.tolist(), headers=list(df.columns), showindex=list(df.index), tablefmt="psql"
        )
    )
