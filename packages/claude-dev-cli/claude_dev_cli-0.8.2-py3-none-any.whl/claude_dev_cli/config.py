"""Configuration management for Claude Dev CLI."""

import json
import os
from pathlib import Path
from typing import Dict, Optional, List
from pydantic import BaseModel, Field

from claude_dev_cli.secure_storage import SecureStorage


class ContextConfig(BaseModel):
    """Global context gathering configuration."""
    
    auto_context_default: bool = False  # Default for --auto-context flag
    max_file_lines: int = 1000  # Maximum lines per file in context
    max_related_files: int = 5  # Maximum related files to include
    max_diff_lines: int = 200  # Maximum lines of diff to include
    include_git: bool = True  # Include git context by default
    include_dependencies: bool = True  # Include dependencies by default
    include_tests: bool = True  # Include test files by default


class APIConfig(BaseModel):
    """Configuration for a Claude API key."""
    
    name: str
    api_key: str
    description: Optional[str] = None
    default: bool = False


class ProjectProfile(BaseModel):
    """Project-specific configuration."""
    
    name: str
    api_config: str  # Name of the API config to use
    system_prompt: Optional[str] = None
    allowed_commands: List[str] = Field(default_factory=lambda: ["all"])
    
    # Project memory - preferences and patterns
    auto_context: bool = False  # Default value for --auto-context flag
    coding_style: Optional[str] = None  # Preferred coding style
    test_framework: Optional[str] = None  # Preferred test framework
    preferences: Dict[str, str] = Field(default_factory=dict)  # Custom preferences
    
    # Context gathering configuration
    max_context_files: int = 5  # Maximum number of related files to include
    max_diff_lines: int = 200  # Maximum lines of diff to include
    max_file_lines: int = 1000  # Maximum lines per file in context
    include_tests_by_default: bool = True  # Include test files in review context
    context_depth: int = 2  # How deep to search for related modules


class Config:
    """Manages configuration for Claude Dev CLI."""
    
    def __init__(self) -> None:
        """Initialize configuration."""
        # Determine home directory (respects HOME env var for testing)
        home = Path(os.environ.get("HOME", str(Path.home())))
        
        self.config_dir = home / ".claude-dev-cli"
        self.config_file = self.config_dir / "config.json"
        self.usage_log = self.config_dir / "usage.jsonl"
        
        self._ensure_config_dir()
        self._data: Dict = self._load_config()
        
        # Initialize secure storage
        self.secure_storage = SecureStorage(self.config_dir)
        
        # Auto-migrate if plaintext keys exist
        self._auto_migrate_keys()
    
    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.usage_log.touch(exist_ok=True)
    
    def _load_config(self) -> Dict:
        """Load configuration from file."""
        if not self.config_file.exists():
            default_config = {
                "api_configs": [],
                "project_profiles": [],
                "default_model": "claude-3-5-sonnet-20241022",
                "max_tokens": 4096,
                "context": ContextConfig().model_dump(),
            }
            self._save_config(default_config)
            return default_config
        
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def _save_config(self, data: Optional[Dict] = None) -> None:
        """Save configuration to file."""
        if data is None:
            data = self._data
        
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _auto_migrate_keys(self) -> None:
        """Automatically migrate plaintext API keys to secure storage."""
        api_configs = self._data.get("api_configs", [])
        migrated = False
        
        for config in api_configs:
            if "api_key" in config and config["api_key"]:
                # Migrate this key to secure storage
                self.secure_storage.store_key(config["name"], config["api_key"])
                # Remove from plaintext config
                config["api_key"] = ""  # Empty string indicates key is in secure storage
                migrated = True
        
        if migrated:
            self._save_config()
    
    def add_api_config(
        self,
        name: str,
        api_key: Optional[str] = None,
        description: Optional[str] = None,
        make_default: bool = False
    ) -> None:
        """Add a new API configuration."""
        # Get API key from env if not provided
        if api_key is None:
            env_var = f"{name.upper()}_ANTHROPIC_API_KEY"
            api_key = os.environ.get(env_var)
            if not api_key:
                raise ValueError(
                    f"API key not provided and {env_var} environment variable not set"
                )
        
        # Check if name already exists
        api_configs = self._data.get("api_configs", [])
        for config in api_configs:
            if config["name"] == name:
                raise ValueError(f"API config with name '{name}' already exists")
        
        # Store API key in secure storage
        self.secure_storage.store_key(name, api_key)
        
        # If this is the first config or make_default is True, set as default
        if make_default or not api_configs:
            for config in api_configs:
                config["default"] = False
        
        # Store metadata without the actual key (empty string indicates secure storage)
        api_config = APIConfig(
            name=name,
            api_key="",  # Empty string indicates key is in secure storage
            description=description,
            default=make_default or not api_configs
        )
        
        api_configs.append(api_config.model_dump())
        self._data["api_configs"] = api_configs
        self._save_config()
    
    def get_api_config(self, name: Optional[str] = None) -> Optional[APIConfig]:
        """Get API configuration by name or default."""
        api_configs = self._data.get("api_configs", [])
        
        config_data = None
        if name:
            for config in api_configs:
                if config["name"] == name:
                    config_data = config
                    break
        else:
            # Return default
            for config in api_configs:
                if config.get("default", False):
                    config_data = config
                    break
        
        if not config_data:
            return None
        
        # Retrieve actual API key from secure storage
        api_key = self.secure_storage.get_key(config_data["name"])
        if not api_key:
            # Fallback to plaintext if not in secure storage (shouldn't happen after migration)
            api_key = config_data.get("api_key", "")
        
        # Return config with actual key
        return APIConfig(
            name=config_data["name"],
            api_key=api_key,
            description=config_data.get("description"),
            default=config_data.get("default", False)
        )
    
    def list_api_configs(self) -> List[APIConfig]:
        """List all API configurations."""
        configs = []
        for c in self._data.get("api_configs", []):
            # Retrieve actual API key from secure storage
            api_key = self.secure_storage.get_key(c["name"])
            if not api_key:
                # Fallback to plaintext
                api_key = c.get("api_key", "")
            
            configs.append(APIConfig(
                name=c["name"],
                api_key=api_key,
                description=c.get("description"),
                default=c.get("default", False)
            ))
        return configs
    
    def add_project_profile(
        self,
        name: str,
        api_config: str,
        system_prompt: Optional[str] = None,
        allowed_commands: Optional[List[str]] = None
    ) -> None:
        """Add a project profile."""
        profiles = self._data.get("project_profiles", [])
        
        profile = ProjectProfile(
            name=name,
            api_config=api_config,
            system_prompt=system_prompt,
            allowed_commands=allowed_commands or ["all"]
        )
        
        profiles.append(profile.model_dump())
        self._data["project_profiles"] = profiles
        self._save_config()
    
    def get_project_profile(self, cwd: Optional[Path] = None) -> Optional[ProjectProfile]:
        """Get project profile for current directory."""
        if cwd is None:
            cwd = Path.cwd()
        
        # Check for .claude-dev-cli file in current or parent directories
        current = cwd
        while current != current.parent:
            config_file = current / ".claude-dev-cli"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    return ProjectProfile(**data)
            current = current.parent
        
        return None
    
    def get_model(self) -> str:
        """Get default model."""
        return self._data.get("default_model", "claude-3-5-sonnet-20241022")
    
    def get_max_tokens(self) -> int:
        """Get default max tokens."""
        return self._data.get("max_tokens", 4096)
    
    def get_context_config(self) -> ContextConfig:
        """Get context gathering configuration."""
        context_data = self._data.get("context", {})
        return ContextConfig(**context_data) if context_data else ContextConfig()
