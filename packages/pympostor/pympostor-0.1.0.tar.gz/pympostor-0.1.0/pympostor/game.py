"""Game logic for the impostor game."""

import random
from enum import Enum
from typing import List, Optional, Tuple

from pydantic import BaseModel

from programs import NPC, Vote
from words import get_random_category_and_word


class PlayerRole(str, Enum):
    JUGADOR = "jugador"
    IMPOSTOR = "impostor"


class Player(BaseModel):
    """Represents a player in the game."""
    name: str
    is_human: bool
    role: PlayerRole
    is_alive: bool = True
    word_said: Optional[str] = None
    position: int = 0


class GameState(BaseModel):
    """Represents the current state of the game."""
    players: List[Player]
    keyword: str
    category: str
    round: int = 1
    
    def get_alive_players(self) -> List[Player]:
        """Get all alive players."""
        return [p for p in self.players if p.is_alive]
    
    def get_human_player(self) -> Optional[Player]:
        """Get the human player."""
        for player in self.players:
            if player.is_human:
                return player
        return None
    
    def get_impostor(self) -> Optional[Player]:
        """Get the impostor player (deprecated, use get_impostors())."""
        impostors = self.get_impostors()
        return impostors[0] if impostors else None
    
    def get_impostors(self) -> List[Player]:
        """Get all impostor players."""
        return [p for p in self.players if p.role == PlayerRole.IMPOSTOR]
    
    def get_alive_impostors(self) -> List[Player]:
        """Get all alive impostor players."""
        return [p for p in self.players if p.is_alive and p.role == PlayerRole.IMPOSTOR]
    
    def get_alive_innocents(self) -> List[Player]:
        """Get all alive innocent players."""
        return [p for p in self.players if p.is_alive and p.role == PlayerRole.JUGADOR]
    
    def check_impostor_win_condition(self) -> bool:
        """Check if impostors have won (innocents <= impostors)."""
        alive_innocents = self.get_alive_innocents()
        alive_impostors = self.get_alive_impostors()
        return len(alive_innocents) <= len(alive_impostors)
    
    def clear_words_for_new_round(self) -> None:
        """Clear all words said by players for a new round."""
        for player in self.players:
            player.word_said = None
        self.round += 1
    
    def format_words_said(self) -> str:
        """Format all words said by players for display."""
        lines = []
        for player in self.players:
            if player.is_alive and player.word_said:
                lines.append(f"{player.name}: {player.word_said}")
        return "\n".join(lines)
    
    def format_words_for_ai(self, exclude_player: Optional[Player] = None) -> str:
        """Format words said for AI context, excluding a specific player if provided."""
        lines = []
        for player in self.players:
            if player.is_alive and player.word_said and player != exclude_player:
                lines.append(f"{player.name}: {player.word_said}")
        return "\n".join(lines) if lines else "Ninguna palabra dicha aún"


