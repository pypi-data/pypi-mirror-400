"""Command-line interface for Claude Dev CLI."""

import os
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from claude_dev_cli import __version__
from claude_dev_cli.config import Config
from claude_dev_cli.core import ClaudeClient
from claude_dev_cli.commands import (
    generate_tests,
    code_review,
    debug_code,
    generate_docs,
    refactor_code,
    git_commit_message,
)
from claude_dev_cli.usage import UsageTracker
from claude_dev_cli import toon_utils
from claude_dev_cli.plugins import load_plugins
from claude_dev_cli.history import ConversationHistory, Conversation
from claude_dev_cli.template_manager import TemplateManager, Template

console = Console()


@click.group()
@click.version_option(version=__version__)
@click.pass_context
def main(ctx: click.Context) -> None:
    """Claude Dev CLI - AI-powered development assistant with multi-API routing."""
    ctx.ensure_object(dict)
    ctx.obj['console'] = console


# Load plugins after main group is defined
# Silently load plugins - they'll register their commands
try:
    plugins = load_plugins()
    for plugin in plugins:
        plugin.register_commands(main)
except Exception:
    # Don't fail if plugins can't load - continue without them
    pass


@main.command()
@click.argument('prompt', required=False)
@click.option('-f', '--file', type=click.Path(exists=True), help='Include file content in prompt')
@click.option('-s', '--system', help='System prompt')
@click.option('-a', '--api', help='API config to use')
@click.option('-m', '--model', help='Claude model to use')
@click.option('--stream/--no-stream', default=True, help='Stream response')
@click.option('--auto-context', is_flag=True, help='Automatically include git, dependencies, and related files')
@click.pass_context
def ask(
    ctx: click.Context,
    prompt: Optional[str],
    file: Optional[str],
    system: Optional[str],
    api: Optional[str],
    model: Optional[str],
    stream: bool,
    auto_context: bool
) -> None:
    """Ask Claude a question (single-shot mode)."""
    console = ctx.obj['console']
    
    # Build prompt
    prompt_parts = []
    
    # Gather context if requested
    if auto_context and file:
        from claude_dev_cli.context import ContextGatherer
        
        with console.status("[bold blue]Gathering context..."):
            gatherer = ContextGatherer()
            context = gatherer.gather_for_file(Path(file))
            context_info = context.format_for_prompt()
        
        console.print("[dim]✓ Context gathered[/dim]")
        prompt_parts.append(context_info)
    elif file:
        with open(file, 'r') as f:
            file_content = f.read()
            prompt_parts.append(f"File: {file}\n\n{file_content}\n\n")
    
    # Read from stdin if available
    if not sys.stdin.isatty():
        stdin_content = sys.stdin.read().strip()
        if stdin_content:
            prompt_parts.append(f"{stdin_content}\n\n")
    
    if prompt:
        prompt_parts.append(prompt)
    elif not prompt_parts:
        console.print("[red]Error: No prompt provided[/red]")
        sys.exit(1)
    
    full_prompt = ''.join(prompt_parts)
    
    try:
        client = ClaudeClient(api_config_name=api)
        
        if stream:
            for chunk in client.call_streaming(
                full_prompt,
                system_prompt=system,
                model=model
            ):
                console.print(chunk, end='')
            console.print()  # New line at end
        else:
            response = client.call(full_prompt, system_prompt=system, model=model)
            md = Markdown(response)
            console.print(md)
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option('-a', '--api', help='API config to use')
@click.option('--continue', 'continue_conversation', is_flag=True, 
              help='Continue the last conversation')
@click.option('--save/--no-save', default=True, help='Save conversation history')
@click.pass_context
def interactive(
    ctx: click.Context, 
    api: Optional[str],
    continue_conversation: bool,
    save: bool
) -> None:
    """Start interactive chat mode."""
    console = ctx.obj['console']
    
    # Setup conversation history
    config = Config()
    history_dir = config.config_dir / "history"
    conv_history = ConversationHistory(history_dir)
    
    # Load or create conversation
    if continue_conversation:
        conversation = conv_history.get_latest_conversation()
        if conversation:
            console.print(f"[green]↶ Continuing conversation from {conversation.updated_at.strftime('%Y-%m-%d %H:%M')}[/green]")
            console.print(f"[dim]Messages: {len(conversation.messages)}[/dim]\n")
        else:
            console.print("[yellow]No previous conversation found, starting new one[/yellow]\n")
            conversation = Conversation()
    else:
        conversation = Conversation()
    
    console.print(Panel.fit(
        "Claude Dev CLI - Interactive Mode\n"
        "Type 'exit' or 'quit' to end\n"
        "Type 'clear' to reset conversation",
        title="Welcome",
        border_style="blue"
    ))
    
    try:
        client = ClaudeClient(api_config_name=api)
        response_buffer = []
        
        while True:
            try:
                user_input = console.input("\n[bold cyan]You:[/bold cyan] ").strip()
                
                if user_input.lower() in ['exit', 'quit']:
                    if save and conversation.messages:
                        conv_history.save_conversation(conversation)
                        console.print(f"\n[dim]💾 Saved conversation: {conversation.conversation_id}[/dim]")
                    break
                
                if user_input.lower() == 'clear':
                    conversation = Conversation()
                    console.print("[yellow]Conversation cleared[/yellow]")
                    continue
                
                if not user_input:
                    continue
                
                # Add user message to history
                conversation.add_message("user", user_input)
                
                # Get response
                console.print("\n[bold green]Claude:[/bold green] ", end='')
                response_buffer = []
                for chunk in client.call_streaming(user_input):
                    console.print(chunk, end='')
                    response_buffer.append(chunk)
                console.print()
                
                # Add assistant response to history
                full_response = ''.join(response_buffer)
                conversation.add_message("assistant", full_response)
                
                # Auto-save periodically
                if save and len(conversation.messages) % 10 == 0:
                    conv_history.save_conversation(conversation)
                
            except KeyboardInterrupt:
                console.print("\n\n[yellow]Interrupted. Type 'exit' to quit.[/yellow]")
                continue
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if save and conversation.messages:
            conv_history.save_conversation(conversation)
        sys.exit(1)


