"""
GitHub API client for creating and managing remote repositories.
"""

from pathlib import Path
from typing import Optional

from github import Github, GithubException, Auth
from git import Repo
from rich.console import Console

console = Console()


class GitHubClient:
    """Handles GitHub API operations."""
    
    def __init__(self, token: str, username: Optional[str] = None):
        auth = Auth.Token(token)
        self.github = Github(auth=auth)
        self.user = self.github.get_user()
        self.username = username or self.user.login
        self.token = token
        
    def create_remote_repo(
        self,
        name: str,
        description: str,
        private: bool = False,
        topics: Optional[list[str]] = None
    ) -> str:
        """
        Create a new repository on GitHub.
        
        Returns the clone URL.
        """
        try:
            repo = self.user.create_repo(
                name=name,
                description=description,
                private=private,
                auto_init=False,  # We'll push our own initial commit
                has_issues=True,
                has_wiki=False,
                has_downloads=True
            )
            
            console.print(f"  [green]✓[/green] Created remote repo: {repo.html_url}")
            
            # Set topics if provided
            if topics:
                # Sanitize topics (lowercase, alphanumeric with hyphens)
                clean_topics = [
                    t.lower().replace(" ", "-").replace("_", "-")[:50]
                    for t in topics
                ]
                try:
                    repo.replace_topics(clean_topics[:20])  # GitHub limits to 20 topics
                except GithubException:
                    pass  # Topics are optional, don't fail on this
            
            return repo.clone_url
            
        except GithubException as e:
            if e.status == 422 and "already exists" in str(e):
                console.print(f"  [yellow]⚠[/yellow] Repo {name} already exists, fetching...")
                repo = self.user.get_repo(name)
                return repo.clone_url
            raise
    
    def delete_repo(self, name: str) -> bool:
        """Delete a repository from GitHub."""
        try:
            repo = self.user.get_repo(name)
            repo.delete()
            console.print(f"  [red]✗[/red] Deleted remote repo: {name}")
            return True
        except GithubException as e:
            console.print(f"  [yellow]⚠[/yellow] Could not delete {name}: {e}")
            return False
    
    def push_repo(self, local_repo: Repo, remote_url: str) -> bool:
        """Push a local repository to GitHub."""
        try:
            # Create authenticated URL
            auth_url = remote_url.replace(
                "https://",
                f"https://{self.username}:{self.token}@"
            )
            
            # Add or update remote
            if "origin" in [r.name for r in local_repo.remotes]:
                local_repo.delete_remote("origin")
            
            origin = local_repo.create_remote("origin", auth_url)
            
            # Ensure we're on main branch
            if "main" not in [h.name for h in local_repo.heads]:
                local_repo.create_head("main", local_repo.head.commit)
            
            local_repo.heads.main.checkout()
            
            # Push to remote
            origin.push(refspec="main:main", force=True)
            
            # Clean up authenticated URL from remote
            local_repo.delete_remote("origin")
            local_repo.create_remote("origin", remote_url)
            
            console.print(f"  [green]✓[/green] Pushed to {remote_url}")
            return True
            
        except Exception as e:
            console.print(f"  [red]✗[/red] Push failed: {e}")
            return False
    
    def repo_exists(self, name: str) -> bool:
        """Check if a repository exists."""
        try:
            self.user.get_repo(name)
            return True
        except GithubException:
            return False
    
    def get_user_info(self) -> dict:
        """Get information about the authenticated user."""
        return {
            "login": self.user.login,
            "name": self.user.name,
            "email": self.user.email,
            "public_repos": self.user.public_repos,
            "created_at": self.user.created_at,
        }
    
    def list_repos(self) -> list[str]:
        """List all repositories for the authenticated user."""
        return [repo.name for repo in self.user.get_repos()]

