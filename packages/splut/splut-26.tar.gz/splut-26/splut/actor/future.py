from threading import Condition
import asyncio

class NormalOutcome:

    def __init__(self, obj):
        self.obj = obj

    def result(self):
        return self.obj

    def forget(self, log):
        pass

class AbruptOutcome:

    def __init__(self, e):
        self.e = e

    def result(self):
        raise self.e

    def forget(self, log):
        log.error('Task failed:', exc_info = self.e)

class Future:

    def __init__(self):
        self.condition = Condition()
        self.callbacks = []
        self.outcome = None

    def set(self, outcome):
        assert outcome is not None
        with self.condition:
            assert self.outcome is None
            self.outcome = outcome
            self.condition.notify_all()
            callbacks, self.callbacks = self.callbacks, None
        for f in callbacks:
            f(outcome)

    def get(self):
        with self.condition:
            while True:
                outcome = self.outcome
                if outcome is not None:
                    return outcome
                self.condition.wait()

    def wait(self):
        '''Block until there is an outcome, then return/raise it.
        For use outside actors, or within one if you know the future is done and don't want to suspend execution with `await` in that case.'''
        return self.get().result()

    def listenoutcome(self, f):
        with self.condition:
            if self.callbacks is not None:
                self.callbacks.append(f)
                return
            outcome = self.outcome
        f(outcome)

    def __await__(self):
        return (yield self).result()

    def andforget(self, log):
        'Send any exception to the given log.'
        self.listenoutcome(lambda o: o.forget(log))

    def elf(self):
        'Create a future awaitable by the current event loop that has the same outcome as this one.'
        loop = asyncio.get_running_loop()
        g = loop.create_future()
        self.listenoutcome(lambda o: asyncio.run_coroutine_threadsafe(_transfer(o, g), loop))
        return g

async def _transfer(o, g):
    try:
        x = o.result()
    except BaseException as e:
        g.set_exception(e)
    else:
        g.set_result(x)