@main.group()
def completion() -> None:
    """Shell completion installation."""
    pass


@completion.command('install')
@click.option('--shell', type=click.Choice(['bash', 'zsh', 'fish', 'auto']), default='auto',
              help='Shell type (auto-detects if not specified)')
@click.pass_context
def completion_install(ctx: click.Context, shell: str) -> None:
    """Install shell completion for cdc command."""
    console = ctx.obj['console']
    
    # Auto-detect shell if needed
    if shell == 'auto':
        shell_path = os.environ.get('SHELL', '')
        if 'zsh' in shell_path:
            shell = 'zsh'
        elif 'bash' in shell_path:
            shell = 'bash'
        elif 'fish' in shell_path:
            shell = 'fish'
        else:
            console.print("[red]Could not auto-detect shell[/red]")
            console.print("Please specify: --shell bash|zsh|fish")
            sys.exit(1)
    
    console.print(f"[cyan]Installing completion for {shell}...[/cyan]\n")
    
    if shell == 'zsh':
        console.print("Add this to your ~/.zshrc:\n")
        console.print("[yellow]eval \"$(_CDC_COMPLETE=zsh_source cdc)\"[/yellow]\n")
        console.print("Then run: [cyan]source ~/.zshrc[/cyan]")
    elif shell == 'bash':
        console.print("Add this to your ~/.bashrc:\n")
        console.print("[yellow]eval \"$(_CDC_COMPLETE=bash_source cdc)\"[/yellow]\n")
        console.print("Then run: [cyan]source ~/.bashrc[/cyan]")
    elif shell == 'fish':
        console.print("Add this to ~/.config/fish/completions/cdc.fish:\n")
        console.print("[yellow]_CDC_COMPLETE=fish_source cdc | source[/yellow]\n")
        console.print("Then reload: [cyan]exec fish[/cyan]")
    
    console.print("\n[green]✓[/green] Instructions displayed above")
    console.print("[dim]Completion will provide command and option suggestions[/dim]")


@completion.command('generate')
@click.option('--shell', type=click.Choice(['bash', 'zsh', 'fish']), required=True,
              help='Shell type')
