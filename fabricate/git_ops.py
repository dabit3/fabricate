"""
Git operations for creating and managing repositories.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from git import Repo, Actor
from rich.console import Console

from .generator import GeneratedCommit, GeneratedRepo

console = Console()


class GitOperations:
    """Handles local git repository operations."""
    
    def __init__(self, work_dir: str, author_name: str, author_email: str):
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.author = Actor(author_name, author_email)
        
    def create_repo(self, name: str) -> Repo:
        """Create a new git repository."""
        repo_path = self.work_dir / name
        
        # Clean up if exists
        if repo_path.exists():
            shutil.rmtree(repo_path)
        
        repo_path.mkdir(parents=True)
        repo = Repo.init(repo_path)
        
        # Set initial branch to main
        if repo.head.is_valid():
            repo.head.reference = repo.create_head("main")
        
        return repo
    
    def write_files(self, repo: Repo, commit: GeneratedCommit) -> list[str]:
        """Write files from a commit to the repository."""
        repo_path = Path(repo.working_dir)
        written_files = []
        
        for file in commit.files:
            file_path = repo_path / file.path
            
            # Create parent directories
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            file_path.write_text(file.content)
            written_files.append(file.path)
        
        return written_files
    
    def create_commit(
        self,
        repo: Repo,
        commit: GeneratedCommit,
        commit_date: datetime,
        author_name: Optional[str] = None,
        author_email: Optional[str] = None
    ) -> str:
        """Create a commit with the given files and message."""
        
        # Write files
        written_files = self.write_files(repo, commit)
        
        # Stage files
        repo.index.add(written_files)
        
        # Create author with custom name/email if provided
        if author_name and author_email:
            author = Actor(author_name, author_email)
        else:
            author = self.author
        
        # Format date for git
        date_str = commit_date.strftime("%Y-%m-%d %H:%M:%S")
        
        # Set environment for commit date
        os.environ["GIT_AUTHOR_DATE"] = date_str
        os.environ["GIT_COMMITTER_DATE"] = date_str
        
        # Create commit
        commit_obj = repo.index.commit(
            commit.message,
            author=author,
            committer=author,
            author_date=date_str,
            commit_date=date_str
        )
        
        # Clean up environment
        if "GIT_AUTHOR_DATE" in os.environ:
            del os.environ["GIT_AUTHOR_DATE"]
        if "GIT_COMMITTER_DATE" in os.environ:
            del os.environ["GIT_COMMITTER_DATE"]
        
        return commit_obj.hexsha
    
    def apply_generated_repo(
        self,
        generated_repo: GeneratedRepo,
        commit_dates: list[datetime],
        author_name: Optional[str] = None,
        author_email: Optional[str] = None
    ) -> Repo:
        """Apply a generated repository to disk with proper commit history."""
        
        console.print(f"\n[bold blue]Creating local repo: {generated_repo.name}[/bold blue]")
        
        # Create the repository
        repo = self.create_repo(generated_repo.name)
        
        # Ensure we have a main branch
        # For initial commit, we'll create the branch after
        
        # Apply each commit
        for i, (commit, date) in enumerate(zip(generated_repo.commits, commit_dates)):
            sha = self.create_commit(
                repo, commit, date,
                author_name=author_name,
                author_email=author_email
            )
            console.print(f"  [dim]Commit {i+1}:[/dim] {sha[:8]} - {commit.message[:50]}")
            
            # After first commit, ensure we're on main branch
            if i == 0:
                try:
                    repo.head.reference = repo.create_head("main", repo.head.commit)
                except:
                    pass  # Branch might already exist
        
        return repo
    
    def get_repo_path(self, name: str) -> Path:
        """Get the path to a repository."""
        return self.work_dir / name
    
    def cleanup_repo(self, name: str) -> None:
        """Remove a repository from the work directory."""
        repo_path = self.work_dir / name
        if repo_path.exists():
            shutil.rmtree(repo_path)
            console.print(f"[dim]Cleaned up: {name}[/dim]")


def generate_commit_dates(
    num_commits: int,
    history_days: int,
    repo_index: int,
    total_repos: int
) -> list[datetime]:
    """
    Generate realistic commit dates distributed across the history period.
    
    Each repo starts on a random day within the history_days timeframe.
    """
    import random
    from datetime import timedelta
    
    now = datetime.now()
    
    # Pick a completely random start date within the history period
    # The repo can start anywhere from (history_days ago) to (7 days ago)
    min_start_days_ago = 7  # At least a week old
    max_start_days_ago = history_days
    
    random_days_ago = random.randint(min_start_days_ago, max_start_days_ago)
    start_date = now - timedelta(days=random_days_ago)
    
    # Add hour-level randomness to avoid all repos starting at midnight
    start_date = start_date + timedelta(
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )
    
    # Calculate duration for this repo
    duration = now - start_date
    
    dates = []
    for i in range(num_commits):
        # Base progress through the repo's timeline
        progress = i / max(num_commits - 1, 1)
        
        # Add some randomness to simulate irregular commit patterns
        # Sometimes developers commit in bursts
        if random.random() < 0.3:  # 30% chance of being part of a "burst"
            jitter_hours = random.randint(-6, 6)
        else:
            jitter_hours = random.randint(-48, 48)
        
        commit_time = start_date + (duration * progress) + timedelta(hours=jitter_hours)
        
        # Ensure commit time is valid
        if commit_time > now:
            commit_time = now - timedelta(hours=random.randint(1, 24))
        if commit_time < start_date:
            commit_time = start_date + timedelta(hours=random.randint(1, 24))
        
        dates.append(commit_time)
    
    # Sort dates to ensure chronological order
    dates.sort()
    
    return dates

