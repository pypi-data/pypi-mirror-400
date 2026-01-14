import typer
from pathlib import Path
from typing import Optional, List

app = typer.Typer()

@app.command()
def init(
    refs: List[Path] = typer.Option(..., "--ref", "-r", help="Path to reference repository"),
    language: Optional[str] = typer.Option(None, "--language", "-l", help="Language to learn from (e.g., python, powershell)")
):
    """
    Learn from reference repo(s) and generate baselines and standards.
    """
    if not language:
        from core.language_loader import detect_language
        # Detect from the first reference repo
        if refs:
            language = detect_language(refs[0])
        
        if not language:
            typer.echo("Could not detect language. Please specify --language.")
            raise typer.Exit(code=1)
        typer.echo(f"Detected language: {language}")

    typer.echo(f"Initializing consistency engine for {language} using refs: {refs}")
    from core import reference_init
    reference_init.run(language, refs)

@app.command()
def analyze(
    repo: Path = typer.Option(..., "--repo", "-p", help="Path to the repository to analyze"),
    name: str = typer.Option(..., "--name", "-n", help="Logical name of the service/repo"),
    language: Optional[str] = typer.Option(None, "--language", "-l", help="Language of the repo"),
    with_ai: bool = typer.Option(False, "--with-ai", help="Enable AI-based analysis")
):
    """
    Analyze a new repo against learned standards.
    """
    if not language:
        from core.language_loader import detect_language
        language = detect_language(repo)
        
        if not language:
            typer.echo("Could not detect language. Please specify --language.")
            raise typer.Exit(code=1)
        typer.echo(f"Detected language: {language}")

    typer.echo(f"Analyzing {name} ({repo}) as {language} project. AI enabled: {with_ai}")
    from core import repo_analysis
    repo_analysis.run(language, repo, name, with_ai)

if __name__ == "__main__":
    app()
