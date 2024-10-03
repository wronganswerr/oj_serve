from dramatiq.middleware.asyncio import AsyncIO


class AsyncIOWithUvLoop(AsyncIO):
    def before_worker_boot(self, broker, worker):
        import uvloop
        uvloop.install()
        super().before_worker_boot(broker, worker)
