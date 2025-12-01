"""
Configuration models for Fabricate.
"""

from datetime import datetime, timedelta
from typing import Optional
import random

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class RepoConfig(BaseModel):
    """Configuration for a single repository."""
    
    name: str
    description: str
    language: str
    complexity: str = Field(description="low, medium, high")
    num_commits: int = Field(ge=5, le=37)
    is_private: bool = False
    topics: list[str] = Field(default_factory=list)
    

class PersonaConfig(BaseModel):
    """Configuration for the GitHub persona to fabricate."""
    
    languages: list[str] = Field(
        default=["python", "typescript", "rust", "solidity"],
        description="Programming languages to use across repos"
    )
    num_repos: int = Field(
        default_factory=lambda: random.randint(1, 50),
        ge=1,
        le=50,
        description="Number of repositories to create (random 1-50 if not specified)"
    )
    history_days: int = Field(
        default_factory=lambda: random.randint(30, 1825),
        ge=30,
        le=1825,
        description="How far back the commit history should go (random 30-1825 days if not specified)"
    )
    min_commits_per_repo: int = Field(default=5, ge=1)
    max_commits_per_repo: int = Field(default=37, le=100)
    repo_name_style: str = Field(
        default="descriptive",
        description="Style for repo names: descriptive, quirky, technical"
    )
    include_readme: bool = True
    include_license: bool = True
    license_type: str = "MIT"
    
    def generate_commit_count(self) -> int:
        """Generate a random commit count within configured bounds."""
        return random.randint(self.min_commits_per_repo, self.max_commits_per_repo)
    
    def generate_commit_date(self, repo_start_date: datetime, commit_index: int, total_commits: int) -> datetime:
        """Generate a commit date that progresses through the repo's history."""
        now = datetime.now()
        repo_duration = now - repo_start_date
        
        # Distribute commits somewhat evenly with some randomness
        progress = commit_index / max(total_commits - 1, 1)
        base_offset = repo_duration * progress
        
        # Add some randomness (up to 2 days variance)
        jitter = timedelta(hours=random.randint(-48, 48))
        
        commit_date = repo_start_date + base_offset + jitter
        
        # Ensure we don't go past now
        if commit_date > now:
            commit_date = now - timedelta(hours=random.randint(1, 24))
            
        return commit_date


class FabricateSettings(BaseSettings):
    """Environment-based settings for Fabricate."""
    
    anthropic_api_key: str = Field(description="Anthropic API key for code generation")
    github_token: str = Field(description="GitHub personal access token")
    github_username: Optional[str] = Field(default=None, description="GitHub username (auto-detected if not set)")
    work_dir: str = Field(default="./fabricated_repos", description="Directory for temporary repo work")
    
    class Config:
        env_prefix = "FABRICATE_"
        env_file = ".env"
        extra = "ignore"


# Repository complexity profiles
COMPLEXITY_PROFILES = {
    "low": {
        "file_count_range": (2, 5),
        "lines_per_file_range": (20, 100),
        "description": "Simple utility or script",
    },
    "medium": {
        "file_count_range": (5, 15),
        "lines_per_file_range": (50, 300),
        "description": "Small library or tool",
    },
    "high": {
        "file_count_range": (10, 30),
        "lines_per_file_range": (100, 500),
        "description": "Complex application or framework",
    },
}

# Language-specific configurations
LANGUAGE_CONFIGS = {
    "python": {
        "extension": ".py",
        "config_files": ["requirements.txt", "setup.py", "pyproject.toml"],
        "common_dirs": ["src", "tests", "docs"],
        "package_manager": "pip",
    },
    "javascript": {
        "extension": ".js",
        "config_files": ["package.json", ".eslintrc.json"],
        "common_dirs": ["src", "lib", "test", "dist"],
        "package_manager": "npm",
    },
    "typescript": {
        "extension": ".ts",
        "config_files": ["package.json", "tsconfig.json", ".eslintrc.json"],
        "common_dirs": ["src", "lib", "test", "dist"],
        "package_manager": "npm",
    },
    "rust": {
        "extension": ".rs",
        "config_files": ["Cargo.toml"],
        "common_dirs": ["src", "tests", "benches"],
        "package_manager": "cargo",
    },
    "go": {
        "extension": ".go",
        "config_files": ["go.mod", "go.sum"],
        "common_dirs": ["cmd", "pkg", "internal"],
        "package_manager": "go mod",
    },
    "ruby": {
        "extension": ".rb",
        "config_files": ["Gemfile", ".rubocop.yml"],
        "common_dirs": ["lib", "spec", "bin"],
        "package_manager": "bundler",
    },
    "java": {
        "extension": ".java",
        "config_files": ["pom.xml", "build.gradle"],
        "common_dirs": ["src/main/java", "src/test/java"],
        "package_manager": "maven",
    },
    "c": {
        "extension": ".c",
        "config_files": ["Makefile", "CMakeLists.txt"],
        "common_dirs": ["src", "include", "tests"],
        "package_manager": "make",
    },
    "cpp": {
        "extension": ".cpp",
        "config_files": ["Makefile", "CMakeLists.txt"],
        "common_dirs": ["src", "include", "tests"],
        "package_manager": "cmake",
    },
}

# Project idea templates by category
PROJECT_CATEGORIES = [
    "cli_tool",
    "web_api",
    "library",
    "data_processing",
    "automation",
    "game",
    "visualization",
    "testing_tool",
    "devops",
    "machine_learning",
]

