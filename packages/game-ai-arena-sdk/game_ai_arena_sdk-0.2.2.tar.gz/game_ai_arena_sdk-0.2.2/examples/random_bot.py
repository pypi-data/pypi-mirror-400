"""
Example bot that makes random moves.

Usage:
    # Set environment variables
    export MATCHMAKER_URL=ws://192.168.2.106:9000/matchmaking/ws
    export BOT1_ID=your-bot-id
    export BOT1_KEY=your-bot-api-key

    # Optional: run two bots against each other
    export BOT2_ID=your-second-bot-id
    export BOT2_KEY=your-second-bot-api-key

    # Run
    python -m game_ai_arena_sdk.examples.random_bot
"""

import asyncio
import os
import random
import sys

from game_ai_arena_sdk import Bot, run, GameType, Move, GameStateLoop, GameStateEnd

# Get matchmaker URL from environment
MATCHMAKER_URL = os.getenv("MATCHMAKER_URL", "ws://127.0.0.1:9000/matchmaking/ws")

# Get bot credentials from environment
BOT1_ID = os.getenv("BOT1_ID")
BOT1_KEY = os.getenv("BOT1_KEY")
BOT2_ID = os.getenv("BOT2_ID")
BOT2_KEY = os.getenv("BOT2_KEY")


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
    # Validate required credentials
    if not BOT1_ID or not BOT1_KEY:
        print("Error: BOT1_ID and BOT1_KEY environment variables are required")
        print()
        print("Usage:")
        print("  export MATCHMAKER_URL=ws://your-server:9000/matchmaking/ws")
        print("  export BOT1_ID=your-bot-id")
        print("  export BOT1_KEY=your-bot-api-key")
        print()
        print("  # Optional: second bot for local testing")
        print("  export BOT2_ID=second-bot-id")
        print("  export BOT2_KEY=second-bot-api-key")
        print()
        print("  python -m game_ai_arena_sdk.examples.random_bot")
        sys.exit(1)

    print(f"Connecting to: {MATCHMAKER_URL}")

    bot1 = RandomBot(BOT1_ID, BOT1_KEY)

    # If second bot credentials provided, run both
    if BOT2_ID and BOT2_KEY:
        print(f"Running 2 bots: {BOT1_ID[:8]}... and {BOT2_ID[:8]}...")
        bot2 = RandomBot(BOT2_ID, BOT2_KEY)
        await asyncio.gather(
            run(bot1, GameType.FLIPFLOP_3X3, matchmaker_url=MATCHMAKER_URL),
            run(bot2, GameType.FLIPFLOP_3X3, matchmaker_url=MATCHMAKER_URL),
        )
    else:
        print(f"Running 1 bot: {BOT1_ID[:8]}... (waiting for opponent)")
        await run(bot1, GameType.FLIPFLOP_3X3, matchmaker_url=MATCHMAKER_URL)


if __name__ == "__main__":
    asyncio.run(main())
