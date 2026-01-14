"""CLI interface for the impostor game."""

import asyncio
import sys
import warnings
from pathlib import Path
from typing import Optional

import readchar
import typer
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

warnings.filterwarnings('ignore', category=UserWarning, module='pydantic')

src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from game import Game, GameState, PlayerRole

app = typer.Typer()
console = Console()


def display_your_role(game_state: GameState):
    """Display the human player's role and information."""
    human_player = game_state.get_human_player()
    if not human_player:
        return
    
    impostors = game_state.get_impostors()
    num_impostors = len(impostors)
    
    if human_player.role == PlayerRole.IMPOSTOR:
        role_text = Text()
        if num_impostors == 1:
            role_text.append("🎭 ERES EL IMPOSTOR\n", style="bold red")
        else:
            role_text.append(f"🎭 ERES UNO DE LOS {num_impostors} IMPOSTORES\n", style="bold red")
        role_text.append(f"Categoría: ", style="white")
        role_text.append(f"{game_state.category}\n", style="bold yellow")
        role_text.append("\n⚠️  Solo conoces la CATEGORÍA, NO la palabra clave.", style="dim")
        if num_impostors > 1:
            other_impostors = [p.name for p in impostors if p != human_player]
            role_text.append(f"\n\nOtros impostores: {', '.join(other_impostors)}", style="dim red")
        panel = Panel(role_text, title="INFO", border_style="red")
    else:
        role_text = Text()
        role_text.append("✅ ERES UN JUGADOR\n", style="bold green")
        role_text.append(f"Categoría: ", style="white")
        role_text.append(f"{game_state.category}\n", style="yellow")
        role_text.append(f"Palabra clave: ", style="white")
        role_text.append(f"{game_state.keyword}", style="bold green")
        if num_impostors > 1:
            role_text.append(f"\n\n⚠️  Hay {num_impostors} impostores entre los jugadores.", style="dim yellow")
        panel = Panel(role_text, title="INFO", border_style="green")
    
    console.print(panel)
    console.print()


def create_players_table(game_state: GameState, thinking_player: Optional[str] = None) -> Table:
    """Create a rich table showing players and their words."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    
    for i, player in enumerate(game_state.players, 1):
        table.add_column(justify="center", min_width=12)
    
    names_row = []
    words_row = []
    
    for i, player in enumerate(game_state.players, 1):
        status = "👤" if player.is_human else "🤖"
        names_row.append(f"{i}: {status} {player.name}")
        
        if thinking_player and player.name == thinking_player:
            words_row.append(Text("pensando...", style="italic yellow"))
        elif player.word_said:
            words_row.append(Text(player.word_said, style="bold cyan"))
        else:
            words_row.append("")
    
    table.add_row(*names_row)
    table.add_row(*words_row)
    
    return table


def create_game_display(game_state: GameState, thinking_player: Optional[str] = None) -> Panel:
    """Create the full game display panel."""
    table = create_players_table(game_state, thinking_player)
    return Panel(table, title="JUGADORES EN LA MESA", border_style="blue")


def create_voting_panel(game_state: GameState, selected_player_index: Optional[int] = None) -> Panel:
    """Create a voting panel with highlighted selected player."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    
    alive_players = game_state.get_alive_players()
    
    for player in alive_players:
        table.add_column(justify="center", min_width=12)
    
    names_row = []
    words_row = []
    
    for i, player in enumerate(alive_players):
        status = "👤" if player.is_human else "🤖"
        name_text = f"{i+1}: {status} {player.name}"
        
        if selected_player_index is not None and i == selected_player_index:
            names_row.append(Text(name_text, style="bold magenta reverse"))
        else:
            names_row.append(name_text)
        
        if player.word_said:
            word_text = Text(player.word_said, style="bold cyan")
            if selected_player_index is not None and i == selected_player_index:
                word_text.style = "bold magenta reverse"
            words_row.append(word_text)
        else:
            words_row.append("")
    
    table.add_row(*names_row)
    table.add_row(*words_row)
    
    return Panel(table, title="VOTACIÓN", border_style="magenta")


