"""
Command-line interface for the Dynamic Scoliosis Credentials System.

This module provides a user-friendly CLI for generating, validating, and managing
verifiable credentials.
"""

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track

from .generator import CredentialGenerator
from .qr_generator import QRGenerator
from .utils import (
    CredentialValidator,
    ConfigurationHelper,
    setup_logging,
    get_credential_summary,
)
from .models import (
    CredentialConfig,
    CredentialOutput,
    CredentialType,
    CredentialLevel,
    IssuerConfig,
    SubjectConfig,
    PractitionerCredential,
    PatientHealthRecord,
    EmergencyContact,
    MedicalAlert,
)

app = typer.Typer(
    name="ds-credentials",
    help="Dynamic Scoliosis Credentials System - Generate W3C Verifiable Credentials",
    add_completion=False,
)
console = Console()


@app.command()
def generate(
    config_file: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration file (JSON/YAML)",
    ),
    output_dir: Path = typer.Option(
        Path("output"),
        "--output",
        "-o",
        help="Output directory for generated files",
    ),
    credential_type: Optional[CredentialType] = typer.Option(
        None,
        "--type",
        "-t",
        help="Type of credential to generate",
    ),
    subject_name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="Name of the credential subject",
    ),
    issuer_did: Optional[str] = typer.Option(
        None,
        "--issuer",
        "-i",
        help="DID of the credential issuer",
    ),
    generate_qr: bool = typer.Option(
        True,
        "--qr/--no-qr",
        help="Generate QR code for the credential",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging",
    ),
):
    """Generate a new verifiable credential."""
    setup_logging("DEBUG" if verbose else "INFO")
    
    try:
        # Load configuration
        if config_file:
            if not config_file.exists():
                console.print(f"[red]Error: Configuration file not found: {config_file}[/red]")
                raise typer.Exit(1)
            config = ConfigurationHelper.load_config_from_file(config_file)
        else:
            # Interactive configuration
            config = _create_interactive_config(credential_type, subject_name, issuer_did)
        
        # Setup output configuration
        output_config = CredentialOutput(
            output_dir=str(output_dir),
            generate_qr=generate_qr,
        )
        
        # Generate credential
        with console.status("[bold green]Generating credential..."):
            generator = CredentialGenerator(config, output_config)
            credential, saved_path = generator.generate_and_save()
        
        console.print(f"[green]✓[/green] Generated credential: {saved_path}")
        
        # Generate QR code if requested
        if generate_qr:
            with console.status("[bold green]Generating QR code..."):
                qr_generator = QRGenerator(config.qr_config)
                qr_path = output_dir / "credential_qr.png"
                qr_payload, qr_image_path = qr_generator.generate_credential_qr(
                    credential, qr_path
                )
            
            console.print(f"[green]✓[/green] Generated QR code: {qr_image_path}")
            
            # Show QR size information
            size_info = qr_generator.estimate_qr_size(credential)
            console.print(f"[blue]Info:[/blue] QR payload size: {size_info['qr_payload_bytes']} bytes")
            console.print(f"[blue]Info:[/blue] Compression ratio: {size_info['compression_ratio']}")
        
        # Display credential summary
        summary = get_credential_summary(credential)
        _display_credential_summary(summary)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def validate(
    credential_file: Path = typer.Argument(..., help="Path to credential JSON file"),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed validation information",
    ),
):
    """Validate a verifiable credential."""
    setup_logging("DEBUG" if verbose else "WARNING")
    
    try:
        if not credential_file.exists():
            console.print(f"[red]Error: Credential file not found: {credential_file}[/red]")
            raise typer.Exit(1)
        
        # Load credential
        with open(credential_file, 'r', encoding='utf-8') as f:
            credential = json.load(f)
        
        # Validate credential
        result = CredentialValidator.validate_credential(credential)
        
        # Display results
        if result["is_valid"]:
            console.print(f"[green]✓ Credential is valid[/green]")
        else:
            console.print(f"[red]✗ Credential is invalid[/red]")
        
        if result["errors"]:
            console.print("\n[red]Errors:[/red]")
            for error in result["errors"]:
                console.print(f"  • {error}")
        
        if result["warnings"]:
            console.print("\n[yellow]Warnings:[/yellow]")
            for warning in result["warnings"]:
                console.print(f"  • {warning}")
        
        if verbose and result["info"]:
            console.print("\n[blue]Information:[/blue]")
            for key, value in result["info"].items():
                console.print(f"  • {key}: {value}")
        
        if not result["is_valid"]:
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def decode_qr(
    qr_payload: str = typer.Argument(..., help="QR code payload string"),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file for decoded credential",
    ),
):
    """Decode a verifiable credential from QR code payload."""
    try:
        qr_generator = QRGenerator()
        credential = qr_generator.decode_credential_from_qr(qr_payload)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(credential, f, indent=2, ensure_ascii=False)
            console.print(f"[green]✓[/green] Decoded credential saved to: {output_file}")
        else:
            console.print(json.dumps(credential, indent=2, ensure_ascii=False))
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def create_config(
    output_dir: Path = typer.Option(
        Path("config"),
        "--output",
        "-o",
        help="Output directory for configuration files",
    ),
    config_type: Optional[str] = typer.Option(
        None,
        "--type",
        "-t",
        help="Type of configuration to create (practitioner, patient, all)",
    ),
):
    """Create example configuration files."""
    try:
        if config_type and config_type not in ["practitioner", "patient", "all"]:
            console.print("[red]Error: config_type must be 'practitioner', 'patient', or 'all'[/red]")
            raise typer.Exit(1)
        
        configs = ConfigurationHelper.create_example_configs(output_dir)
        
        if config_type == "all" or config_type is None:
            for name, path in configs.items():
                console.print(f"[green]✓[/green] Created {name} configuration: {path}")
        else:
            path = configs.get(config_type)
            if path:
                console.print(f"[green]✓[/green] Created {config_type} configuration: {path}")
            else:
                console.print(f"[red]Error: Unknown configuration type: {config_type}[/red]")
                raise typer.Exit(1)
                
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def summary(
    credential_file: Path = typer.Argument(..., help="Path to credential JSON file"),
):
    """Display a summary of a verifiable credential."""
    try:
        if not credential_file.exists():
            console.print(f"[red]Error: Credential file not found: {credential_file}[/red]")
            raise typer.Exit(1)
        
        with open(credential_file, 'r', encoding='utf-8') as f:
            credential = json.load(f)
        
        summary = get_credential_summary(credential)
        _display_credential_summary(summary)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def _create_interactive_config(
    credential_type: Optional[CredentialType],
    subject_name: Optional[str],
    issuer_did: Optional[str],
) -> CredentialConfig:
    """Create configuration interactively."""
    console.print("[bold blue]Interactive Configuration[/bold blue]")
    
    # Get credential type
    if not credential_type:
        console.print("\nSelect credential type:")
        console.print("1. Practitioner")
        console.print("2. Patient Record")
        console.print("3. Emergency Contact")
        console.print("4. Medical Alert")
        
        choice = typer.prompt("Enter choice (1-4)", type=int)
        type_map = {
            1: CredentialType.PRACTITIONER,
            2: CredentialType.PATIENT_RECORD,
            3: CredentialType.EMERGENCY_CONTACT,
            4: CredentialType.MEDICAL_ALERT,
        }
        credential_type = type_map.get(choice)
        if not credential_type:
            console.print("[red]Invalid choice[/red]")
            raise typer.Exit(1)
    
    # Get issuer information
    if not issuer_did:
        issuer_did = typer.prompt("Enter issuer DID", default="did:web:kim-clinic.example")
    
    issuer_name = typer.prompt("Enter issuer name", default="Dr. Kim's Dynamic Scoliosis Clinic")
    verification_method = typer.prompt(
        "Enter verification method",
        default=f"{issuer_did}#key-1"
    )
    
    issuer = IssuerConfig(
        did=issuer_did,
        name=issuer_name,
        verification_method=verification_method,
    )
    
    # Get subject information
    if not subject_name:
        subject_name = typer.prompt("Enter subject name", default="Kim Johnson")
    
    subject = SubjectConfig(name=subject_name)
    
    # Create base config
    config = CredentialConfig(
        credential_type=credential_type,
        issuer=issuer,
        subject=subject,
    )
    
    # Add type-specific configuration
    if credential_type == CredentialType.PRACTITIONER:
        level_choice = typer.prompt(
            "Enter credential level (1=Level 1, 2=Level 2, 3=Level 3, 4=Certified, 5=Expert)",
            type=int,
            default=1
        )
        level_map = {
            1: CredentialLevel.LEVEL_1,
            2: CredentialLevel.LEVEL_2,
            3: CredentialLevel.LEVEL_3,
            4: CredentialLevel.CERTIFIED,
            5: CredentialLevel.EXPERT,
        }
        level = level_map.get(level_choice, CredentialLevel.LEVEL_1)
        
        config.practitioner = PractitionerCredential(level=level)
    
    elif credential_type in [CredentialType.PATIENT_RECORD, CredentialType.EMERGENCY_CONTACT, CredentialType.MEDICAL_ALERT]:
        patient_id = typer.prompt("Enter patient ID", default="P123456")
        config.patient_record = PatientHealthRecord(patient_id=patient_id)
    
    return config


def _display_credential_summary(summary: dict) -> None:
    """Display a formatted credential summary."""
    table = Table(title="Credential Summary")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    
    for key, value in summary.items():
        # Format the key nicely
        display_key = key.replace("_", " ").title()
        # Handle list values
        if isinstance(value, list):
            display_value = ", ".join(str(v) for v in value)
        else:
            display_value = str(value)
        
        table.add_row(display_key, display_value)
    
    console.print(table)


@app.command()
def version():
    """Show version information."""
    from . import __version__, __author__
    
    panel = Panel(
        f"[bold]Dynamic Scoliosis Credentials System[/bold]\n"
        f"Version: {__version__}\n"
        f"Author: {__author__}",
        title="Version Information",
        border_style="blue",
    )
    console.print(panel)


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main() 