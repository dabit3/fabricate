"""
Code generation using Anthropic's Claude API.
"""

import json
import random
from typing import Optional
from dataclasses import dataclass

import anthropic
from rich.console import Console

from .config import LANGUAGE_CONFIGS, COMPLEXITY_PROFILES, PROJECT_CATEGORIES

console = Console()


@dataclass
class GeneratedFile:
    """Represents a generated source file."""
    path: str
    content: str
    description: str


@dataclass
class GeneratedCommit:
    """Represents a generated commit with files and message."""
    message: str
    files: list[GeneratedFile]
    description: str


@dataclass
class GeneratedRepo:
    """Represents a fully generated repository."""
    name: str
    description: str
    language: str
    commits: list[GeneratedCommit]
    topics: list[str]


class CodeGenerator:
    """Generates code and repository content using Claude."""
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        
    def _call_claude(self, system: str, user: str, max_tokens: int = 4096) -> str:
        """Make a call to Claude API."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}]
        )
        return response.content[0].text
    
    def generate_repo_concept(
        self,
        language: str,
        complexity: str,
        name_style: str = "descriptive",
        existing_names: Optional[list[str]] = None
    ) -> dict:
        """Generate a unique repository concept."""
        
        existing_str = ""
        if existing_names:
            existing_str = f"\n\nAVOID these names that already exist: {', '.join(existing_names)}"
        
        category = random.choice(PROJECT_CATEGORIES)
        lang_config = LANGUAGE_CONFIGS.get(language, LANGUAGE_CONFIGS["python"])
        complexity_profile = COMPLEXITY_PROFILES[complexity]
        
        system = """You are a creative developer who comes up with unique, interesting project ideas.
You respond ONLY with valid JSON, no markdown formatting or explanation."""

        user = f"""Generate a unique {complexity} complexity {language} project concept.

Category hint: {category}
Complexity: {complexity_profile['description']}
Name style: {name_style} (descriptive=clear purpose, quirky=fun/memorable, technical=formal/precise)
{existing_str}

Respond with ONLY this JSON structure:
{{
    "name": "repo-name-in-kebab-case",
    "description": "A concise one-line description",
    "purpose": "What problem this solves or what it does",
    "topics": ["topic1", "topic2", "topic3"],
    "main_features": ["feature1", "feature2", "feature3"]
}}"""

        response = self._call_claude(system, user, max_tokens=500)
        
        # Parse JSON from response
        try:
            # Try to extract JSON if wrapped in code blocks
            if "```" in response:
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            return json.loads(response.strip())
        except json.JSONDecodeError:
            # Fallback concept
            return {
                "name": f"{language}-{category}-{random.randint(100, 999)}",
                "description": f"A {complexity} {language} {category} project",
                "purpose": f"Demonstrates {language} best practices",
                "topics": [language, category],
                "main_features": ["core functionality", "documentation"]
            }
    
    def generate_initial_commit(
        self,
        repo_concept: dict,
        language: str,
        complexity: str
    ) -> GeneratedCommit:
        """Generate the initial commit for a repository."""
        
        lang_config = LANGUAGE_CONFIGS.get(language, LANGUAGE_CONFIGS["python"])
        complexity_profile = COMPLEXITY_PROFILES[complexity]
        
        file_count = random.randint(*complexity_profile["file_count_range"])
        file_count = min(file_count, 5)  # Initial commit shouldn't be too large
        
        system = """You are an expert developer creating the initial structure of a new project.
You write clean, idiomatic code with appropriate comments.
You respond ONLY with valid JSON, no markdown formatting."""

        user = f"""Create the initial commit for this {language} project:

Name: {repo_concept['name']}
Description: {repo_concept['description']}
Purpose: {repo_concept['purpose']}
Features to implement: {repo_concept['main_features']}

Language config:
- Extension: {lang_config['extension']}
- Config files: {lang_config['config_files']}

Generate {file_count} files for the initial project structure.

Respond with ONLY this JSON:
{{
    "commit_message": "Initial commit message",
    "files": [
        {{
            "path": "relative/path/to/file.ext",
            "content": "full file content here",
            "description": "what this file does"
        }}
    ]
}}