@click.pass_context
def completion_generate(ctx: click.Context, shell: str) -> None:
    """Generate completion script for shell."""
    import subprocess
    import sys
    
    env_var = f"_CDC_COMPLETE={shell}_source"
    result = subprocess.run(
        [sys.executable, '-m', 'claude_dev_cli.cli'],
        env={**os.environ, '_CDC_COMPLETE': f'{shell}_source'},
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        click.echo(result.stdout)
    else:
        ctx.obj['console'].print(f"[red]Error generating completion: {result.stderr}[/red]")
        sys.exit(1)


@main.group()
def history() -> None:
    """Manage conversation history."""
    pass


@history.command('list')
@click.option('-n', '--limit', type=int, default=10, help='Number of conversations to show')
@click.option('-s', '--search', help='Search conversations')
@click.pass_context
def history_list(ctx: click.Context, limit: int, search: Optional[str]) -> None:
    """List conversation history."""
    console = ctx.obj['console']
    config = Config()
    conv_history = ConversationHistory(config.config_dir / "history")
    
    conversations = conv_history.list_conversations(limit=limit, search_query=search)
    
    if not conversations:
        console.print("[yellow]No conversations found[/yellow]")
        return
    
    for conv in conversations:
        summary = conv.get_summary(80)
        console.print(f"\n[cyan]{conv.conversation_id}[/cyan]")
        console.print(f"[dim]{conv.updated_at.strftime('%Y-%m-%d %H:%M')} | {len(conv.messages)} messages[/dim]")
        console.print(f"  {summary}")


@history.command('export')
@click.argument('conversation_id')
@click.option('--format', type=click.Choice(['markdown', 'json']), default='markdown')
@click.option('-o', '--output', type=click.Path(), help='Output file')
@click.pass_context
def history_export(ctx: click.Context, conversation_id: str, format: str, output: Optional[str]) -> None:
    """Export a conversation."""
    console = ctx.obj['console']
    config = Config()
    conv_history = ConversationHistory(config.config_dir / "history")
    
    content = conv_history.export_conversation(conversation_id, format)
    if not content:
        console.print(f"[red]Conversation {conversation_id} not found[/red]")
        sys.exit(1)
    
    if output:
        Path(output).write_text(content)
        console.print(f"[green]✓[/green] Exported to {output}")
    else:
        click.echo(content)


@main.group()
def config() -> None:
    """Manage configuration."""
    pass


@config.command('add')
@click.argument('name')
@click.option('--api-key', help='API key (or set {NAME}_ANTHROPIC_API_KEY env var)')
@click.option('--description', help='Description of this API config')
@click.option('--default', is_flag=True, help='Set as default API config')
@click.pass_context
def config_add(
    ctx: click.Context,
    name: str,
    api_key: Optional[str],
    description: Optional[str],
    default: bool
) -> None:
    """Add a new API configuration."""
    console = ctx.obj['console']
    
    try:
        config = Config()
        config.add_api_config(
            name=name,
            api_key=api_key,
            description=description,
            make_default=default
        )
        console.print(f"[green]✓[/green] Added API config: {name}")
        
        # Show storage method
        storage_method = config.secure_storage.get_storage_method()
        if storage_method == "keyring":
            console.print("[dim]🔐 Stored securely in system keyring[/dim]")
        else:
            console.print("[dim]🔒 Stored in encrypted file (keyring unavailable)[/dim]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@config.command('migrate-keys')
@click.pass_context
def config_migrate_keys(ctx: click.Context) -> None:
    """Manually migrate API keys to secure storage."""
    console = ctx.obj['console']
    
    try:
        config = Config()
        
        # Check if any keys need migration
        api_configs = config._data.get("api_configs", [])
        plaintext_keys = {c["name"]: c.get("api_key", "") 
                         for c in api_configs 
                         if c.get("api_key")}
        
        if not plaintext_keys:
            console.print("[green]✓[/green] All keys are already in secure storage.")
            storage_method = config.secure_storage.get_storage_method()
            console.print(f"[dim]Using: {storage_method}[/dim]")
            return
        
        console.print(f"[yellow]Found {len(plaintext_keys)} plaintext key(s)[/yellow]")
        console.print("Migrating to secure storage...\n")
        
        # Trigger migration
        config._auto_migrate_keys()
        
        console.print(f"[green]✓[/green] Migrated {len(plaintext_keys)} key(s) to secure storage.")
        storage_method = config.secure_storage.get_storage_method()
        console.print(f"[dim]Using: {storage_method}[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@config.command('list')
@click.pass_context
def config_list(ctx: click.Context) -> None:
    """List all API configurations."""
    console = ctx.obj['console']
    
    config = Config()
    api_configs = config.list_api_configs()
    
    if not api_configs:
        console.print("[yellow]No API configurations found.[/yellow]")
        console.print("Run 'cdc config add' to add one.")
        return
    
    # Show storage method
    storage_method = config.secure_storage.get_storage_method()
    storage_display = {
        "keyring": "🔐 System Keyring (Secure)",
        "encrypted_file": "🔒 Encrypted File (Fallback)"
    }.get(storage_method, storage_method)
    console.print(f"\n[dim]Storage: {storage_display}[/dim]\n")
    
    for cfg in api_configs:
        default_marker = " [bold green](default)[/bold green]" if cfg.default else ""
        console.print(f"• {cfg.name}{default_marker}")
        if cfg.description:
            console.print(f"  {cfg.description}")
        console.print(f"  API Key: {cfg.api_key[:15]}...")


@main.group()
def generate() -> None:
    """Generate code, tests, and documentation."""
    pass


@generate.command('tests')
@click.argument('file_path', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), help='Output file path')
@click.option('-a', '--api', help='API config to use')
@click.option('-i', '--interactive', is_flag=True, help='Interactive refinement mode')
@click.option('--auto-context', is_flag=True, help='Include dependencies and related files')
@click.pass_context
def gen_tests(
    ctx: click.Context,
    file_path: str,
    output: Optional[str],
    api: Optional[str],
    interactive: bool,
    auto_context: bool
) -> None:
    """Generate pytest tests for a Python file."""
    console = ctx.obj['console']
    
    try:
        if auto_context:
            from claude_dev_cli.context import ContextGatherer
            
            with console.status("[bold blue]Gathering context..."):
                gatherer = ContextGatherer()
                context = gatherer.gather_for_file(Path(file_path), include_git=False)
                context_info = context.format_for_prompt()
            
            console.print("[dim]✓ Context gathered (dependencies, related files)[/dim]")
            
            # Use context-aware test generation
            client = ClaudeClient(api_config_name=api)
            enhanced_prompt = f"{context_info}\n\nPlease generate comprehensive pytest tests for the main file, including fixtures, edge cases, and proper mocking where needed."
            result = client.call(enhanced_prompt)
        else:
            with console.status("[bold blue]Generating tests..."):
                result = generate_tests(file_path, api_config_name=api)
        
        if interactive:
            # Show initial result
            console.print("\n[bold]Initial Tests:[/bold]\n")
            console.print(result)
            
            # Interactive refinement loop
            client = ClaudeClient(api_config_name=api)
            conversation_context = [result]
            
            while True:
                console.print("\n[dim]Commands: 'save' to save and exit, 'exit' to discard, or ask for changes[/dim]")
                user_input = console.input("[cyan]You:[/cyan] ").strip()
                
                if user_input.lower() == 'exit':
                    console.print("[yellow]Discarded changes[/yellow]")
                    return
                
                if user_input.lower() == 'save':
                    result = conversation_context[-1]
                    break
                
                if not user_input:
                    continue
                
                # Get refinement
                refinement_prompt = f"Previous tests:\n\n{conversation_context[-1]}\n\nUser request: {user_input}\n\nProvide the updated tests."
                
                console.print("\n[bold green]Claude:[/bold green] ", end='')
                response_parts = []
                for chunk in client.call_streaming(refinement_prompt):
                    console.print(chunk, end='')
                    response_parts.append(chunk)
                console.print()
                
                result = ''.join(response_parts)
                conversation_context.append(result)
        
        if output:
            with open(output, 'w') as f:
                f.write(result)
            console.print(f"\n[green]✓[/green] Tests saved to: {output}")
        elif not interactive:
            console.print(result)
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@generate.command('docs')
@click.argument('file_path', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), help='Output file path')
@click.option('-a', '--api', help='API config to use')
@click.option('-i', '--interactive', is_flag=True, help='Interactive refinement mode')
@click.option('--auto-context', is_flag=True, help='Include dependencies and related files')
@click.pass_context
def gen_docs(
    ctx: click.Context,
    file_path: str,
    output: Optional[str],
    api: Optional[str],
    interactive: bool,
    auto_context: bool
) -> None:
    """Generate documentation for a Python file."""
    console = ctx.obj['console']
    
    try:
        if auto_context:
            from claude_dev_cli.context import ContextGatherer
            
            with console.status("[bold blue]Gathering context..."):
                gatherer = ContextGatherer()
                context = gatherer.gather_for_file(Path(file_path), include_git=False)
                context_info = context.format_for_prompt()
            
            console.print("[dim]✓ Context gathered (dependencies, related files)[/dim]")
            
            # Use context-aware documentation generation
            client = ClaudeClient(api_config_name=api)
            enhanced_prompt = f"{context_info}\n\nPlease generate comprehensive documentation for the main file, including API reference, usage examples, and integration notes."
            result = client.call(enhanced_prompt)
        else:
            with console.status("[bold blue]Generating documentation..."):
                result = generate_docs(file_path, api_config_name=api)
        
        if interactive:
            console.print("\n[bold]Initial Documentation:[/bold]\n")
            md = Markdown(result)
            console.print(md)
            
            client = ClaudeClient(api_config_name=api)
            conversation_context = [result]
            
            while True:
                console.print("\n[dim]Commands: 'save' to save and exit, 'exit' to discard, or ask for changes[/dim]")
                user_input = console.input("[cyan]You:[/cyan] ").strip()
                
                if user_input.lower() == 'exit':
                    console.print("[yellow]Discarded changes[/yellow]")
                    return
                
                if user_input.lower() == 'save':
                    result = conversation_context[-1]
                    break
                
                if not user_input:
                    continue
                
                refinement_prompt = f"Previous documentation:\n\n{conversation_context[-1]}\n\nUser request: {user_input}\n\nProvide the updated documentation."
                
                console.print("\n[bold green]Claude:[/bold green] ", end='')
                response_parts = []
                for chunk in client.call_streaming(refinement_prompt):
                    console.print(chunk, end='')
                    response_parts.append(chunk)
                console.print()
                
                result = ''.join(response_parts)
                conversation_context.append(result)
        
        if output:
            with open(output, 'w') as f:
                f.write(result)
            console.print(f"\n[green]✓[/green] Documentation saved to: {output}")
        elif not interactive:
            md = Markdown(result)
            console.print(md)
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.command('review')
@click.argument('file_path', type=click.Path(exists=True))
@click.option('-a', '--api', help='API config to use')
@click.option('-i', '--interactive', is_flag=True, help='Interactive follow-up questions')
@click.option('--auto-context', is_flag=True, help='Automatically include git, dependencies, and related files')
@click.pass_context
def review(
    ctx: click.Context,
    file_path: str,
    api: Optional[str],
    interactive: bool,
    auto_context: bool
) -> None:
    """Review code for bugs and improvements."""
    console = ctx.obj['console']
    
    try:
        # Gather context if requested
        context_info = ""
        if auto_context:
            from claude_dev_cli.context import ContextGatherer
            
            with console.status("[bold blue]Gathering context..."):
                gatherer = ContextGatherer()
                context = gatherer.gather_for_review(Path(file_path))
                context_info = context.format_for_prompt()
            
            console.print("[dim]✓ Context gathered (git, dependencies, tests)[/dim]")
        
        with console.status("[bold blue]Reviewing code..."):
            # If we have context, prepend it to the file analysis
            if context_info:
                # Read file separately for context-aware review
                result = code_review(file_path, api_config_name=api)
                # The context module already includes the file, so we use it differently
                client = ClaudeClient(api_config_name=api)
                enhanced_prompt = f"{context_info}\n\nPlease review this code for bugs and improvements."
                result = client.call(enhanced_prompt)
            else:
                result = code_review(file_path, api_config_name=api)
        
        md = Markdown(result)
        console.print(md)
        
        if interactive:
            client = ClaudeClient(api_config_name=api)
            with open(file_path, 'r') as f:
                file_content = f.read()
            
            console.print("\n[dim]Ask follow-up questions about the review, or 'exit' to quit[/dim]")
            
            while True:
                user_input = console.input("\n[cyan]You:[/cyan] ").strip()
                
                if user_input.lower() == 'exit':
                    break
                
                if not user_input:
                    continue
                
                follow_up_prompt = f"Code review:\n\n{result}\n\nOriginal code:\n\n{file_content}\n\nUser question: {user_input}"
                
                console.print("\n[bold green]Claude:[/bold green] ", end='')
                for chunk in client.call_streaming(follow_up_prompt):
                    console.print(chunk, end='')
                console.print()
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.command('debug')
@click.option('-f', '--file', type=click.Path(exists=True), help='File to debug')
@click.option('-e', '--error', help='Error message to analyze')
@click.option('-a', '--api', help='API config to use')
@click.option('--auto-context', is_flag=True, help='Automatically include git context and parse error details')
@click.pass_context
def debug(
    ctx: click.Context,
    file: Optional[str],
    error: Optional[str],
    api: Optional[str],
    auto_context: bool
) -> None:
    """Debug code and analyze errors."""
    console = ctx.obj['console']
    
    # Read from stdin if available
    stdin_content = None
    if not sys.stdin.isatty():
        stdin_content = sys.stdin.read().strip()
    
    error_text = error or stdin_content
    
    try:
        # Gather context if requested
        if auto_context and error_text:
            from claude_dev_cli.context import ContextGatherer
            
            with console.status("[bold blue]Gathering context..."):
                gatherer = ContextGatherer()
                file_path = Path(file) if file else None
                context = gatherer.gather_for_error(error_text, file_path=file_path)
                context_info = context.format_for_prompt()
            
            console.print("[dim]✓ Context gathered (error details, git context)[/dim]")
            
            # Use context-aware analysis
            client = ClaudeClient(api_config_name=api)
            enhanced_prompt = f"{context_info}\n\nPlease analyze this error and suggest fixes."
            result = client.call(enhanced_prompt)
        else:
            # Original behavior
            with console.status("[bold blue]Analyzing error..."):
                result = debug_code(
                    file_path=file,
                    error_message=error_text,
                    api_config_name=api
                )
        
        md = Markdown(result)
        console.print(md)
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.command('refactor')
@click.argument('file_path', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), help='Output file path')
@click.option('-a', '--api', help='API config to use')
@click.option('-i', '--interactive', is_flag=True, help='Interactive refinement mode')
@click.option('--auto-context', is_flag=True, help='Automatically include git, dependencies, and related files')
@click.pass_context
def refactor(
    ctx: click.Context,
    file_path: str,
    output: Optional[str],
    api: Optional[str],
    interactive: bool,
    auto_context: bool
) -> None:
    """Suggest refactoring improvements."""
    console = ctx.obj['console']
    
    try:
        # Gather context if requested
        if auto_context:
            from claude_dev_cli.context import ContextGatherer
            
            with console.status("[bold blue]Gathering context..."):
                gatherer = ContextGatherer()
                context = gatherer.gather_for_file(Path(file_path))
                context_info = context.format_for_prompt()
            
            console.print("[dim]✓ Context gathered[/dim]")
            
            # Use context-aware refactoring
            client = ClaudeClient(api_config_name=api)
            enhanced_prompt = f"{context_info}\n\nPlease suggest refactoring improvements for the main file."
            result = client.call(enhanced_prompt)
        else:
            with console.status("[bold blue]Analyzing code..."):
                result = refactor_code(file_path, api_config_name=api)
        
        if interactive:
            console.print("\n[bold]Initial Refactoring:[/bold]\n")
            md = Markdown(result)
            console.print(md)
            
            client = ClaudeClient(api_config_name=api)
            conversation_context = [result]
            
            while True:
                console.print("\n[dim]Commands: 'save' to save and exit, 'exit' to discard, or ask for changes[/dim]")
                user_input = console.input("[cyan]You:[/cyan] ").strip()
                
                if user_input.lower() == 'exit':
                    console.print("[yellow]Discarded changes[/yellow]")
                    return
                
                if user_input.lower() == 'save':
                    result = conversation_context[-1]
                    break
                
                if not user_input:
                    continue
                
                refinement_prompt = f"Previous refactoring:\n\n{conversation_context[-1]}\n\nUser request: {user_input}\n\nProvide the updated refactoring suggestions."
                
                console.print("\n[bold green]Claude:[/bold green] ", end='')
                response_parts = []
                for chunk in client.call_streaming(refinement_prompt):
                    console.print(chunk, end='')
                    response_parts.append(chunk)
                console.print()
                
                result = ''.join(response_parts)
                conversation_context.append(result)
        
        if output:
            with open(output, 'w') as f:
                f.write(result)
            console.print(f"\n[green]✓[/green] Refactored code saved to: {output}")
        elif not interactive:
            md = Markdown(result)
            console.print(md)
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.group()
def git() -> None:
    """Git workflow helpers."""
    pass


