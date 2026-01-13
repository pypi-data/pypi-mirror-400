import asyncio
import threading


class AsyncBridge:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run(self, coro):
        """Submit a coroutine to the loop and wait for the result."""
        return asyncio.run_coroutine_threadsafe(coro, self.loop).result()

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join()
