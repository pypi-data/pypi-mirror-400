import asyncio
import os
import random
import sys
from pathlib import Path

# Add parent to path so we can import the SDK
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from game_ai_arena_sdk import Bot, run, GameType, Move, GameStateLoop, GameStateEnd

# Use tunnel URL if set, otherwise localhost
MATCHMAKER_URL = os.getenv(
    "MATCHMAKER_URL",
    "wss://alleged-series-ethical-evans.trycloudflare.com/matchmaking/ws"
)

BOT1_ID = "d627b6d0-b937-46f1-bd7a-14f31b22fe62"
BOT1_KEY = "QVgg8P5LIiuaEMia-Lu1DXcBhdeenevoFKN7rjh0dC_k74bAUg2c0fF4JDPQTH_v"

BOT2_ID = "fac74dc9-6661-4265-a9a6-0e54d48dc94a"
BOT2_KEY = "ljSKFnjdjFufhfWAIjLw3nZzx9BVL42oz1GeZYvAsDQKaqkG-0zHOGZffySV6FlW"


class RandomBot(Bot):
    """A bot that makes random moves."""

    async def on_move(self, state: GameStateLoop) -> Move:
        # Pick a random piece that can move
        piece = random.choice(state.legal_moves)
        # Pick a random destination
        dest = random.choice(piece.valid_moves)
        return Move(from_pos=piece.pos, to_pos=dest)

    async def on_game_end(self, winner: str | None, state: GameStateEnd) -> None:
        if winner == state.my_side.value:
            print(f"[{self.id[:8]}] I won!")
        elif winner is None:
            print(f"[{self.id[:8]}] Draw!")
        else:
            print(f"[{self.id[:8]}] I lost!")


async def main():
    print(f"Connecting to: {MATCHMAKER_URL}")
    bot1 = RandomBot(BOT1_ID, BOT1_KEY)
    bot2 = RandomBot(BOT2_ID, BOT2_KEY)

    await asyncio.gather(
        run(bot1, GameType.FLIPFLOP_3X3, matchmaker_url=MATCHMAKER_URL),
        run(bot2, GameType.FLIPFLOP_3X3, matchmaker_url=MATCHMAKER_URL),
    )


if __name__ == "__main__":
    asyncio.run(main())
