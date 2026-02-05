"""Formateador de salida para CLI."""

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table

from src.application.dto.generation_result import GenerationResult

console = Console()


class OutputFormatter:
    """
    Formateador de salida con Rich.

    Proporciona métodos para mostrar resultados con estilo.
    """

    @staticmethod
    def print_header(input_dir: Path, pom_path: Path | None = None) -> None:
        """Muestra header inicial con banner ASCII art."""
        banner = """
[bold cyan]
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║   ██████╗  ██████╗ ███╗   ███╗     ██████╗ ██████╗ ██╗ █████╗       ║
║   ██╔══██╗██╔═══██╗████╗ ████║     ██╔══██╗██╔══██╗██║██╔══██╗      ║
║   ██████╔╝██║   ██║██╔████╔██║     ██████╔╝██████╔╝██║███████║      ║
║   ██╔═══╝ ██║   ██║██║╚██╔╝██║     ██╔═══╝ ██╔═══╝ ██║██╔══██║      ║
║   ██║     ╚██████╔╝██║ ╚═╝ ██║     ██║     ██║     ██║██║  ██║      ║
║   ╚═╝      ╚═════╝ ╚═╝     ╚═╝     ╚═╝     ╚═╝     ╚═╝╚═╝  ╚═╝      ║
║                                                                       ║
║              [bold white]Generador de POM y Tests desde Playwright[/bold white]             ║
║                                                                       ║
║   [dim]Transforma tests declarativos TypeScript en documentación POM[/dim]     ║
║   [dim]estructurada y tests refactorizados con Page Object Model[/dim]        ║
║                                                                       ║
║   [yellow]Autor:[/yellow] [white]jgmoreu[/white]  |  [yellow]Powered by:[/yellow] [white]OpenAI GPT-4[/white]                    ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
[/bold cyan]
        """
        console.print(banner)
        console.print(f"[bold]📂 Directorio:[/bold] [cyan]{input_dir}[/cyan]")

        if pom_path:
            console.print(
                f"[bold green]📖 POM existente detectado:[/bold green] [cyan]{pom_path.name}[/cyan]"
            )

    @staticmethod
    def create_progress() -> Progress:
        """Crea barra de progreso."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        )

    @staticmethod
    def print_result(result: GenerationResult) -> None:
        """
        Muestra resultado de la generación.

        Args:
            result: Resultado de la generación
        """
        if result.success:
            OutputFormatter._print_success(result)
        else:
            OutputFormatter._print_error(result)

    @staticmethod
    def _print_success(result: GenerationResult) -> None:
        """Muestra resultado exitoso."""
        console.print("\n[bold green]✅ Generación completada[/bold green]")

        # Tabla de archivos generados
        if result.generated_files:
            table = Table(title="📁 Archivos Generados")
            table.add_column("Tipo", style="cyan")
            table.add_column("Archivo", style="magenta")
            table.add_column("Path", style="dim")

            file_types = {
                "pom": "POM Structure",
                "pom_components": "POM Components",
                "cucumber": "Cucumber Tests",
                "playwright": "Playwright Tests",
            }

            for file_type, path in result.generated_files.items():
                table.add_row(
                    file_types.get(file_type, file_type),
                    path.name,
                    str(path.parent),
                )

            console.print(table)

        # Metadata
        metadata = result.metadata
        output_dir = metadata.get("output_dir", "N/A")
        duration = metadata.get("duration_seconds", 0)
        test_count = metadata.get("test_count", 0)
        mcp_excluded = metadata.get("mcp_tests_excluded", 0)

        info_panel = f"""
[bold]Directorio de salida:[/bold] {output_dir}
[bold]Tests procesados:[/bold] {test_count}
[bold]Tests MCP excluidos:[/bold] {mcp_excluded}
[bold]Tiempo total:[/bold] {duration}s
        """

        console.print(Panel(info_panel.strip(), title="ℹ️ Información"))

        # Warnings
        if result.warnings:
            console.print(
                f"\n[yellow]⚠ {len(result.warnings)} warnings:[/yellow]"
            )
            for warning in result.warnings[:5]:  # Mostrar máximo 5
                console.print(f"  [dim]• {warning}[/dim]")

            if len(result.warnings) > 5:
                console.print(
                    f"  [dim]... y {len(result.warnings) - 5} más[/dim]"
                )

    @staticmethod
    def _print_error(result: GenerationResult) -> None:
        """Muestra resultado con errores."""
        console.print("\n[bold red]❌ Generación falló[/bold red]")

        if result.errors:
            console.print(f"\n[red]Errores encontrados ({len(result.errors)}):[/red]")
            for error in result.errors:
                console.print(f"  [red]• {error}[/red]")

        if result.warnings:
            console.print(f"\n[yellow]Warnings ({len(result.warnings)}):[/yellow]")
            for warning in result.warnings[:5]:
                console.print(f"  [dim]• {warning}[/dim]")

    @staticmethod
    def print_scanning(directory: Path) -> None:
        """Muestra mensaje de escaneo."""
        console.print(f"\n[cyan]🔍 Escaneando directorio: {directory}[/cyan]")
