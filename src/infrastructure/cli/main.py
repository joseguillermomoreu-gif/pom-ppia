"""Entry point de la CLI."""

import sys
from pathlib import Path

import click
from rich.console import Console

from src.application.use_cases.process_tests.process_tests_command import (
    ProcessTestsCommand,
)
from src.infrastructure.cli.interactive_selector import InteractiveSelector
from src.infrastructure.cli.output_formatter import OutputFormatter
from src.infrastructure.config.dependency_injection import DIContainer
from src.infrastructure.config.settings import settings
from src.infrastructure.exceptions import MCPTestDetectedError

console = Console()


@click.command()
@click.option(
    "--input",
    "-i",
    "input_dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Directorio con archivos de test TypeScript",
)
@click.option(
    "--pom",
    "pom_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Path a POM.md existente (opcional)",
)
@click.option(
    "--output",
    "-o",
    "output_dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directorio de salida (default: ./output)",
)
@click.option(
    "--model",
    "-m",
    "model",
    type=str,
    default=None,
    help="Modelo LLM a usar (default: gpt-4o-mini)",
)
@click.option(
    "--non-interactive",
    is_flag=True,
    help="Modo no interactivo (procesa todos los tests)",
)
def main(
    input_dir: Path,
    pom_path: Path | None,
    output_dir: Path | None,
    model: str | None,
    non_interactive: bool,
) -> None:
    """
    🤖 POM-PPIA Generator

    Genera documentación POM y tests desde tests Playwright declarativos.

    Ejemplos:

    \b
        # Modo interactivo
        python -m src.infrastructure.cli.main --input /path/to/tests

    \b
        # Con POM existente
        python -m src.infrastructure.cli.main --input /path/to/tests --pom pom.md

    \b
        # Modo no interactivo (todos los tests)
        python -m src.infrastructure.cli.main --input /path/to/tests --non-interactive
    """
    try:
        # Configurar output dir si se proporciona
        if output_dir:
            settings.output_dir = output_dir

        # Configurar modelo si se proporciona
        if model:
            settings.default_model = model

        # Mostrar header
        OutputFormatter.print_header(input_dir, pom_path)

        # Escanear directorio
        OutputFormatter.print_scanning(input_dir)
        test_repository = DIContainer.get_test_repository()
        all_test_files = test_repository.list_test_files(input_dir)

        if not all_test_files:
            console.print("[red]✗ No se encontraron archivos .spec.ts[/red]")
            sys.exit(1)

        # Filtrar tests MCP
        valid_tests, mcp_tests = _filter_mcp_tests(
            all_test_files, test_repository
        )

        if not valid_tests:
            console.print(
                "[red]✗ Todos los tests usan MCP sequences (no se pueden procesar)[/red]"
            )
            sys.exit(1)

        # Seleccionar tests (interactivo o todos)
        if non_interactive:
            selected_tests = valid_tests
            console.print(
                f"\n[green]✓ Procesando {len(selected_tests)} tests (modo no interactivo)[/green]"
            )
        else:
            selector = InteractiveSelector()
            selected_tests = selector.select_tests(valid_tests, mcp_tests)

        # Crear comando
        command = ProcessTestsCommand(
            input_dir=input_dir,
            test_files=selected_tests,
            pom_md_path=pom_path,
            output_dir=output_dir,
        )

        # Ejecutar procesamiento con progress bar
        result = _process_with_progress(command)

        # Mostrar resultado
        OutputFormatter.print_result(result)

        # Exit code según resultado
        sys.exit(0 if result.success else 1)

    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Cancelado por el usuario[/yellow]")
        sys.exit(130)

    except Exception as e:
        console.print(f"\n[red]❌ Error inesperado: {str(e)}[/red]")
        if "--debug" in sys.argv:
            console.print_exception()
        sys.exit(1)


def _filter_mcp_tests(all_tests, test_repository):
    """
    Filtra tests con MCP sequences.

    Returns:
        Tupla (valid_tests, mcp_tests)
    """
    valid_tests = []
    mcp_tests = []

    for test_path in all_tests:
        try:
            # Intentar leer el test
            test_file = test_repository.read_test(test_path)
            valid_tests.append(test_path)

        except MCPTestDetectedError:
            # Test con MCP detectado
            mcp_tests.append(test_path)

        except Exception as e:
            # Otro error - mostrar warning
            console.print(
                f"[yellow]⚠ Error leyendo {test_path.name}: {str(e)}[/yellow]"
            )

    return valid_tests, mcp_tests


def _process_with_progress(command):
    """Ejecuta procesamiento con barra de progreso."""
    progress = OutputFormatter.create_progress()

    with progress:
        task = progress.add_task("[cyan]Procesando con OpenAI...", total=4)

        handler = DIContainer.get_process_tests_handler()

        # Nota: En una implementación más avanzada, cada handler
        # podría reportar progreso individual
        progress.update(task, advance=0, description="[cyan]Analizando tests...")

        result = handler.execute(command)

        progress.update(task, advance=4, description="[green]✓ Completado")

    return result


if __name__ == "__main__":
    main()