class Game:
    """Main game controller."""
    
    def __init__(self, ai_names: Optional[List[str]] = None):
        self.ai_names = ai_names or ["Alice", "Bob", "Carlos", "Diana", "Elena", "Fernando", "Gabriela", "Hugo", "Isabel", "Javier", "Karla", "Luis", "María", "Nicolás", "Olivia", "Pedro", "Quinn", "Rosa", "Sergio", "Teresa"]
        self.npc_program = NPC()
        self.vote_program = Vote()
    
    def _generate_ai_names(self, num_ai_players: int) -> List[str]:
        """Generate AI player names dynamically."""
        if num_ai_players <= len(self.ai_names):
            return random.sample(self.ai_names, num_ai_players)
        
        names = list(self.ai_names)
        for i in range(len(self.ai_names), num_ai_players):
            names.append(f"Jugador {i + 1}")
        return names
    
    async def setup_game(self, num_players: int = 5, num_impostors: int = 1) -> GameState:
        """Set up a new game with random assignments.
        
        Args:
            num_players: Total number of players (minimum 3)
            num_impostors: Number of impostors (minimum 1, maximum num_players // 2)
        """
        if num_players < 3:
            raise ValueError("Se necesitan al menos 3 jugadores")
        if num_impostors < 1:
            raise ValueError("Debe haber al menos 1 impostor")
        if num_impostors > num_players // 2:
            raise ValueError(f"El número de impostores ({num_impostors}) no puede ser igual o mayor a {num_players // 2 + 1} (jugadores/2) con {num_players} jugadores")
        
        keyword, category = get_random_category_and_word()
        
        players = []
        human_player = Player(name="Tú", is_human=True, role=PlayerRole.JUGADOR)
        players.append(human_player)
        
        num_ai_players = num_players - 1
        ai_names = self._generate_ai_names(num_ai_players)
        
        for name in ai_names:
            players.append(Player(name=name, is_human=False, role=PlayerRole.JUGADOR))
        
        random.shuffle(players)
        
        impostors = random.sample(players, num_impostors)
        for impostor in impostors:
            impostor.role = PlayerRole.IMPOSTOR
        
        for i, player in enumerate(players):
            player.position = i
        
        return GameState(players=players, keyword=keyword, category=category)
    
    async def play_word_round(self, game_state: GameState) -> None:
        """Play a round where each player says a word."""
        alive_players = game_state.get_alive_players()
        
        for player in alive_players:
            if player.is_human:
                continue
            
            words_said_so_far = game_state.format_words_for_ai(exclude_player=player)
            player_names = ", ".join([p.name for p in alive_players])
            
            role = player.role.value
            secret_info = game_state.category if player.role == PlayerRole.IMPOSTOR else game_state.keyword
            
            word = await self.npc_program.aforward(
                role=role,
                secret_info=secret_info,
                words_said=words_said_so_far,
                player_names=player_names,
            )
            
            player.word_said = word
    
    async def collect_votes(self, game_state: GameState) -> dict[str, int]:
        """Collect votes from all alive players."""
        votes: dict[str, int] = {}
        alive_players = game_state.get_alive_players()
        active_player_names = [p.name for p in alive_players]
        
        all_words = game_state.format_words_said()
        active_players_str = ", ".join(active_player_names)
        
        for player in alive_players:
            if player.is_human:
                continue
            
            role = player.role.value
            secret_info = game_state.category if player.role == PlayerRole.IMPOSTOR else game_state.keyword
            
            vote = await self.vote_program.aforward(
                role=role,
                secret_info=secret_info,
                all_words=all_words,
                active_players=active_players_str,
                your_name=player.name,
            )
            
            vote = vote.strip()
            
            if vote in active_player_names and vote != player.name:
                votes[vote] = votes.get(vote, 0) + 1
        
        return votes
    
    async def collect_votes_parallel(self, game_state: GameState) -> dict[str, int]:
        """Collect votes from all AI players in parallel."""
        import asyncio
        
        alive_players = game_state.get_alive_players()
        active_player_names = [p.name for p in alive_players]
        
        all_words = game_state.format_words_said()
        active_players_str = ", ".join(active_player_names)
        
        async def get_vote(player: Player) -> tuple[str, Optional[str]]:
            """Get vote from a single player."""
            role = player.role.value
            secret_info = game_state.category if player.role == PlayerRole.IMPOSTOR else game_state.keyword
            
            vote = await self.vote_program.aforward(
                role=role,
                secret_info=secret_info,
                all_words=all_words,
                active_players=active_players_str,
                your_name=player.name,
            )
            
            vote = vote.strip()
            
            if vote in active_player_names and vote != player.name:
                return player.name, vote
            return player.name, None
        
        ai_players = [p for p in alive_players if not p.is_human]
        vote_results = await asyncio.gather(*[get_vote(player) for player in ai_players])
        
        votes: dict[str, int] = {}
        for _, vote in vote_results:
            if vote:
                votes[vote] = votes.get(vote, 0) + 1
        
        return votes
    
    def get_tied_players(self, votes: dict[str, int]) -> List[str]:
        """Get list of players tied for most votes."""
        if not votes:
            return []
        
        max_votes = max(votes.values())
        tied = [name for name, count in votes.items() if count == max_votes]
        return tied
    
    async def voting_round(self, game_state: GameState, human_vote: Optional[str] = None, auto_resolve_ties: bool = True) -> Tuple[str, dict[str, int]]:
        """Execute a voting round, optionally handling ties.
        
        Args:
            game_state: Current game state
            human_vote: Optional human player vote
            auto_resolve_ties: If True, automatically resolve ties. If False, return None for eliminated when there's a tie.
        
        Returns:
            Tuple of (eliminated_player_name, votes_dict). If auto_resolve_ties=False and there's a tie, eliminated will be None.
        """
        alive_players = game_state.get_alive_players()
        active_player_names = [p.name for p in alive_players]
        
        votes: dict[str, int] = {}
        
        if human_vote and human_vote in active_player_names:
            human_player = game_state.get_human_player()
            if human_player and human_player.is_alive:
                votes[human_vote] = votes.get(human_vote, 0) + 1
        
        ai_votes = await self.collect_votes(game_state)
        for name, count in ai_votes.items():
            votes[name] = votes.get(name, 0) + count
        
        tied_players = self.get_tied_players(votes)
        
        if len(tied_players) > 1:
            if auto_resolve_ties:
                return await self.resolve_tie(game_state, tied_players, human_vote)
            else:
                return None, votes
        
        eliminated = max(votes.items(), key=lambda x: x[1])[0] if votes else None
        return eliminated, votes
    
    async def collect_tie_votes_parallel(self, game_state: GameState, tied_players: List[str]) -> dict[str, int]:
        """Collect votes from AI players in a tie resolution round, in parallel."""
        import asyncio
        
        alive_players = game_state.get_alive_players()
        active_player_names = [p.name for p in alive_players if p.name in tied_players]
        
        if len(active_player_names) <= 1:
            return {}
        
        all_words = game_state.format_words_said()
        active_players_str = ", ".join(active_player_names)
        
        async def get_vote(player: Player) -> tuple[str, Optional[str]]:
            """Get vote from a single player."""
            role = player.role.value
            secret_info = game_state.category if player.role == PlayerRole.IMPOSTOR else game_state.keyword
            
            vote = await self.vote_program.aforward(
                role=role,
                secret_info=secret_info,
                all_words=all_words,
                active_players=active_players_str,
                your_name=player.name,
            )
            
            vote = vote.strip()
            
            if vote in active_player_names and vote != player.name:
                return player.name, vote
            return player.name, None
        
        ai_players = [p for p in alive_players if p.name in tied_players and not p.is_human]
        vote_results = await asyncio.gather(*[get_vote(player) for player in ai_players])
        
        votes: dict[str, int] = {}
        for _, vote in vote_results:
            if vote:
                votes[vote] = votes.get(vote, 0) + 1
        
        return votes
    
    async def resolve_tie(self, game_state: GameState, tied_players: List[str], human_vote: Optional[str] = None) -> Tuple[str, dict[str, int]]:
        """Resolve a voting tie by revoting among tied players."""
        alive_players = game_state.get_alive_players()
        active_player_names = [p.name for p in alive_players if p.name in tied_players]
        
        if len(active_player_names) <= 1:
            return active_player_names[0] if active_player_names else None, {}
        
        votes: dict[str, int] = {}
        
        if human_vote and human_vote in active_player_names:
            human_player = game_state.get_human_player()
            if human_player and human_player.is_alive and human_player.name in tied_players:
                votes[human_vote] = votes.get(human_vote, 0) + 1
        
        all_words = game_state.format_words_said()
        active_players_str = ", ".join(active_player_names)
        
        for player in alive_players:
            if player.name not in tied_players:
                continue
            
            if player.is_human:
                continue
            
            role = player.role.value
            secret_info = game_state.category if player.role == PlayerRole.IMPOSTOR else game_state.keyword
            
            vote = await self.vote_program.aforward(
                role=role,
                secret_info=secret_info,
                all_words=all_words,
                active_players=active_players_str,
                your_name=player.name,
            )
            
            vote = vote.strip()
            
            if vote in active_player_names and vote != player.name:
                votes[vote] = votes.get(vote, 0) + 1
        
        tied_again = self.get_tied_players(votes)
        
        if len(tied_again) > 1:
            return tied_again[0], votes
        
        eliminated = max(votes.items(), key=lambda x: x[1])[0] if votes else tied_players[0]
        return eliminated, votes
    
    def check_game_over(self, game_state: GameState, eliminated_name: str) -> Tuple[bool, Optional[bool]]:
        """Check if game is over and who won.
        
        Returns:
            Tuple of (is_over, innocents_won)
            - is_over: True if game ended, False if continues
            - innocents_won: True if innocents won, False if impostors won, None if game continues
        """
        eliminated_player = None
        for player in game_state.players:
            if player.name == eliminated_name:
                eliminated_player = player
                break
        
        if not eliminated_player:
            return False, None
        
        eliminated_player.is_alive = False
        
        if eliminated_player.role == PlayerRole.IMPOSTOR:
            alive_impostors = game_state.get_alive_impostors()
            if len(alive_impostors) == 0:
                return True, True
            else:
                return False, None
        else:
            if game_state.check_impostor_win_condition():
                return True, False
            else:
                return False, None