IMPORTANT:
- Include a README.md
- Include appropriate config files for {language}
- Make the code realistic and functional
- Use proper formatting and indentation (use \\n for newlines, \\t for tabs)"""

        response = self._call_claude(system, user, max_tokens=8000)
        
        try:
            if "```" in response:
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            data = json.loads(response.strip())
            
            files = [
                GeneratedFile(
                    path=f["path"],
                    content=f["content"],
                    description=f.get("description", "")
                )
                for f in data["files"]
            ]
            
            return GeneratedCommit(
                message=data["commit_message"],
                files=files,
                description="Initial project structure"
            )
        except (json.JSONDecodeError, KeyError) as e:
            console.print(f"[yellow]Warning: Failed to parse initial commit response: {e}[/yellow]")
            # Return minimal fallback
            return self._generate_fallback_initial_commit(repo_concept, language, lang_config)
    
    def _generate_fallback_initial_commit(
        self,
        repo_concept: dict,
        language: str,
        lang_config: dict
    ) -> GeneratedCommit:
        """Generate a minimal fallback initial commit."""
        files = [
            GeneratedFile(
                path="README.md",
                content=f"# {repo_concept['name']}\n\n{repo_concept['description']}\n",
                description="Project readme"
            )
        ]
        return GeneratedCommit(
            message="Initial commit",
            files=files,
            description="Initial project structure"
        )
    
    def generate_subsequent_commit(
        self,
        repo_concept: dict,
        language: str,
        existing_files: list[str],
        commit_number: int,
        total_commits: int
    ) -> GeneratedCommit:
        """Generate a subsequent commit that builds on existing code."""
        
        lang_config = LANGUAGE_CONFIGS.get(language, LANGUAGE_CONFIGS["python"])
        
        # Determine commit type based on progress
        progress = commit_number / total_commits
        if progress < 0.3:
            commit_type = random.choice(["feature", "structure", "config"])
        elif progress < 0.7:
            commit_type = random.choice(["feature", "feature", "refactor", "fix"])
        else:
            commit_type = random.choice(["fix", "docs", "refactor", "polish"])
        
        system = """You are an expert developer working on an existing project.
You write clean, idiomatic code and meaningful commit messages.
You respond ONLY with valid JSON, no markdown formatting."""

        user = f"""Generate commit #{commit_number} of {total_commits} for this {language} project:

Project: {repo_concept['name']}
Description: {repo_concept['description']}
Features: {repo_concept['main_features']}

Existing files in repo:
{chr(10).join(f'- {f}' for f in existing_files)}

Commit type: {commit_type}
- feature: Add new functionality
- structure: Add new modules/organization
- config: Update configuration/dependencies
- refactor: Improve existing code
- fix: Bug fixes or corrections
- docs: Documentation updates
- polish: Small improvements, formatting

Respond with ONLY this JSON:
{{
    "commit_message": "type: descriptive commit message",
    "files": [
        {{
            "path": "path/to/file",
            "content": "complete file content",
            "description": "what changed"
        }}
    ]
}}

IMPORTANT:
- Generate 1-3 files per commit
- Either modify existing files or add new ones
- Make changes realistic and incremental
- Use conventional commit message format
- Content should be complete and valid {language} code"""

        response = self._call_claude(system, user, max_tokens=6000)
        
        try:
            if "```" in response:
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            data = json.loads(response.strip())
            
            files = [
                GeneratedFile(
                    path=f["path"],
                    content=f["content"],
                    description=f.get("description", "")
                )
                for f in data["files"]
            ]
            
            return GeneratedCommit(
                message=data["commit_message"],
                files=files,
                description=f"Commit {commit_number}: {commit_type}"
            )
        except (json.JSONDecodeError, KeyError) as e:
            console.print(f"[yellow]Warning: Failed to parse commit response: {e}[/yellow]")
            return GeneratedCommit(
                message=f"{commit_type}: update project",
                files=[
                    GeneratedFile(
                        path="README.md",
                        content=f"# {repo_concept['name']}\n\n{repo_concept['description']}\n\n## Updates\n\nCommit {commit_number}",
                        description="Updated readme"
                    )
                ],
                description=f"Fallback commit {commit_number}"
            )
    
    def generate_full_repo(
        self,
        language: str,
        complexity: str,
        num_commits: int,
        name_style: str = "descriptive",
        existing_names: Optional[list[str]] = None
    ) -> GeneratedRepo:
        """Generate a complete repository with all commits."""
        
        console.print(f"\n[bold cyan]Generating {complexity} {language} repository...[/bold cyan]")
        
        # Generate concept
        concept = self.generate_repo_concept(language, complexity, name_style, existing_names)
        console.print(f"  [green]✓[/green] Concept: {concept['name']}")
        
        commits = []
        existing_files = []
        
        # Generate initial commit
        initial = self.generate_initial_commit(concept, language, complexity)
        commits.append(initial)
        existing_files.extend([f.path for f in initial.files])
        console.print(f"  [green]✓[/green] Initial commit: {len(initial.files)} files")
        
        # Generate subsequent commits
        for i in range(2, num_commits + 1):
            commit = self.generate_subsequent_commit(
                concept, language, existing_files, i, num_commits
            )
            commits.append(commit)
            
            # Update existing files list
            for f in commit.files:
                if f.path not in existing_files:
                    existing_files.append(f.path)
            
            console.print(f"  [green]✓[/green] Commit {i}/{num_commits}: {commit.message[:50]}...")
        
        return GeneratedRepo(
            name=concept["name"],
            description=concept["description"],
            language=language,
            commits=commits,
            topics=concept.get("topics", [language])
        )

