"""
Command-line interface for Fabricate.
"""

import os
import sys
from typing import Optional

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from .persona import PersonaFabricator, run_fabrication
from .config import PersonaConfig

console = Console()

# Load environment variables
load_dotenv()


@click.group()
@click.version_option(version="0.1.0", prog_name="fabricate")
def cli():
    """
    Fabricate - GitHub Persona Generator
    
    An experimental tool for creating AI-generated GitHub personas
    with realistic repositories and commit histories.
    """
    pass


@cli.command()
@click.option(
    "--anthropic-key", "-a",
    envvar="FABRICATE_ANTHROPIC_API_KEY",
    help="Anthropic API key (or set FABRICATE_ANTHROPIC_API_KEY)"
)
@click.option(
    "--github-token", "-g",
    envvar="FABRICATE_GITHUB_TOKEN",
    help="GitHub personal access token (or set FABRICATE_GITHUB_TOKEN)"
)
@click.option(
    "--languages", "-l",
    multiple=True,
    default=["python", "javascript", "rust", "solidity"],
    help="Programming languages to use (can specify multiple)"
)
@click.option(
    "--repos", "-r",
    default=None,
    type=click.IntRange(1, 50),
    help="Number of repositories to create (random 1-50 if not specified)"
)
@click.option(
    "--history-days", "-d",
    default=None,
    type=click.IntRange(30, 1825),
    help="How far back commit history should go (random 30-1825 days if not specified)"
)
@click.option(
    "--min-commits",
    default=5,
    type=click.IntRange(1, 100),
    help="Minimum commits per repository"
)
@click.option(
    "--max-commits",
    default=37,
    type=click.IntRange(1, 100),
    help="Maximum commits per repository"
)
@click.option(
    "--github-username", "-u",
    envvar="FABRICATE_GITHUB_USERNAME",
    help="GitHub username (auto-detected if not set)"
)
@click.option(
    "--work-dir", "-w",
    default="./fabricated_repos",
    help="Directory for temporary repository files"
)
@click.option(
    "--no-push",
    is_flag=True,
    help="Don't push to GitHub (local only)"
)
@click.option(
    "--cleanup",
    is_flag=True,
    help="Remove local files after pushing"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be created without actually creating"
)
def generate(
    anthropic_key: Optional[str],
    github_token: Optional[str],
    languages: tuple,
    repos: Optional[int],
    history_days: Optional[int],
    min_commits: int,
    max_commits: int,
    github_username: Optional[str],
    work_dir: str,
    no_push: bool,
    cleanup: bool,
    dry_run: bool
):
    """
    Generate a fabricated GitHub persona.
    
    Creates multiple repositories with AI-generated code and realistic
    commit histories, then pushes them to GitHub.
    
    Examples:
    
        # Basic usage with 3 Python repos
        fabricate generate -l python -r 3
        
        # Multiple languages, longer history
        fabricate generate -l python -l javascript -l go -r 10 -d 730
        
        # Local only (no GitHub push)
        fabricate generate --no-push -r 2
    """
    
    # Validate required credentials
    if not anthropic_key:
        console.print("[red]Error: Anthropic API key required[/red]")
        console.print("Set FABRICATE_ANTHROPIC_API_KEY or use --anthropic-key")
        sys.exit(1)
    
    if not github_token and not no_push:
        console.print("[red]Error: GitHub token required for pushing[/red]")
        console.print("Set FABRICATE_GITHUB_TOKEN or use --github-token")
        console.print("Or use --no-push for local-only generation")
        sys.exit(1)
    
    if min_commits > max_commits:
        console.print("[red]Error: min-commits cannot be greater than max-commits[/red]")
        sys.exit(1)
    
    # Generate random values if not specified
    import random
    if repos is None:
        repos = random.randint(1, 50)
        console.print(f"[dim]Randomly selected {repos} repositories to create[/dim]")
    
    if history_days is None:
        history_days = random.randint(30, 1825)
        console.print(f"[dim]Randomly selected {history_days} days of history (~{history_days // 30} months)[/dim]")
    
    languages_list = list(languages)
    
    if dry_run:
        console.print(Panel(
            f"[bold]Dry Run - Would Create:[/bold]\n\n"
            f"Repositories: [cyan]{repos}[/cyan]\n"
            f"Languages: [cyan]{', '.join(languages_list)}[/cyan]\n"
            f"History: [cyan]{history_days}[/cyan] days\n"
            f"Commits per repo: [cyan]{min_commits}-{max_commits}[/cyan]\n"
            f"Push to GitHub: [cyan]{not no_push}[/cyan]\n"
            f"Work directory: [cyan]{work_dir}[/cyan]",
            title="Dry Run",
            border_style="yellow"
        ))
        return
    
    # Run the fabrication
    try:
        generated = run_fabrication(
            anthropic_api_key=anthropic_key,
            github_token=github_token or "",
            languages=languages_list,
            num_repos=repos,
            history_days=history_days,
            min_commits=min_commits,
            max_commits=max_commits,
            github_username=github_username,
            work_dir=work_dir,
            push_to_github=not no_push,
            cleanup_local=cleanup
        )
        
        console.print(f"\n[green]Successfully created {len(generated)} repositories![/green]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Fabrication interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option(
    "--github-token", "-g",
    envvar="FABRICATE_GITHUB_TOKEN",
    required=True,
    help="GitHub personal access token"
)
def status(github_token: str):
    """
    Show status of the connected GitHub account.
    """
    from .github_client import GitHubClient
    
    try:
        client = GitHubClient(github_token)
        info = client.get_user_info()
        
        console.print(Panel(
            f"[bold]GitHub Account Status[/bold]\n\n"
            f"Username: [cyan]{info['login']}[/cyan]\n"
            f"Name: [cyan]{info.get('name', 'Not set')}[/cyan]\n"
            f"Email: [cyan]{info.get('email', 'Not public')}[/cyan]\n"
            f"Public repos: [cyan]{info['public_repos']}[/cyan]\n"
            f"Account created: [cyan]{info['created_at']}[/cyan]",
            title="Connected",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"[red]Error connecting to GitHub: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--github-token", "-g",
    envvar="FABRICATE_GITHUB_TOKEN",
    required=True,
    help="GitHub personal access token"
)
@click.option(
    "--prefix",
    help="Only list repos starting with this prefix"
)
def list_repos(github_token: str, prefix: Optional[str]):
    """
    List repositories in the connected GitHub account.
    """
    from .github_client import GitHubClient
    
    try:
        client = GitHubClient(github_token)
        repos = client.list_repos()
        
        if prefix:
            repos = [r for r in repos if r.startswith(prefix)]
        
        console.print(f"\n[bold]Repositories ({len(repos)}):[/bold]\n")
        for repo in sorted(repos):
            console.print(f"  • {repo}")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--github-token", "-g",
    envvar="FABRICATE_GITHUB_TOKEN",
    required=True,
    help="GitHub personal access token"
)
@click.argument("repo_names", nargs=-1, required=True)
@click.option(
    "--force", "-f",
    is_flag=True,
    help="Skip confirmation prompt"
)
def delete(github_token: str, repo_names: tuple, force: bool):
    """
    Delete repositories from GitHub.
    
    Use with caution! This permanently deletes repositories.
    
    Examples:
    
        fabricate delete my-repo-1 my-repo-2
        fabricate delete --force my-old-project
    """
    from .github_client import GitHubClient
    
    if not force:
        console.print(f"[yellow]About to delete {len(repo_names)} repositories:[/yellow]")
        for name in repo_names:
            console.print(f"  • {name}")
        
        if not click.confirm("\nAre you sure?"):
            console.print("[dim]Cancelled[/dim]")
            return
    
    try:
        client = GitHubClient(github_token)
        
        for name in repo_names:
            client.delete_repo(name)
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()