@git.command('commit')
@click.option('-a', '--api', help='API config to use')
@click.option('--auto-context', is_flag=True, help='Include git history and branch context')
@click.pass_context
def git_commit(ctx: click.Context, api: Optional[str], auto_context: bool) -> None:
    """Generate commit message from staged changes."""
    console = ctx.obj['console']
    
    try:
        if auto_context:
            from claude_dev_cli.context import ContextGatherer
            
            with console.status("[bold blue]Gathering context..."):
                gatherer = ContextGatherer()
                # Get git context with recent commits and branch info
                git_context = gatherer.git.gather(include_diff=True)
                context_info = git_context.format_for_prompt()
            
            console.print("[dim]✓ Context gathered (branch, commits, diff)[/dim]")
            
            # Use context-aware commit message generation
            client = ClaudeClient(api_config_name=api)
            enhanced_prompt = f"{context_info}\n\nPlease generate a concise, conventional commit message for the staged changes. Follow best practices: imperative mood, clear scope, explain what and why."
            result = client.call(enhanced_prompt)
        else:
            with console.status("[bold blue]Analyzing changes..."):
                result = git_commit_message(api_config_name=api)
        
        console.print("\n[bold green]Suggested commit message:[/bold green]")
        console.print(Panel(result, border_style="green"))
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.group()
def context() -> None:
    """Context gathering tools and information."""
    pass