def interactive_vote_selector(game_state: GameState, allowed_players: Optional[list[str]] = None) -> Optional[str]:
    """Interactive vote selector using arrow keys."""
    alive_players = game_state.get_alive_players()
    human_player = game_state.get_human_player()
    
    if allowed_players:
        selectable_players = [p for p in alive_players if p.name in allowed_players and not p.is_human and p.is_alive]
    else:
        selectable_players = [p for p in alive_players if not p.is_human and p.is_alive]
    
    if not selectable_players:
        return None
    
    selectable_indices = [i for i, p in enumerate(alive_players) if p in selectable_players]
    current_idx = 0
    
    with Live(create_voting_panel(game_state, selectable_indices[current_idx]), console=console, refresh_per_second=10) as live:
        while True:
            live.update(create_voting_panel(game_state, selectable_indices[current_idx]))
            
            key = readchar.readkey()
            
            if key == readchar.key.LEFT:
                current_idx = (current_idx - 1) % len(selectable_indices)
            elif key == readchar.key.RIGHT:
                current_idx = (current_idx + 1) % len(selectable_indices)
            elif key == readchar.key.ENTER or key == '\r' or key == '\n':
                selected_player = selectable_players[current_idx]
                return selected_player.name


async def play_word_round_interactive(game: Game, game_state: GameState):
    """Play word round with human interaction."""
    alive_players = game_state.get_alive_players()
    human_player = game_state.get_human_player()
    
    ai_players_before = []
    ai_players_after = []
    human_position = None
    
    for i, player in enumerate(alive_players):
        if player.is_human:
            human_position = i
        elif human_position is None:
            ai_players_before.append(player)
        else:
            ai_players_after.append(player)
    
    if ai_players_before:
        with Live(create_game_display(game_state), console=console, refresh_per_second=4, transient=True) as live:
            for player in ai_players_before:
                live.update(create_game_display(game_state, thinking_player=player.name))
                
                words_said_so_far = game_state.format_words_for_ai(exclude_player=player)
                player_names = ", ".join([p.name for p in alive_players])
                
                role = player.role.value
                secret_info = game_state.category if player.role == PlayerRole.IMPOSTOR else game_state.keyword
                
                word = await game.npc_program.aforward(
                    role=role,
                    secret_info=secret_info,
                    words_said=words_said_so_far,
                    player_names=player_names,
                )
                
                player.word_said = word
                live.update(create_game_display(game_state))
    
    if human_player:
        console.print(create_game_display(game_state))
        console.print(f"\n📢 Es tu turno, {human_player.name}!")
        
        word = typer.prompt("\nDi tu palabra (una sola palabra)")
        human_player.word_said = word.strip()
        
        lines_to_clear = 8
        print(f"\033[{lines_to_clear}A\033[J", end="", flush=True)
    
    if ai_players_after:
        with Live(create_game_display(game_state), console=console, refresh_per_second=4) as live:
            for player in ai_players_after:
                live.update(create_game_display(game_state, thinking_player=player.name))
                
                words_said_so_far = game_state.format_words_for_ai(exclude_player=player)
                player_names = ", ".join([p.name for p in alive_players])
                
                role = player.role.value
                secret_info = game_state.category if player.role == PlayerRole.IMPOSTOR else game_state.keyword
                
                word = await game.npc_program.aforward(
                    role=role,
                    secret_info=secret_info,
                    words_said=words_said_so_far,
                    player_names=player_names,
                )
                
                player.word_said = word
                live.update(create_game_display(game_state))
    else:
        console.print(create_game_display(game_state))
    
    console.print()


