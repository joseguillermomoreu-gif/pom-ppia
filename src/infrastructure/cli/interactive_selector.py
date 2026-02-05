"""Selector interactivo de tests."""

import sys
from pathlib import Path
from typing import List

from rich.console import Console
from rich.table import Table

console = Console()


class InteractiveSelector:
    """
    Selector interactivo de archivos de test.

    Presenta opciones al usuario y retorna la selección.
    """

    def select_tests(
        self, test_files: List[Path], mcp_excluded: List[Path] = None
    ) -> List[Path]:
        """
        Presenta selector interactivo y retorna tests seleccionados.

        Args:
            test_files: Lista de archivos de test disponibles
            mcp_excluded: Lista de tests excluidos por MCP (opcional)

        Returns:
            Lista de tests seleccionados por el usuario
        """
        if not test_files:
            console.print("[red]✗ No test files found[/red]")
            sys.exit(1)

        # Mostrar resumen
        console.print(f"\n[green]✓ Encontrados {len(test_files)} archivos de test[/green]")

        if mcp_excluded:
            console.print(
                f"[yellow]⚠ Excluidos {len(mcp_excluded)} tests con MCP sequences[/yellow]"
            )

        # Mostrar tabla de tests
        self._display_test_table(test_files)

        # Pedir selección
        return self._prompt_selection(test_files)

    def _display_test_table(self, test_files: List[Path]) -> None:
        """Muestra tabla con tests disponibles."""
        table = Table(title="📋 Tests Disponibles")

        table.add_column("#", justify="right", style="cyan", no_wrap=True)
        table.add_column("Archivo", style="magenta")
        table.add_column("Tamaño", justify="right", style="green")

        for idx, test_path in enumerate(test_files, 1):
            size_kb = test_path.stat().st_size / 1024
            table.add_row(str(idx), test_path.name, f"{size_kb:.1f} KB")

        console.print(table)

    def _prompt_selection(self, test_files: List[Path]) -> List[Path]:
        """
        Solicita al usuario que seleccione tests.

        Acepta:
        - 'a' o 'all' para todos los tests
        - 'q' o 'quit' para salir
        - Números directamente (ej: 1,3,5)

        Returns:
            Lista de tests seleccionados
        """
        console.print(
            "\n[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]"
        )
        console.print("[bold white]¿Qué tests deseas procesar?[/bold white]\n")
        console.print("  [bold green]a[/bold green]  → Procesar [bold]TODOS[/bold] los tests")
        console.print(
            "  [bold cyan]1,3,5[/bold cyan] → Procesar tests específicos "
            "(números separados por comas)"
        )
        console.print("  [bold red]q[/bold red]  → [bold]SALIR[/bold] del programa\n")
        console.print(
            "[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]"
        )

        while True:
            try:
                choice = console.input("\n[bold yellow]Selección:[/bold yellow] ").strip().lower()

                # Procesar todos los tests
                if choice in ("a", "all"):
                    console.print(
                        f"\n[green]✓ Seleccionados: {len(test_files)} tests[/green]"
                    )
                    return test_files

                # Salir
                elif choice in ("q", "quit"):
                    console.print("\n[yellow]👋 Cancelado por el usuario[/yellow]")
                    sys.exit(0)

                # Números directos o vacío
                elif choice:
                    # Intentar parsear como números
                    return self._parse_selection(choice, test_files)

                else:
                    console.print(
                        "[red]❌ Selección vacía. Escribe 'a' (todos), "
                        "números (1,3,5) o 'q' (salir)[/red]"
                    )

            except KeyboardInterrupt:
                console.print("\n[yellow]👋 Cancelado por el usuario[/yellow]")
                sys.exit(0)

    def _parse_selection(
        self, numbers: str, test_files: List[Path]
    ) -> List[Path]:
        """
        Parsea selección numérica del usuario.

        Args:
            numbers: String con números (ej: "1,3,5" o "1 3 5")
            test_files: Lista de tests disponibles

        Returns:
            Lista de tests seleccionados
        """
        try:
            # Soportar tanto comas como espacios
            numbers_clean = numbers.replace(",", " ")
            indices = [int(n.strip()) for n in numbers_clean.split() if n.strip()]

            if not indices:
                console.print("[red]❌ No se proporcionaron números válidos[/red]")
                return self._prompt_selection(test_files)

            selected = []
            invalid_numbers = []

            for idx in indices:
                if 1 <= idx <= len(test_files):
                    selected.append(test_files[idx - 1])
                else:
                    invalid_numbers.append(idx)

            # Mostrar warnings de números inválidos
            if invalid_numbers:
                console.print(
                    f"[yellow]⚠ Números fuera de rango (1-{len(test_files)}): "
                    f"{', '.join(map(str, invalid_numbers))}[/yellow]"
                )

            if not selected:
                console.print("[red]❌ No se seleccionaron tests válidos[/red]")
                return self._prompt_selection(test_files)

            console.print(f"\n[green]✓ Seleccionados: {len(selected)} tests[/green]")

            # Mostrar qué tests se seleccionaron
            for test_path in selected:
                console.print(f"  [dim]• {test_path.name}[/dim]")

            return selected

        except ValueError as e:
            console.print(
                f"[red]❌ Formato inválido: {str(e)}[/red]"
            )
            console.print("[yellow]Ejemplos válidos: 1,3,5 o 1 3 5[/yellow]")
            return self._prompt_selection(test_files)