@context.command('summary')
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--include-git/--no-git', default=True, help='Include git context')
@click.option('--include-deps/--no-deps', default=True, help='Include dependencies')
@click.option('--include-tests/--no-tests', default=True, help='Include test files')
@click.pass_context
def context_summary(
    ctx: click.Context,
    file_path: str,
    include_git: bool,
    include_deps: bool,
    include_tests: bool
) -> None:
    """Show what context would be gathered for a file."""
    from claude_dev_cli.context import ContextGatherer
    from rich.table import Table
    
    console = ctx.obj['console']
    
    try:
        file_path_obj = Path(file_path)
        gatherer = ContextGatherer()
        
        # Gather context
        with console.status("[bold blue]Analyzing context..."):
            context = gatherer.gather_for_review(
                file_path_obj,
                include_git=include_git,
                include_tests=include_tests
            )
        
        # Display summary
        console.print(f"\n[bold cyan]Context Summary for:[/bold cyan] {file_path}\n")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Type", style="cyan")
        table.add_column("Content", style="white")
        table.add_column("Size", justify="right", style="yellow")
        table.add_column("Lines", justify="right", style="green")
        table.add_column("Truncated", justify="center", style="red")
        
        total_chars = 0
        total_lines = 0
        
        for item in context.items:
            lines = len(item.content.split('\n'))
            chars = len(item.content)
            truncated = "✓" if item.metadata.get('truncated') else ""
            
            # Format content preview
            if item.type == 'file':
                content = item.metadata.get('path', 'unknown')
                if item.metadata.get('is_test'):
                    content += " [TEST]"
            elif item.type == 'git':
                branch = item.metadata.get('branch', 'unknown')
                modified = item.metadata.get('modified_count', 0)
                content = f"Branch: {branch}, {modified} modified files"
            elif item.type == 'dependency':
                dep_files = item.metadata.get('dependency_files', [])
                content = f"{len(dep_files)} dependency files"
            else:
                content = item.type
            
            table.add_row(
                item.type.title(),
                content[:60] + "..." if len(content) > 60 else content,
                f"{chars:,}",
                f"{lines:,}",
                truncated
            )
            
            total_chars += chars
            total_lines += lines
        
        console.print(table)
        
        # Show totals
        console.print(f"\n[bold]Total:[/bold]")
        console.print(f"  Characters: [yellow]{total_chars:,}[/yellow]")
        console.print(f"  Lines: [green]{total_lines:,}[/green]")
        console.print(f"  Estimated tokens: [cyan]~{total_chars // 4:,}[/cyan] (rough estimate)")
        
        # Show any truncation warnings
        truncated_items = [item for item in context.items if item.metadata.get('truncated')]
        if truncated_items:
            console.print(f"\n[yellow]⚠ {len(truncated_items)} item(s) truncated to fit size limits[/yellow]")
        
        console.print(f"\n[dim]Use --auto-context with commands to include this context[/dim]")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.command('usage')
