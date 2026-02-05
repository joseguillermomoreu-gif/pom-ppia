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

        Returns:
            Lista de tests seleccionados
        """
        console.print("\n[bold]¿Qué deseas procesar?[/bold]")
        console.print("  [cyan][a][/cyan] Todos los tests")
        console.print("  [cyan][n][/cyan] Número específico (ej: 1,3,5)")
        console.print("  [cyan][q][/cyan] Salir")

        while True:
            try:
                choice = console.input("\n[bold yellow]Selección:[/bold yellow] ").strip().lower()

                if choice == "a":
                    console.print(
                        f"\n[green]✓ Seleccionados: {len(test_files)} tests[/green]"
                    )
                    return test_files

                elif choice == "q":
                    console.print("[yellow]👋 Cancelado por el usuario[/yellow]")
                    sys.exit(0)

                elif choice == "n":
                    numbers = console.input(
                        "[bold yellow]Números (ej: 1,3,5):[/bold yellow] "
                    ).strip()
                    return self._parse_selection(numbers, test_files)

                else:
                    console.print("[red]❌ Opción inválida. Usa 'a', 'n' o 'q'[/red]")

            except KeyboardInterrupt:
                console.print("\n[yellow]👋 Cancelado por el usuario[/yellow]")
                sys.exit(0)

    def _parse_selection(
        self, numbers: str, test_files: List[Path]
    ) -> List[Path]:
        """
        Parsea selección numérica del usuario.

        Args:
            numbers: String con números (ej: "1,3,5")
            test_files: Lista de tests disponibles

        Returns:
            Lista de tests seleccionados
        """
        try:
            indices = [int(n.strip()) for n in numbers.split(",")]

            selected = []
            for idx in indices:
                if 1 <= idx <= len(test_files):
                    selected.append(test_files[idx - 1])
                else:
                    console.print(
                        f"[yellow]⚠ Número {idx} fuera de rango (ignorado)[/yellow]"
                    )

            if not selected:
                console.print("[red]❌ No se seleccionaron tests válidos[/red]")
                return self._prompt_selection(test_files)

            console.print(f"\n[green]✓ Seleccionados: {len(selected)} tests[/green]")
            return selected

        except ValueError:
            console.print(
                "[red]❌ Formato inválido. Usa números separados por comas (ej: 1,3,5)[/red]"
            )
            return self._prompt_selection(test_files)
