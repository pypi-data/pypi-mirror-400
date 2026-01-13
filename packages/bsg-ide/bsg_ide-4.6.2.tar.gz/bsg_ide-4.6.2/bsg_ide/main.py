import asyncio
from typing import Optional
from .core.editor import SlideEditor
from .core.terminal import TerminalIO
from .core.presentation import PresentationManager

class BSG_IDE:
    def __init__(self):
        self.editor: Optional[SlideEditor] = None
        self.terminal: Optional[TerminalIO] = None
        self.presentation: Optional[PresentationManager] = None

    async def initialize(self):
        """Async initialization of all components"""
        self.editor = SlideEditor()
        self.terminal = TerminalIO()
        self.presentation = PresentationManager()

        # Parallel initialization
        await asyncio.gather(
            self.editor.initialize(),
            self.terminal.start_async()
        )

    def run(self):
        """Main application loop"""
        asyncio.run(self._run_async())

    async def _run_async(self):
        """Async application runner"""
        await self.initialize()
        # Main application logic here

def main():
    app = BSG_IDE()
    app.run()

if __name__ == "__main__":
    main()