@click.option('--days', type=int, help='Filter by days')
@click.option('--api', help='Filter by API config')
@click.pass_context
def usage(ctx: click.Context, days: Optional[int], api: Optional[str]) -> None:
    """Show API usage statistics."""
    console = ctx.obj['console']
    
    try:
        tracker = UsageTracker()
        tracker.display_usage(console, days=days, api_config=api)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.group()
def toon() -> None:
    """TOON format conversion tools."""
    pass


@toon.command('encode')
@click.argument('input_file', type=click.Path(exists=True), required=False)
@click.option('-o', '--output', type=click.Path(), help='Output file')
@click.pass_context
def toon_encode(ctx: click.Context, input_file: Optional[str], output: Optional[str]) -> None:
    """Convert JSON to TOON format."""
    console = ctx.obj['console']
    
    if not toon_utils.is_toon_available():
        console.print("[red]TOON support not installed.[/red]")
        console.print("Install with: [cyan]pip install claude-dev-cli[toon][/cyan]")
        sys.exit(1)
    
    try:
        import json
        
        # Read input
        if input_file:
            with open(input_file, 'r') as f:
                data = json.load(f)
        elif not sys.stdin.isatty():
            data = json.load(sys.stdin)
        else:
            console.print("[red]Error: No input provided[/red]")
            console.print("Usage: cdc toon encode [FILE] or pipe JSON via stdin")
            sys.exit(1)
        
        # Convert to TOON
        toon_str = toon_utils.to_toon(data)
        
        # Output
        if output:
            with open(output, 'w') as f:
                f.write(toon_str)
            console.print(f"[green]✓[/green] Converted to TOON: {output}")
        else:
            console.print(toon_str)
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@toon.command('decode')
@click.argument('input_file', type=click.Path(exists=True), required=False)
@click.option('-o', '--output', type=click.Path(), help='Output file')
@click.pass_context
def toon_decode(ctx: click.Context, input_file: Optional[str], output: Optional[str]) -> None:
    """Convert TOON format to JSON."""
    console = ctx.obj['console']
    
    if not toon_utils.is_toon_available():
        console.print("[red]TOON support not installed.[/red]")
        console.print("Install with: [cyan]pip install claude-dev-cli[toon][/cyan]")
        sys.exit(1)
    
    try:
        import json
        
        # Read input
        if input_file:
            with open(input_file, 'r') as f:
                toon_str = f.read()
        elif not sys.stdin.isatty():
            toon_str = sys.stdin.read()
        else:
            console.print("[red]Error: No input provided[/red]")
            console.print("Usage: cdc toon decode [FILE] or pipe TOON via stdin")
            sys.exit(1)
        
        # Convert from TOON
        data = toon_utils.from_toon(toon_str)
        
        # Output
        json_str = json.dumps(data, indent=2)
        if output:
            with open(output, 'w') as f:
                f.write(json_str)
            console.print(f"[green]✓[/green] Converted to JSON: {output}")
        else:
            console.print(json_str)
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@toon.command('info')
@click.pass_context
def toon_info(ctx: click.Context) -> None:
    """Show TOON format installation status and token savings info."""
    console = ctx.obj['console']
    
    if toon_utils.is_toon_available():
        console.print("[green]✓[/green] TOON format support is installed")
        console.print("\n[bold]About TOON:[/bold]")
        console.print("• Token-Oriented Object Notation")
        console.print("• 30-60% fewer tokens than JSON")
        console.print("• Optimized for LLM prompts")
        console.print("• Human-readable and lossless")
        console.print("\n[bold]Usage:[/bold]")
        console.print("  cdc toon encode data.json -o data.toon")
        console.print("  cdc toon decode data.toon -o data.json")
        console.print("  cat data.json | cdc toon encode")
    else:
        console.print("[yellow]TOON format support not installed[/yellow]")
        console.print("\nInstall with: [cyan]pip install claude-dev-cli[toon][/cyan]")
        console.print("\n[bold]Benefits:[/bold]")
        console.print("• Reduce API costs by 30-60%")
        console.print("• Faster LLM response times")
        console.print("• Same data, fewer tokens")


@main.group()
def template() -> None:
    """Manage custom prompt templates."""
    pass


