#!/usr/bin/env python3
"""
iCloud HideMyEmail Generator CLI

A luxury CLI experience for generating iCloud+ HideMyEmail addresses.
"""

import os
import sys
import json
import csv
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

import click
from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.text import Text
from rich.align import Align
from rich.padding import Padding
from rich.live import Live
from rich.layout import Layout
from rich import box

from icloud_hme import ICloudSession, HideMyEmailGenerator

console = Console()

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

CONFIG_DIR = Path.home() / ".icloud-hme"
VERSION = "1.0.0"

# Colors
ACCENT = "#00d4ff"
ACCENT2 = "#a855f7"
SUCCESS = "#22c55e"
ERROR = "#ef4444"
WARNING = "#f59e0b"
DIM = "#6b7280"

# ═══════════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def get_account_dir(email: str) -> Path:
    safe_email = email.replace("@", "_at_").replace(".", "_")
    return CONFIG_DIR / safe_email


def get_session_path(email: str) -> Path:
    return get_account_dir(email) / "session.json"


def get_emails_path(email: str) -> Path:
    return get_account_dir(email) / "emails.json"


def ensure_account_dir(email: str) -> Path:
    account_dir = get_account_dir(email)
    account_dir.mkdir(parents=True, exist_ok=True)
    return account_dir


def list_accounts() -> List[str]:
    if not CONFIG_DIR.exists():
        return []
    
    accounts = []
    for item in CONFIG_DIR.iterdir():
        if item.is_dir():
            session_file = item / "session.json"
            if session_file.exists():
                try:
                    with open(session_file) as f:
                        data = json.load(f)
                        email = data.get("account_info", {}).get("appleId") or \
                                data.get("account_info", {}).get("primaryEmail")
                        if email:
                            accounts.append(email)
                except:
                    pass
    return accounts


def load_generated_emails(email: str) -> List[Dict[str, Any]]:
    emails_path = get_emails_path(email)
    if emails_path.exists():
        try:
            with open(emails_path) as f:
                return json.load(f)
        except:
            pass
    return []


