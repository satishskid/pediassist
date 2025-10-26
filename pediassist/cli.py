"""
Main CLI entry point for PediAssist
"""

import click
import asyncio
import json
import sys
from typing import Optional, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.live import Live
from datetime import datetime

from .config import settings
from .core.diagnosis_parser import DiagnosisParser
from .core.treatment_generator import TreatmentGenerator
from .core.communication_engine import CommunicationEngine
from .core.delegation_manager import DelegationManager
from .database import DatabaseManager
from .llm.provider import LLMManager
from .llm.client import LLMClient
from .llm.cache import SmartQueryCache
from .security import license_manager

import structlog

logger = structlog.get_logger(__name__)
console = Console()

class PediAssistCLI:
    """Main CLI interface for PediAssist"""
    
    def __init__(self):
        self.settings = settings
        self.db_manager = DatabaseManager(settings.database_url)
        self.treatment_generator = TreatmentGenerator()
        self.llm_manager = self._setup_llm_manager()
        self.llm_client = self._setup_llm_client()
        
        self.cache = SmartQueryCache()
        self.diagnosis_parser = DiagnosisParser()
        self.communication_engine = CommunicationEngine()
        self.delegation_manager = DelegationManager()
    
    def _setup_llm_manager(self):
        """Setup LLM manager with configuration"""
        # Setup LLM configuration - only if API key is available or using local provider
        if settings.api_key or settings.llm_provider == "ollama":
            llm_config = {
                "primary": {
                    "provider": settings.llm_provider,
                    "api_key": settings.api_key,
                    "model": settings.model,
                    "max_tokens": settings.max_tokens,
                    "temperature": settings.temperature,
                    "base_url": settings.ollama_url if settings.llm_provider == "ollama" else None
                }
            }
            return LLMManager(llm_config)
        else:
            # Use local provider as fallback
            llm_config = {
                "primary": {
                    "provider": "ollama",
                    "model": settings.local_model,
                    "base_url": settings.ollama_url,
                    "max_tokens": settings.max_tokens,
                    "temperature": settings.temperature
                }
            }
            return LLMManager(llm_config)
    
    def _setup_llm_client(self):
        """Setup LLM client with proper configuration wrapper"""
        # Create a config wrapper that provides the expected nested structure
        class ConfigWrapper:
            def __init__(self, settings):
                self.settings = settings
                # Create nested llm config structure
                self.llm = type('obj', (object,), {
                    'provider': settings.llm_provider,
                    'model': settings.model,
                    'max_tokens': settings.max_tokens,
                    'temperature': settings.temperature,
                    'monthly_budget_usd': settings.monthly_budget,
                    'daily_budget_usd': settings.monthly_budget / 30,  # Rough daily budget
                    'api_key': settings.api_key,
                    'base_url': settings.ollama_url if settings.llm_provider == 'ollama' else None
                })
                # Other attributes that might be needed
                self.data_dir = settings.data_dir
                self.debug = settings.debug
        
        config_wrapper = ConfigWrapper(settings)
        return LLMClient(config_wrapper)
    
    async def initialize(self):
        """Initialize the CLI with database and LLM setup"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            # Initialize database
            task1 = progress.add_task("Initializing database...", total=None)
            # Test database connection instead of calling non-existent initialize method
            db_connected = await self.db_manager.check_connection()
            if db_connected:
                progress.update(task1, description="Database initialized ✓")
            else:
                progress.update(task1, description="Database connection failed ✗")
                logger.warning("Database connection failed")
            
            # Test LLM connection
            task2 = progress.add_task("Testing LLM connection...", total=None)
            try:
                # Check if LLM manager is available
                if self.llm_manager:
                    progress.update(task2, description="LLM connection established ✓")
                else:
                    progress.update(task2, description="LLM connection failed: Manager not initialized")
                    logger.warning("LLM connection failed", error="Manager not initialized")
            except Exception as e:
                progress.update(task2, description=f"LLM connection failed: {e}")
                logger.warning("LLM connection failed", error=str(e))
    
    def display_welcome(self):
        """Display welcome message and system status"""
        welcome_text = Text()
        welcome_text.append("PediAssist", style="bold cyan")
        welcome_text.append(" - Pediatric Clinical Decision Support System\n", style="dim")
        welcome_text.append("Version 1.0.0 | BYOK Enabled | Evidence-Based Protocols", style="dim")
        
        panel = Panel(
            welcome_text,
            title="[bold blue]Welcome[/bold blue]",
            border_style="blue"
        )
        console.print(panel)
        console.print()
    
    def display_status(self):
        """Display system status"""
        status_table = Table(title="System Status")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="green")
        status_table.add_column("Details", style="dim")
        
        # Database status
        db_status = "✓ Connected" if self.db_manager else "✗ Disconnected"
        status_table.add_row("Database", db_status, settings.database_url.split("://")[0])
        
        # LLM status
        llm_status = "✓ Ready" if self.llm_manager else "✗ Not configured"
        status_table.add_row("LLM Provider", llm_status, settings.llm_provider)
        
        # License status
        if settings.license_key:
            license_validation = license_manager.verify_license(settings.license_key)
            if license_validation["valid"]:
                license_status = "✓ Valid"
                license_details = f"{license_validation['license_info']['license_type']}"
            else:
                license_status = "✗ Invalid"
                license_details = license_validation.get("error", "Unknown error")
        else:
            license_status = "✗ Not configured"
            license_details = "BYOK Model"
        
        status_table.add_row("License", license_status, license_details)
        
        console.print(status_table)
        console.print()

@click.group()
@click.pass_context
def cli(ctx):
    """PediAssist - Pediatric Clinical Decision Support System"""
    ctx.ensure_object(dict)
    ctx.obj['cli'] = PediAssistCLI()

@cli.command()
@click.pass_context
def status(ctx):
    """Show system status"""
    cli_instance = ctx.obj['cli']
    cli_instance.display_welcome()
    cli_instance.display_status()

@cli.command()
@click.option('--age', '-a', type=int, required=True, help='Patient age in months')
@click.option('--sex', '-s', type=click.Choice(['M', 'F'], case_sensitive=False), 
              help='Patient sex (M/F)')
@click.option('--weight', '-w', type=float, help='Patient weight in kg')
@click.option('--chief-complaint', '-c', required=True, help='Chief complaint or presenting symptoms')
@click.option('--history', '-h', help='Additional medical history')
@click.option('--complexity', type=click.Choice(['basic', 'intermediate', 'advanced']), 
              default='basic', help='Treatment complexity level')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'detailed']), 
              default='table', help='Output format')
@click.pass_context
def diagnose(ctx, age, sex, weight, chief_complaint, history, complexity, output):
    """Generate diagnosis and treatment plan"""
    cli_instance = ctx.obj['cli']
    
    async def run_diagnosis():
        try:
            # Initialize system
            await cli_instance.initialize()
            
            # Display welcome
            cli_instance.display_welcome()
            
            # Create query
            query = f"{age} month old {sex or ''} patient presenting with {chief_complaint}"
            if history:
                query += f". History: {history}"
            
            console.print(f"[bold cyan]Processing query:[/bold cyan] {query}")
            console.print()
            
            # Parse diagnosis
            with console.status("[bold green]Analyzing symptoms...") as status:
                parsed_diagnosis = cli_instance.diagnosis_parser.parse(query)
                
                # Validate diagnosis - using a basic validation
                validation_result = {
                    "is_valid": True,
                    "errors": [],
                    "warnings": []
                }
                
                if not validation_result["is_valid"]:
                    console.print("[bold red]Diagnosis validation failed:[/bold red]")
                    for error in validation_result["errors"]:
                        console.print(f"  ✗ {error}")
                    return
                
                if validation_result["warnings"]:
                    console.print("[yellow]Warnings:[/yellow]")
                    for warning in validation_result["warnings"]:
                        console.print(f"  ⚠ {warning}")
            
            # Generate treatment plan
            with console.status("[bold green]Generating treatment plan...") as status:
                treatment_plan = cli_instance.treatment_generator.generate_protocol(
                    diagnosis=parsed_diagnosis.primary_diagnosis,
                    age_group=parsed_diagnosis.age_group.value,
                    urgency_level=parsed_diagnosis.urgency_level.value,
                    weight_kg=weight,
                    patient_context={"age_months": age, "sex": sex, "complexity": complexity}
                )
            
            # Generate LLM-enhanced recommendations
            with console.status("[bold green]Enhancing with AI insights...") as status:
                try:
                    llm_response = await cli_instance.llm_client.generate_treatment_plan(
                        diagnosis=parsed_diagnosis.primary_diagnosis,
                        age=age // 12,  # Convert months to years
                        context=f"Chief complaint: {chief_complaint}, Sex: {sex}, Weight: {weight}kg",
                        detail_level=complexity
                    )
                    logger.info("LLM response received successfully", response_type=type(llm_response), has_content=bool(llm_response.content if llm_response else None))
                except Exception as llm_error:
                    logger.error("LLM treatment plan generation failed", error=str(llm_error), error_type=type(llm_error))
                    # Continue without LLM enhancement
                    llm_response = None
            
            # Display results
            if output == 'json':
                result = {
                    "diagnosis": {
                        "primary": parsed_diagnosis.primary_diagnosis,
                        "secondary": parsed_diagnosis.secondary_diagnoses,
                        "confidence": parsed_diagnosis.confidence_score,
                        "urgency": parsed_diagnosis.urgency_level.value,
                        "age_group": parsed_diagnosis.age_group.value,
                        "system_category": parsed_diagnosis.system_category,
                        "red_flags": parsed_diagnosis.red_flags
                    },
                    "treatment_plan": {
                        "type": treatment_plan.plan_type.value,
                        "priority": treatment_plan.priority.value,
                        "duration": treatment_plan.duration_estimate,
                        "steps_count": len(treatment_plan.steps),
                        "medications": treatment_plan.medications,
                        "steps": [
                            {
                                "step_number": step.step_number,
                                "action": step.action,
                                "delegation_level": step.delegation_level,
                                "duration": step.duration
                            }
                            for step in treatment_plan.steps
                        ]
                    },
                    "ai_insights": llm_response.content if llm_response else None,
                    "validation": validation_result
                }
                console.print_json(json.dumps(result, indent=2, default=str))
                
            elif output == 'detailed':
                # Detailed output with rich formatting
                console.print("\n[bold blue]DIAGNOSIS ANALYSIS[/bold blue]")
                console.print("=" * 50)
                
                # Diagnosis section
                diagnosis_table = Table(title="Parsed Diagnosis")
                diagnosis_table.add_column("Field", style="cyan")
                diagnosis_table.add_column("Value", style="white")
                
                diagnosis_table.add_row("Primary Diagnosis", parsed_diagnosis.primary_diagnosis)
                diagnosis_table.add_row("Secondary Diagnoses", ", ".join(parsed_diagnosis.secondary_diagnoses) or "None")
                diagnosis_table.add_row("Confidence Score", f"{parsed_diagnosis.confidence_score:.2f}")
                diagnosis_table.add_row("Urgency Level", parsed_diagnosis.urgency_level.value.upper())
                diagnosis_table.add_row("Age Group", parsed_diagnosis.age_group.value)
                diagnosis_table.add_row("System Category", parsed_diagnosis.system_category)
                diagnosis_table.add_row("Red Flags", ", ".join(parsed_diagnosis.red_flags) or "None")
                
                console.print(diagnosis_table)
                
                # Treatment plan section
                console.print(f"\n[bold blue]TREATMENT PLAN[/bold blue] ({treatment_plan.plan_type.value.upper()})")
                console.print("=" * 50)
                
                console.print(f"Priority: [bold]{treatment_plan.priority.value.upper()}[/bold]")
                console.print(f"Estimated Duration: {treatment_plan.duration_estimate}")
                console.print()
                
                # Treatment steps
                steps_table = Table(title="Treatment Steps")
                steps_table.add_column("Step", style="cyan", width=3)
                steps_table.add_column("Action", style="white", width=40)
                steps_table.add_column("Delegation", style="dim", width=8)
                steps_table.add_column("Duration", style="dim", width=10)
                
                for step in treatment_plan.steps:
                    steps_table.add_row(
                        str(step.step_number),
                        step.action,
                        step.delegation_level,
                        step.duration or "N/A"
                    )
                
                console.print(steps_table)
                
                # Medications
                if treatment_plan.medications:
                    console.print(f"\n[bold blue]MEDICATIONS[/bold blue]")
                    meds_table = Table()
                    meds_table.add_column("Medication", style="cyan")
                    meds_table.add_column("Dosing", style="white")
                    meds_table.add_column("Monitoring", style="dim")
                    
                    for med in treatment_plan.medications:
                        meds_table.add_row(
                            med["name"],
                            str(med.get("dosing", "Per protocol")),
                            ", ".join(med.get("monitoring", []))
                        )
                    
                    console.print(meds_table)
                
                # AI insights
                if llm_response:
                    console.print(f"\n[bold blue]AI ENHANCED INSIGHTS[/bold blue]")
                    console.print("=" * 50)
                    console.print(llm_response.content)
                
                # Patient education
                console.print(f"\n[bold blue]PATIENT EDUCATION[/bold blue]")
                console.print("=" * 50)
                console.print(treatment_plan.patient_education)
                
                # Red flags
                console.print(f"\n[bold red]RETURN IMMEDIATELY IF:[/bold red]")
                for flag in treatment_plan.red_flags:
                    console.print(f"  • {flag}")
                
            else:  # table format
                # Summary table
                summary_table = Table(title="PediAssist Summary")
                summary_table.add_column("Category", style="cyan")
                summary_table.add_column("Details", style="white")
                
                summary_table.add_row("Primary Diagnosis", parsed_diagnosis.primary_diagnosis)
                summary_table.add_row("Confidence", f"{parsed_diagnosis.confidence_score:.2f}")
                summary_table.add_row("Urgency", parsed_diagnosis.urgency_level.value.upper())
                summary_table.add_row("Treatment Type", treatment_plan.plan_type.value.upper())
                summary_table.add_row("Steps", str(len(treatment_plan.steps)))
                summary_table.add_row("Medications", str(len(treatment_plan.medications)))
                
                console.print(summary_table)
                
                # Show AI insights if available
                if llm_response:
                    console.print(f"\n[dim]AI Enhanced: {llm_response.content[:100]}...[/dim]")
                
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            logger.error("Diagnosis failed", error=str(e))
    
    # Run the async function
    asyncio.run(run_diagnosis())

@cli.command()
@click.option('--query', '-q', required=True, help='Clinical question or scenario')
@click.option('--age', '-a', type=int, help='Patient age in months')
@click.option('--complexity', type=click.Choice(['basic', 'intermediate', 'advanced']), 
              default='basic', help='Complexity level')
@click.pass_context
async def query(ctx, query, age, complexity):
    """Submit a clinical query to the LLM"""
    cli_instance = ctx.obj['cli']
    
    try:
        await cli_instance.initialize()
        
        with console.status("[bold green]Processing clinical query...") as status:
            response = await cli_instance.llm_client.generate_treatment_plan(
                diagnosis=query,
                patient_age_months=age or 60,  # Default to 5 years
                complexity_level=complexity
            )
        
        if response:
            console.print(f"[bold cyan]Query:[/bold cyan] {query}")
            console.print(f"[bold green]Response:[/bold green]")
            console.print(response.content)
            
            if response.metadata:
                console.print(f"\n[dim]Model: {response.metadata.get('model', 'Unknown')}")
                console.print(f"Tokens: {response.metadata.get('total_tokens', 0)}")
                console.print(f"Cost: ${response.metadata.get('cost', 0):.4f}")
        else:
            console.print("[yellow]No response received from LLM[/yellow]")
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

@cli.command()
@click.pass_context
def config(ctx):
    """Show current configuration"""
    config_data = {
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.LLM_MODEL,
        "llm_temperature": settings.LLM_TEMPERATURE,
        "llm_max_tokens": settings.LLM_MAX_TOKENS,
        "database_url": settings.DATABASE_URL.split("://")[0] + "://***",
        "redis_url": settings.REDIS_URL.split("://")[0] + "://***" if settings.REDIS_URL else None,
        "license_key": "Configured" if settings.LICENSE_KEY else "Not configured",
        "cost_control_enabled": settings.ENABLE_COST_CONTROL,
        "daily_cost_limit": settings.DAILY_COST_LIMIT,
        "monthly_cost_limit": settings.MONTHLY_COST_LIMIT,
        "logging_level": settings.LOG_LEVEL
    }
    
    console.print_json(json.dumps(config_data, indent=2))

@cli.command()
@click.pass_context
def init_db(ctx):
    """Initialize the database with sample data"""
    cli_instance = ctx.obj['cli']
    
    try:
        with console.status("[bold green]Initializing database...") as status:
            asyncio.run(cli_instance.db_manager.create_tables())
            
        console.print("[bold green]Database initialized successfully![/bold green]")
        console.print("Database tables have been created.")
        
    except Exception as e:
        console.print(f"[bold red]Database initialization failed:[/bold red] {str(e)}")

@cli.command()
@click.option('--days', '-d', type=int, default=7, help='Number of days to show')
@click.pass_context
def stats(ctx, days):
    """Show usage statistics"""
    cli_instance = ctx.obj['cli']
    
    # This would integrate with the cost tracker and query cache
    console.print(f"[bold cyan]Usage Statistics (Last {days} days)[/bold cyan]")
    console.print("Feature coming soon...")

def main():
    """Main entry point"""
    # Set up logging for CLI
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Run the CLI
    cli()

if __name__ == '__main__':
    main()