@template.command('list')
@click.option('-c', '--category', help='Filter by category')
@click.option('--builtin', is_flag=True, help='Show only built-in templates')
@click.option('--user', is_flag=True, help='Show only user templates')
@click.pass_context
def template_list(
    ctx: click.Context,
    category: Optional[str],
    builtin: bool,
    user: bool
) -> None:
    """List available templates."""
    console = ctx.obj['console']
    config = Config()
    manager = TemplateManager(config.config_dir)
    
    templates = manager.list_templates(
        category=category,
        builtin_only=builtin,
        user_only=user
    )
    
    if not templates:
        console.print("[yellow]No templates found.[/yellow]")
        return
    
    from rich.table import Table
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan")
    table.add_column("Category", style="green")
    table.add_column("Variables", style="yellow")
    table.add_column("Type", style="blue")
    table.add_column("Description")
    
    for tmpl in templates:
        vars_display = ", ".join(tmpl.variables) if tmpl.variables else "-"
        type_display = "🔒 Built-in" if tmpl.builtin else "📝 User"
        table.add_row(
            tmpl.name,
            tmpl.category,
            vars_display,
            type_display,
            tmpl.description
        )
    
    console.print(table)
    
    # Show categories
    categories = manager.get_categories()
    console.print(f"\n[dim]Categories: {', '.join(categories)}[/dim]")


@template.command('show')
@click.argument('name')
@click.pass_context
def template_show(ctx: click.Context, name: str) -> None:
    """Show template details."""
    console = ctx.obj['console']
    config = Config()
    manager = TemplateManager(config.config_dir)
    
    tmpl = manager.get_template(name)
    if not tmpl:
        console.print(f"[red]Template not found: {name}[/red]")
        sys.exit(1)
    
    console.print(Panel(
        f"[bold]{tmpl.name}[/bold]\n\n"
        f"[dim]{tmpl.description}[/dim]\n\n"
        f"Category: [green]{tmpl.category}[/green]\n"
        f"Type: {'🔒 Built-in' if tmpl.builtin else '📝 User'}\n"
        f"Variables: [yellow]{', '.join(tmpl.variables) if tmpl.variables else 'None'}[/yellow]",
        title="Template Info",
        border_style="blue"
    ))
    
    console.print("\n[bold]Content:[/bold]\n")
    console.print(Panel(tmpl.content, border_style="dim"))


@template.command('add')
@click.argument('name')
@click.option('-c', '--content', help='Template content (or use stdin)')
@click.option('-d', '--description', help='Template description')
@click.option('--category', default='general', help='Template category')
@click.pass_context
def template_add(
    ctx: click.Context,
    name: str,
    content: Optional[str],
    description: Optional[str],
    category: str
) -> None:
    """Add a new template."""
    console = ctx.obj['console']
    config = Config()
    manager = TemplateManager(config.config_dir)
    
    # Get content from stdin if not provided
    if not content:
        if sys.stdin.isatty():
            console.print("[yellow]Enter template content (Ctrl+D to finish):[/yellow]")
        content = sys.stdin.read().strip()
    
    if not content:
        console.print("[red]Error: No content provided[/red]")
        sys.exit(1)
    
    try:
        tmpl = Template(
            name=name,
            content=content,
            description=description,
            category=category
        )
        manager.add_template(tmpl)
        
        console.print(f"[green]✓[/green] Template added: {name}")
        if tmpl.variables:
            console.print(f"[dim]Variables: {', '.join(tmpl.variables)}[/dim]")
    
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@template.command('delete')
@click.argument('name')
@click.pass_context
def template_delete(ctx: click.Context, name: str) -> None:
    """Delete a user template."""
    console = ctx.obj['console']
    config = Config()
    manager = TemplateManager(config.config_dir)
    
    try:
        if manager.delete_template(name):
            console.print(f"[green]✓[/green] Template deleted: {name}")
        else:
            console.print(f"[red]Template not found: {name}[/red]")
            sys.exit(1)
    
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@template.command('use')
@click.argument('name')
@click.option('-a', '--api', help='API config to use')
@click.option('-m', '--model', help='Claude model to use')
@click.pass_context
def template_use(ctx: click.Context, name: str, api: Optional[str], model: Optional[str]) -> None:
    """Use a template with interactive variable input."""
    console = ctx.obj['console']
    config = Config()
    manager = TemplateManager(config.config_dir)
    
    tmpl = manager.get_template(name)
    if not tmpl:
        console.print(f"[red]Template not found: {name}[/red]")
        sys.exit(1)
    
    # Get variable values
    variables = {}
    if tmpl.variables:
        console.print(f"\n[bold]Template: {name}[/bold]")
        console.print(f"[dim]{tmpl.description}[/dim]\n")
        
        for var in tmpl.variables:
            value = console.input(f"[cyan]{var}:[/cyan] ").strip()
            variables[var] = value
    
    # Check for missing variables
    missing = tmpl.get_missing_variables(**variables)
    if missing:
        console.print(f"[red]Missing required variables: {', '.join(missing)}[/red]")
        sys.exit(1)
    
    # Render template
    prompt = tmpl.render(**variables)
    
    # Call Claude
    try:
        client = ClaudeClient(api_config_name=api)
        
        console.print("\n[bold green]Claude:[/bold green] ", end='')
        for chunk in client.call_streaming(prompt, model=model):
            console.print(chunk, end='')
        console.print()
    
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


@main.group()
def warp() -> None:
    """Warp terminal integration."""
    pass