def save_generated_emails(email: str, emails: List[Dict[str, Any]]):
    ensure_account_dir(email)
    with open(get_emails_path(email), 'w') as f:
        json.dump(emails, f, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# UI Components
# ═══════════════════════════════════════════════════════════════════════════════

def banner():
    """Render the luxury banner."""
    logo = """
╭─────────────────────────────────────────────────────────────────────────────────╮
│                                                                                 │
│     ██╗ ██████╗██╗      ██████╗ ██╗   ██╗██████╗     ██╗  ██╗███╗   ███╗███████╗│
│     ██║██╔════╝██║     ██╔═══██╗██║   ██║██╔══██╗    ██║  ██║████╗ ████║██╔════╝│
│     ██║██║     ██║     ██║   ██║██║   ██║██║  ██║    ███████║██╔████╔██║█████╗  │
│     ██║██║     ██║     ██║   ██║██║   ██║██║  ██║    ██╔══██║██║╚██╔╝██║██╔══╝  │
│     ██║╚██████╗███████╗╚██████╔╝╚██████╔╝██████╔╝    ██║  ██║██║ ╚═╝ ██║███████╗│
│     ╚═╝ ╚═════╝╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝     ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝│
│                                                                                 │
╰─────────────────────────────────────────────────────────────────────────────────╯"""
    
    console.print(Text(logo, style=f"bold {ACCENT}"))
    console.print(Align.center(Text(f"HideMyEmail Generator • v{VERSION}", style=DIM)))
    console.print()


def mini_banner():
    """Compact banner for subcommands."""
    text = Text()
    text.append("◆ ", style=f"bold {ACCENT}")
    text.append("iCloud HME", style="bold white")
    text.append(" ─────────────────────────────────────────────────────────────────", style=DIM)
    console.print(text)
    console.print()


def msg_success(text: str):
    console.print(f"  [{SUCCESS}]✓[/{SUCCESS}] {text}")


def msg_error(text: str):
    console.print(f"  [{ERROR}]✗[/{ERROR}] {text}")


def msg_info(text: str):
    console.print(f"  [{ACCENT}]●[/{ACCENT}] {text}")


def msg_warn(text: str):
    console.print(f"  [{WARNING}]▲[/{WARNING}] {text}")


def divider():
    console.print(f"  [{DIM}]{'─' * 70}[/{DIM}]")


def select_account(accounts: List[str], prompt_text: str = "Select account") -> str:
    """Interactive account selector."""
    if len(accounts) == 1:
        return accounts[0]
    
    console.print(f"\n  [{ACCENT}]?[/{ACCENT}] {prompt_text}\n")
    
    for i, acc in enumerate(accounts, 1):
        console.print(f"    [{DIM}]{i}.[/{DIM}] [{ACCENT}]{acc}[/{ACCENT}]")
    
    console.print()
    choice = IntPrompt.ask(f"  [{DIM}]Enter number[/{DIM}]", choices=[str(i) for i in range(1, len(accounts) + 1)])
    return accounts[choice - 1]


# ═══════════════════════════════════════════════════════════════════════════════
# Commands
# ═══════════════════════════════════════════════════════════════════════════════

@click.group(invoke_without_command=True)
@click.version_option(version=VERSION, prog_name="icloud-hme")
@click.pass_context
def cli(ctx):
    """
    iCloud HideMyEmail Generator - Generate unlimited* email aliases
    """
    if ctx.invoked_subcommand is None:
        banner()
        
        # Show quick status
        accounts = list_accounts()
        if accounts:
            console.print(f"  [{SUCCESS}]●[/{SUCCESS}] {len(accounts)} authenticated account(s)")
            for acc in accounts[:3]:
                console.print(f"    [{DIM}]└─[/{DIM}] [{ACCENT}]{acc}[/{ACCENT}]")
            if len(accounts) > 3:
                console.print(f"    [{DIM}]└─ +{len(accounts) - 3} more...[/{DIM}]")
        else:
            console.print(f"  [{DIM}]○[/{DIM}] No authenticated accounts")
        
        console.print()
        divider()
        console.print()
        
        # Commands
        commands = [
            ("auth", "Authenticate with iCloud", "icloud-hme auth"),
            ("generate", "Generate email aliases", "icloud-hme generate"),
            ("list", "List all email aliases", "icloud-hme list"),
            ("export", "Export emails to file", "icloud-hme export"),
            ("accounts", "Manage accounts", "icloud-hme accounts"),
        ]
        
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column(style=f"bold {ACCENT}")
        table.add_column(style="white")
        table.add_column(style=DIM)
        
        for cmd, desc, usage in commands:
            table.add_row(cmd, desc, usage)
        
        console.print(Padding(table, (0, 2)))
        console.print()
        console.print(f"  [{DIM}]Run[/{DIM}] icloud-hme <command> --help [{DIM}]for more info[/{DIM}]")
        console.print()


@cli.command()
@click.option("--email", "-e", help="iCloud email address")
@click.option("--password", "-p", help="Password (will prompt securely if not provided)")
def auth(email: Optional[str], password: Optional[str]):
    """
    Authenticate with your iCloud account
    
    \b
    Supports two-factor authentication and stores session locally.
    """
    mini_banner()
    
    # Interactive email input
    if not email:
        email = Prompt.ask(f"  [{ACCENT}]?[/{ACCENT}] iCloud email")
    
    console.print()
    ensure_account_dir(email)
    session_path = get_session_path(email)
    
    # Check existing session
    session = ICloudSession(credentials_file=str(session_path), quiet=True)
    
    if session.load_session():
        msg_info("Found existing session, validating...")
        
        valid = False
        with console.status(f"  [{DIM}]Checking session...[/{DIM}]", spinner="dots"):
            valid = session.validate_session()
        
        if valid:
            console.print()
            msg_success(f"Already authenticated as [bold]{session.account_info.get('fullName', email)}[/bold]")
            
            console.print()
            if not Confirm.ask(f"  [{ACCENT}]?[/{ACCENT}] Re-authenticate?", default=False):
                return
    
    # Get password
    if not password:
        console.print()
        password = Prompt.ask(f"  [{ACCENT}]?[/{ACCENT}] Password", password=True)
    
    console.print()
    
    # Authenticate
    with console.status(f"  [{DIM}]Authenticating with Apple...[/{DIM}]", spinner="dots") as status:
        def get_2fa_code():
            status.stop()
            console.print()
            msg_info("Two-factor authentication required")
            console.print()
            code = Prompt.ask(f"  [{ACCENT}]?[/{ACCENT}] Enter 6-digit code")
            console.print()
            status.start()
            status.update(f"  [{DIM}]Verifying code...[/{DIM}]")
            return code
        
        success, message = session.login(email, password, code_callback=get_2fa_code)
    
    console.print()
    
    if success:
        msg_success(f"Authenticated as [bold]{session.account_info.get('fullName', email)}[/bold]")
        
        # Account details
        hme = session.account_info.get("isHideMyEmailFeatureAvailable", False)
        
        console.print()
        details = Table(show_header=False, box=None, padding=(0, 2))
        details.add_column(style=DIM)
        details.add_column()
        
        details.add_row("Email", f"[{ACCENT}]{session.account_info.get('primaryEmail', 'N/A')}[/{ACCENT}]")
        details.add_row("DSID", f"[{DIM}]{session.dsid or 'N/A'}[/{DIM}]")
        details.add_row("HideMyEmail", f"[{SUCCESS}]Available[/{SUCCESS}]" if hme else f"[{ERROR}]Not Available[/{ERROR}]")
        
        console.print(Padding(details, (0, 2)))
        
        if not hme:
            console.print()
            msg_warn("HideMyEmail requires iCloud+ subscription")
    else:
        msg_error(f"Authentication failed: {message}")
        sys.exit(1)


@cli.command()
@click.option("--count", "-n", type=int, help="Number of emails to generate")
@click.option("--account", "-a", help="Account to use")
@click.option("--label", "-l", default="icloud_hme", help="Label prefix")
@click.option("--output", "-o", type=click.Path(), help="Save to file")
@click.option("--format", "-f", "fmt", type=click.Choice(["json", "csv"]), default="json")
@click.option("--temp", is_flag=True, help="Generate temporary (non-reserved) emails")
@click.option("--delay", "-d", type=float, default=2.0, help="Delay between requests")
def generate(count: Optional[int], account: Optional[str], label: str, output: Optional[str],
             fmt: str, temp: bool, delay: float):
    """
    Generate new HideMyEmail addresses
    
    \b
    By default, emails are reserved (permanent). Use --temp for temporary emails.
    """
    mini_banner()
    
    # Get accounts
    accounts = list_accounts()
    
    if not accounts:
        msg_error("No authenticated accounts")
        console.print(f"\n  [{DIM}]Run[/{DIM}] icloud-hme auth [{DIM}]first[/{DIM}]")
        sys.exit(1)
    
    # Select account
    if account and account not in accounts:
        msg_error(f"Account not found: {account}")
        sys.exit(1)
    
    selected = account or (accounts[0] if len(accounts) == 1 else select_account(accounts))
    msg_info(f"Using [{ACCENT}]{selected}[/{ACCENT}]")
    
    # Load session
    session_path = get_session_path(selected)
    session = ICloudSession(credentials_file=str(session_path), quiet=True)
    
    if not session.load_session():
        msg_error("Failed to load session")
        sys.exit(1)
    
    with console.status(f"  [{DIM}]Validating session...[/{DIM}]", spinner="dots"):
        if not session.validate_session():
            msg_error("Session expired, please re-authenticate")
            sys.exit(1)
    
    if not session.account_info.get("isHideMyEmailFeatureAvailable"):
        msg_error("HideMyEmail not available (iCloud+ required)")
        sys.exit(1)
    
    # Get count interactively if not provided
    if count is None:
        console.print()
        count = IntPrompt.ask(f"  [{ACCENT}]?[/{ACCENT}] How many emails to generate", default=1)
    
    console.print()
    reserve = not temp
    
    # Config summary
    config_text = Text()
    config_text.append(f"  Generating ", style=DIM)
    config_text.append(str(count), style=f"bold {ACCENT}")
    config_text.append(" email(s) • ", style=DIM)
    config_text.append("PERMANENT" if reserve else "TEMPORARY", style=f"bold {SUCCESS}" if reserve else f"bold {WARNING}")
    console.print(config_text)
    console.print()
    divider()
    console.print()
    
    # Initialize generator
    emails_path = get_emails_path(selected)
    generator = HideMyEmailGenerator(session, output_file=str(emails_path), quiet=True)
    
    # Generate
    generated = []
    failed = 0
    rate_limited = False
    
    with Progress(
        TextColumn(f"  [{DIM}]" + "{task.description}" + f"[/{DIM}]"),
        SpinnerColumn(style=ACCENT),
        BarColumn(complete_style=ACCENT, finished_style=SUCCESS),
        TextColumn(f"[{DIM}]" + "{task.percentage:>3.0f}%" + f"[/{DIM}]"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("Generating...", total=count)
        
        for i in range(count):
            email = generator.generate_email()
            
            if email:
                data = {
                    "email": email,
                    "label": f"{label}_{i+1}_{datetime.now().strftime('%H%M%S')}",
                    "reserved": False,
                    "created_at": datetime.now().isoformat(),
                    "account": selected
                }
                
                if reserve:
                    progress.update(task, description=f"Reserving {email[:20]}...")
                    if generator.reserve_email(email, data["label"]):
                        data["reserved"] = True
                        generated.append(data)
                        generator.generated_emails.append(data)
                        generator._save_generated_emails()
                        console.print(f"  [{SUCCESS}]✓[/{SUCCESS}] [{ACCENT}]{email}[/{ACCENT}]")
                    else:
                        # Reservation failed - count as failure for permanent mode
                        failed += 1
                        rate_limited = True
                        console.print(f"  [{ERROR}]✗[/{ERROR}] [{DIM}]{email}[/{DIM}] [dim](rate limited)[/dim]")
                else:
                    # Temporary mode - no reservation needed
                    generated.append(data)
                    generator.generated_emails.append(data)
                    generator._save_generated_emails()
                    console.print(f"  [{WARNING}]○[/{WARNING}] [{ACCENT}]{email}[/{ACCENT}] [{DIM}](temporary)[/{DIM}]")
            else:
                failed += 1
                console.print(f"  [{ERROR}]✗[/{ERROR}] [{DIM}]Failed to generate (rate limited)[/{DIM}]")
                rate_limited = True
            
            progress.update(task, advance=1)
            
            if i < count - 1:
                time.sleep(delay)
    
    console.print()
    
    if not generated:
        msg_error("No emails generated - you've hit Apple's rate limit")
        console.print(f"\n  [{DIM}]Try again in ~30 minutes[/{DIM}]")
        sys.exit(1)
    
    # Summary
    divider()
    console.print()
    
    mode_label = "permanent" if reserve else "temporary"
    
    if failed > 0:
        console.print(f"  [{WARNING}]▲[/{WARNING}] Generated [bold]{len(generated)}/{count}[/bold] {mode_label} email(s)")
        console.print(f"    [{DIM}]{failed} failed due to rate limit - try again in ~30 min[/{DIM}]")
    else:
        console.print(f"  [{SUCCESS}]✓[/{SUCCESS}] Generated [bold]{len(generated)}/{count}[/bold] {mode_label} email(s)")
    
    # Save to file
    if output:
        output_path = Path(output)
        
        if fmt == "csv":
            with open(output_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["email", "label", "reserved", "created_at", "account"])
                writer.writeheader()
                writer.writerows(generated)
        else:
            with open(output_path, 'w') as f:
                json.dump(generated, f, indent=2)
        
        msg_success(f"Saved to [{ACCENT}]{output_path}[/{ACCENT}]")


@cli.command("list")
@click.option("--account", "-a", help="Account to use")
def list_emails(account: Optional[str]):
    """
    List all HideMyEmail addresses
    """
    mini_banner()
    
    accounts = list_accounts()
    
    if not accounts:
        msg_error("No authenticated accounts")
        sys.exit(1)
    
    selected = account or (accounts[0] if len(accounts) == 1 else select_account(accounts))
    
    # Load session
    session_path = get_session_path(selected)
    session = ICloudSession(credentials_file=str(session_path), quiet=True)
    
    if not session.load_session() or not session.validate_session():
        msg_error("Session invalid")
        sys.exit(1)
    
    generator = HideMyEmailGenerator(session, quiet=True)
    
    with console.status(f"  [{DIM}]Fetching from iCloud...[/{DIM}]", spinner="dots"):
        emails = generator.list_emails()
    
    if not emails:
        msg_info("No HideMyEmail addresses found")
        return
    
    active_count = sum(1 for e in emails if e.get("isActive"))
    
    console.print(f"  [{ACCENT}]{len(emails)}[/{ACCENT}] emails ([{SUCCESS}]{active_count} active[/{SUCCESS}])")
    console.print()
    divider()
    console.print()
    
    for i, email in enumerate(emails, 1):
        status = f"[{SUCCESS}]●[/{SUCCESS}]" if email.get("isActive") else f"[{ERROR}]○[/{ERROR}]"
        label = email.get("label", "")[:30] or f"[{DIM}]—[/{DIM}]"
        
        console.print(f"  {status} [{ACCENT}]{email.get('hme', '')}[/{ACCENT}]")
        console.print(f"      [{DIM}]{label}[/{DIM}]")
        
        if i < len(emails):
            console.print()


@cli.command()
@click.option("--account", "-a", help="Account to export (all if not specified)")
@click.option("--output", "-o", type=click.Path(), help="Output file path (without extension)")
@click.option("--format", "-f", "fmt", type=click.Choice(["json", "csv"]), default="csv")
@click.option("--filter", "status_filter", type=click.Choice(["all", "active", "inactive"]), default="all")
def export(account: Optional[str], output: Optional[str], fmt: str, status_filter: str):
    """
    Export emails to CSV or JSON
    """
    mini_banner()
    
    accounts = list_accounts()
    
    if not accounts:
        msg_error("No authenticated accounts")
        sys.exit(1)
    
    target = [account] if account else accounts
    all_emails = []
    
    for acc in target:
        session_path = get_session_path(acc)
        session = ICloudSession(credentials_file=str(session_path), quiet=True)
        
        if not session.load_session():
            continue
        
        msg_info(f"Fetching from [{ACCENT}]{acc}[/{ACCENT}]...")
        
        with console.status(f"  [{DIM}]Loading...[/{DIM}]", spinner="dots"):
            if session.validate_session():
                generator = HideMyEmailGenerator(session, quiet=True)
                emails = generator.list_emails()
                
                for e in emails:
                    all_emails.append({
                        "email": e.get("hme", ""),
                        "label": e.get("label", ""),
                        "active": e.get("isActive", True),
                        "account": acc,
                        "created": e.get("createTimestamp", "")
                    })
    
    # Filter
    if status_filter == "active":
        all_emails = [e for e in all_emails if e.get("active")]
    elif status_filter == "inactive":
        all_emails = [e for e in all_emails if not e.get("active")]
    
    if not all_emails:
        msg_warn("No emails to export")
        return
    
    console.print()
    msg_success(f"Found [{ACCENT}]{len(all_emails)}[/{ACCENT}] emails to export")
    console.print()
    
    # Interactive output path if not provided
    if not output:
        default_name = f"hidemyemails_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        output = Prompt.ask(
            f"  [{ACCENT}]?[/{ACCENT}] Save to (without extension)",
            default=default_name
        )
    
    # Export
    output_path = Path(f"{output}.{fmt}")
    
    if fmt == "csv":
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["email", "label", "active", "account", "created"])
            writer.writeheader()
            writer.writerows(all_emails)
    else:
        with open(output_path, 'w') as f:
            json.dump(all_emails, f, indent=2)
    
    console.print()
    msg_success(f"Exported to [{ACCENT}]{output_path}[/{ACCENT}]")


@cli.command()
def accounts():
    """
    List and manage authenticated accounts
    """
    mini_banner()
    
    accs = list_accounts()
    
    if not accs:
        msg_info("No authenticated accounts")
        console.print(f"\n  [{DIM}]Run[/{DIM}] icloud-hme auth [{DIM}]to add one[/{DIM}]")
        return
    
    console.print(f"  [{ACCENT}]{len(accs)}[/{ACCENT}] authenticated account(s)")
    console.print()
    divider()
    console.print()
    
    for acc in accs:
        session_path = get_session_path(acc)
        session = ICloudSession(credentials_file=str(session_path), quiet=True)
        
        if session.load_session():
            hme = session.account_info.get("isHideMyEmailFeatureAvailable", False)
            status = f"[{SUCCESS}]●[/{SUCCESS}]" if hme else f"[{ERROR}]○[/{ERROR}]"
            local = len(load_generated_emails(acc))
            
            console.print(f"  {status} [{ACCENT}]{acc}[/{ACCENT}]")
            console.print(f"      [{DIM}]HME: {'Yes' if hme else 'No'} • Generated: {local}[/{DIM}]")
            console.print()


@cli.command()
@click.option("--email", "-e", help="Account email to remove")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def logout(email: Optional[str], yes: bool):
    """
    Remove an authenticated account
    """
    mini_banner()
    
    accounts = list_accounts()
    
    if not accounts:
        msg_error("No accounts to remove")
        sys.exit(1)
    
    selected = email or (accounts[0] if len(accounts) == 1 else select_account(accounts, "Select account to remove"))
    
    if not yes:
        console.print()
        if not Confirm.ask(f"  [{WARNING}]?[/{WARNING}] Remove [{ACCENT}]{selected}[/{ACCENT}]?", default=False):
            msg_info("Cancelled")
            return
    
    account_dir = get_account_dir(selected)
    
    if account_dir.exists():
        import shutil
        shutil.rmtree(account_dir)
        console.print()
        msg_success(f"Removed [{ACCENT}]{selected}[/{ACCENT}]")
    else:
        msg_error("Account not found")


def main():
    cli()


if __name__ == "__main__":
    main()