async def voting_round_interactive(game: Game, game_state: GameState) -> tuple[str, dict[str, int]]:
    """Execute voting round with human interaction."""
    console.print()
    
    human_player = game_state.get_human_player()
    
    console.print("[dim]Usa las flechas ← → para seleccionar y ENTER para votar[/dim]")
    console.print()
    console.print("🤖 Los otros jugadores están votando...\n")
    
    async def get_human_vote():
        """Get human vote in a separate thread since readchar is blocking."""
        if human_player and human_player.is_alive:
            vote = await asyncio.to_thread(interactive_vote_selector, game_state)
            if not vote:
                console.print("[yellow]⚠️  Voto inválido. No votarás en esta ronda.[/yellow]")
            return vote
        return None
    
    human_vote_task = asyncio.create_task(get_human_vote())
    ai_votes_task = asyncio.create_task(game.collect_votes_parallel(game_state))
    
    human_vote, ai_votes = await asyncio.gather(human_vote_task, ai_votes_task)
    
    console.print()
    
    alive_players = game_state.get_alive_players()
    active_player_names = [p.name for p in alive_players]
    
    votes: dict[str, int] = {}
    
    if human_vote and human_vote in active_player_names:
        votes[human_vote] = votes.get(human_vote, 0) + 1
    
    for name, count in ai_votes.items():
        votes[name] = votes.get(name, 0) + count
    
    tied_players = game.get_tied_players(votes) if votes else []
    
    if len(tied_players) > 1:
        console.print(Panel("EMPATE DETECTADO", style="bold yellow"))
        console.print(f"Hay un empate entre: {', '.join(tied_players)}")
        console.print("Se realizará una revotación solo entre estos jugadores.\n")
        
        async def get_human_vote_tie():
            """Get human vote for tie resolution."""
            if human_player and human_player.is_alive:
                vote = await asyncio.to_thread(interactive_vote_selector, game_state, tied_players)
                if not vote:
                    console.print("[yellow]⚠️  Voto inválido. No votarás en esta revotación.[/yellow]")
                return vote
            return None
        
        console.print("[dim]Usa las flechas ← → para seleccionar y ENTER para votar[/dim]")
        console.print()
        console.print("🤖 Los otros jugadores están revotando...\n")
        
        human_vote_tie_task = asyncio.create_task(get_human_vote_tie())
        ai_votes_tie_task = asyncio.create_task(game.collect_tie_votes_parallel(game_state, tied_players))
        
        human_vote_tie, ai_votes_tie = await asyncio.gather(human_vote_tie_task, ai_votes_tie_task)
        
        console.print()
        
        alive_players = game_state.get_alive_players()
        active_player_names = [p.name for p in alive_players if p.name in tied_players]
        
        votes = {}
        
        if human_vote_tie and human_vote_tie in active_player_names:
            votes[human_vote_tie] = votes.get(human_vote_tie, 0) + 1
        
        for name, count in ai_votes_tie.items():
            votes[name] = votes.get(name, 0) + count
        
        tied_again = game.get_tied_players(votes)
        
        if len(tied_again) > 1:
            eliminated = tied_again[0]
        else:
            eliminated = max(votes.items(), key=lambda x: x[1])[0] if votes else tied_players[0]
    else:
        eliminated = max(votes.items(), key=lambda x: x[1])[0] if votes else None
    
    console.print(Panel("RESULTADOS DE LA VOTACIÓN", style="bold blue"))
    
    if votes:
        for name, count in sorted(votes.items(), key=lambda x: x[1], reverse=True):
            console.print(f"{name}: {count} voto(s)")
    else:
        console.print("No hubo votos válidos.")
    
    console.print()
    
    if eliminated:
        console.print(f"❌ [bold red]{eliminated}[/bold red] ha sido eliminado!")
    else:
        console.print("No se eliminó a nadie.")
    
    console.print()
    
    return eliminated, votes