@warp.command('export-workflows')
@click.option('-o', '--output', type=click.Path(), help='Output directory')
@click.pass_context
def warp_export_workflows(ctx: click.Context, output: Optional[str]) -> None:
    """Export Warp workflows for claude-dev-cli commands."""
    console = ctx.obj['console']
    
    try:
        from claude_dev_cli.warp_integration import export_builtin_workflows
        
        config = Config()
        output_dir = Path(output) if output else config.config_dir / "warp" / "workflows"
        
        created_files = export_builtin_workflows(output_dir)
        
        console.print(f"[green]✓[/green] Exported {len(created_files)} Warp workflows to:")
        console.print(f"  {output_dir}")
        console.print("\n[bold]Workflows:[/bold]")
        for file in created_files:
            console.print(f"  • {file.name}")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@warp.command('export-launch-configs')
@click.option('-o', '--output', type=click.Path(), help='Output file path')
@click.pass_context
def warp_export_launch_configs(ctx: click.Context, output: Optional[str]) -> None:
    """Export Warp launch configurations."""
    console = ctx.obj['console']
    
    try:
        from claude_dev_cli.warp_integration import export_launch_configs
        
        config = Config()
        output_path = Path(output) if output else config.config_dir / "warp" / "launch_configs.json"
        
        export_launch_configs(output_path)
        
        console.print(f"[green]✓[/green] Exported Warp launch configurations to:")
        console.print(f"  {output_path}")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.group()
def workflow() -> None:
    """Manage and run workflows."""
    pass


@workflow.command('run')
@click.argument('workflow_file', type=click.Path(exists=True))
@click.option('--var', '-v', multiple=True, help='Set variables (key=value)')
@click.pass_context
def workflow_run(
    ctx: click.Context,
    workflow_file: str,
    var: tuple
) -> None:
    """Run a workflow from YAML file."""
    console = ctx.obj['console']
    
    # Parse variables
    variables = {}
    for v in var:
        if '=' in v:
            key, value = v.split('=', 1)
            variables[key] = value
    
    try:
        from claude_dev_cli.workflows import WorkflowEngine
        
        engine = WorkflowEngine(console=console)
        workflow_path = Path(workflow_file)
        
        context = engine.execute(workflow_path, initial_vars=variables)
        
        # Show summary
        if context.step_results:
            console.print("\n[bold]Results Summary:[/bold]")
            for step_name, result in context.step_results.items():
                status = "[green]✓[/green]" if result.success else "[red]✗[/red]"
                console.print(f"{status} {step_name}")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@workflow.command('list')
@click.pass_context
def workflow_list(ctx: click.Context) -> None:
    """List available workflows."""
    console = ctx.obj['console']
    config = Config()
    workflow_dir = config.config_dir / "workflows"
    
    from claude_dev_cli.workflows import list_workflows
    workflows = list_workflows(workflow_dir)
    
    if not workflows:
        console.print("[yellow]No workflows found.[/yellow]")
        console.print(f"\nCreate workflows in: {workflow_dir}")
        return
    
    from rich.table import Table
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan")
    table.add_column("Steps", style="yellow")
    table.add_column("Description")
    
    for wf in workflows:
        table.add_row(
            wf['name'],
            str(wf['steps']),
            wf['description']
        )
    
    console.print(table)
    console.print(f"\n[dim]Workflow directory: {workflow_dir}[/dim]")


@workflow.command('show')
@click.argument('workflow_file', type=click.Path(exists=True))
@click.pass_context
def workflow_show(ctx: click.Context, workflow_file: str) -> None:
    """Show workflow details."""
    console = ctx.obj['console']
    
    try:
        from claude_dev_cli.workflows import WorkflowEngine
        
        engine = WorkflowEngine(console=console)
        workflow = engine.load_workflow(Path(workflow_file))
        
        console.print(Panel(
            f"[bold]{workflow.get('name', 'Unnamed')}[/bold]\n\n"
            f"[dim]{workflow.get('description', 'No description')}[/dim]\n\n"
            f"Steps: [yellow]{len(workflow.get('steps', []))}[/yellow]",
            title="Workflow Info",
            border_style="blue"
        ))
        
        # Show steps
        steps = workflow.get('steps', [])
        if steps:
            console.print("\n[bold]Steps:[/bold]\n")
            for i, step in enumerate(steps, 1):
                step_name = step.get('name', f'step-{i}')
                step_type = 'command' if 'command' in step else 'shell' if 'shell' in step else 'set'
                console.print(f"  {i}. [cyan]{step_name}[/cyan] ({step_type})")
                
                if step.get('approval_required'):
                    console.print(f"     [yellow]⚠ Requires approval[/yellow]")
                if 'if' in step:
                    console.print(f"     [dim]Condition: {step['if']}[/dim]")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@workflow.command('validate')
@click.argument('workflow_file', type=click.Path(exists=True))
@click.pass_context
def workflow_validate(ctx: click.Context, workflow_file: str) -> None:
    """Validate workflow syntax."""
    console = ctx.obj['console']
    
    try:
        from claude_dev_cli.workflows import WorkflowEngine
        
        engine = WorkflowEngine(console=console)
        workflow = engine.load_workflow(Path(workflow_file))
        
        # Basic validation
        errors = []
        
        if 'name' not in workflow:
            errors.append("Missing 'name' field")
        
        if 'steps' not in workflow:
            errors.append("Missing 'steps' field")
        elif not isinstance(workflow['steps'], list):
            errors.append("'steps' must be a list")
        else:
            for i, step in enumerate(workflow['steps'], 1):
                if not any(k in step for k in ['command', 'shell', 'set']):
                    errors.append(f"Step {i}: Must have 'command', 'shell', or 'set'")
        
        if errors:
            console.print("[red]✗ Validation failed:[/red]\n")
            for error in errors:
                console.print(f"  • {error}")
            sys.exit(1)
        else:
            console.print(f"[green]✓[/green] Workflow is valid: {workflow.get('name')}")
            console.print(f"  Steps: {len(workflow.get('steps', []))}")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    main(obj={})