def display_game_result(game_state: GameState, innocents_won: bool):
    """Display the final game result."""
    human_player = game_state.get_human_player()
    if not human_player:
        return
    
    human_is_impostor = human_player.role == PlayerRole.IMPOSTOR
    alive_impostors = game_state.get_alive_impostors()
    impostor_names = [p.name for p in alive_impostors]
    
    if innocents_won:
        if human_is_impostor:
            result_text = Text()
            result_text.append("❌ PERDISTE\n", style="bold red")
            result_text.append("Todos los impostores fueron descubiertos.", style="red")
            result_text.append(f"\nLa palabra clave era: {game_state.keyword}", style="green")
            console.print(Panel(result_text, title="🏆 RESULTADO FINAL 🏆", border_style="red"))
        else:
            result_text = Text()
            result_text.append("✅ ¡GANASTE!\n", style="bold green")
            result_text.append("Todos los impostores fueron descubiertos.", style="green")
            if impostor_names:
                result_text.append(f"\nLos impostores eran: {', '.join(impostor_names)}", style="yellow")
            console.print(Panel(result_text, title="🏆 RESULTADO FINAL 🏆", border_style="green"))
    else:
        if human_is_impostor:
            result_text = Text()
            result_text.append("✅ ¡GANASTE!\n", style="bold green")
            result_text.append("Los impostores han ganado.", style="green")
            result_text.append(f"\nLa palabra clave era: {game_state.keyword}", style="green")
            console.print(Panel(result_text, title="🏆 RESULTADO FINAL 🏆", border_style="green"))
        else:
            result_text = Text()
            result_text.append("❌ PERDISTE\n", style="bold red")
            result_text.append("Los impostores han ganado.", style="red")
            if impostor_names:
                result_text.append(f"\nLos impostores eran: {', '.join(impostor_names)}", style="red")
            result_text.append(f"\nLa palabra clave era: {game_state.keyword}", style="green")
            console.print(Panel(result_text, title="🏆 RESULTADO FINAL 🏆", border_style="red"))


@app.command()
def play(
    jugadores: int = typer.Option(5, "--jugadores", "-j", help="Número total de jugadores (mínimo 3)"),
    impostores: int = typer.Option(1, "--impostores", "-i", help="Número de impostores (debe ser menor que jugadores/2)")
):
    """Start a new game of Impostor."""
    console.print()
    console.print(Panel("🎮 ADIVINA EL IMPOSTOR 🎮", style="bold magenta", padding=(0, 2)))
    console.print()
    
    if jugadores < 3:
        console.print("[red]Error: Se necesitan al menos 3 jugadores[/red]")
        raise typer.Exit(1)
    
    max_impostors = jugadores // 2
    if impostores < 1:
        console.print("[red]Error: Debe haber al menos 1 impostor[/red]")
        raise typer.Exit(1)
    
    if impostores > max_impostors:
        console.print(f"[red]Error: El número de impostores ({impostores}) no puede ser igual o mayor a {max_impostors + 1} (jugadores/2)[/red]")
        raise typer.Exit(1)
    
    num_players = jugadores
    num_impostors = impostores
    
    console.print(f"[dim]Configuración: {num_players} jugadores, {num_impostors} impostor{'es' if num_impostors > 1 else ''}[/dim]")
    console.print()
    
    game = Game()
    
    async def run_game():
        game_state = await game.setup_game(num_players=num_players, num_impostors=num_impostors)
        
        display_your_role(game_state)
        
        while True:
            console.print(Panel(f"RONDA {game_state.round}", style="bold cyan"))
            console.print()
            
            await play_word_round_interactive(game, game_state)
            
            await asyncio.sleep(3)
            
            eliminated, votes = await voting_round_interactive(game, game_state)
            
            if not eliminated:
                console.print("[yellow]No se eliminó a nadie. Continuando...[/yellow]")
                console.print()
                continue
            
            is_over, innocents_won = game.check_game_over(game_state, eliminated)
            
            if is_over:
                display_game_result(game_state, innocents_won)
                console.print()
                break
            else:
                alive_players = game_state.get_alive_players()
                alive_innocents = game_state.get_alive_innocents()
                alive_impostors = game_state.get_alive_impostors()
                
                console.print(Panel("ESTADO DEL JUEGO", style="bold yellow"))
                console.print(f"Jugadores vivos: {len(alive_players)}")
                console.print(f"Inocentes vivos: {len(alive_innocents)}")
                console.print(f"Impostores vivos: {len(alive_impostors)}")
                console.print()
                console.print("[dim]Preparando siguiente ronda...[/dim]")
                console.print()
                
                game_state.clear_words_for_new_round()
                await asyncio.sleep(2)
    
    asyncio.run(run_game())


if __name__ == "__main__":
    app()
