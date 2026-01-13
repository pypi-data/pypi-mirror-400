# splut
Actor model for Python.

This README is auto-generated, see [project wiki](https://wikiwheel.net/s/foyono/w/splut) for details.

## API

<a id="splut.actor"></a>

### splut.actor

<a id="splut.actor.ActorHandle"></a>

#### ActorHandle Objects

```python
class ActorHandle(Parabject)
```

<a id="splut.actor.ActorHandle.__getattr__"></a>

###### \_\_getattr\_\_

```python
def __getattr__(name)
```

Return a function to add a message to the mailbox, for execution by a capable worker when one becomes free.

<a id="splut.actor.ActorHandle.__getitem__"></a>

###### \_\_getitem\_\_

```python
def __getitem__(key)
```

Index or slice workers by the given key and return an actor handle backed by the resulting workers.

<a id="splut.actor.ActorHandle.__iter__"></a>

###### \_\_iter\_\_

```python
def __iter__()
```

For each worker, yield an actor handle backed by that worker specifically.

<a id="splut.actor.Spawn"></a>

#### Spawn Objects

```python
class Spawn()
```

<a id="splut.actor.Spawn.__init__"></a>

###### \_\_init\_\_

```python
def __init__(executor)
```

Spawned actors will use threads from the given executor.

<a id="splut.actor.Spawn.__call__"></a>

###### \_\_call\_\_

```python
def __call__(*objs)
```

Create an actor backed by the given worker object(s), each of which is used in a single-threaded way.
Calling a method on the returned actor returns a `Future` immediately, which eventually becomes done with the result of a worker method of the same name (or never if the worker method hangs).
A worker method may be async, in which case it can await futures returned by other actors, releasing the worker in the meantime.

<a id="splut.actor.Join"></a>

#### Join Objects

```python
class Join()
```

Make multiple futures awaitable as a unit. In the zero futures case this resolves (to an empty list) without suspending execution.
Otherwise if any future hangs, so does this. Otherwise if any future failed, all such exceptions are raised as a chain. Otherwise all results are returned as a list.

<a id="splut.actor.ManualExecutor"></a>

#### ManualExecutor Objects

```python
class ManualExecutor()
```

Utilise the main (or any other) thread directly.

<a id="splut.actor.ManualExecutor.run"></a>

###### run

```python
def run()
```

Execute tasks until interrupted. Typical usage is for the main thread to call this after setting up the system.

<a id="splut.actor.ManualExecutor.putinterrupt"></a>

###### putinterrupt

```python
def putinterrupt()
```

Cause exactly one thread to exit the `run` method soon.

<a id="splut.actor.future"></a>

### splut.actor.future

<a id="splut.actor.future.Future"></a>

#### Future Objects

```python
class Future()
```

<a id="splut.actor.future.Future.wait"></a>

###### wait

```python
def wait()
```

Block until there is an outcome, then return/raise it.
For use outside actors, or within one if you know the future is done and don't want to suspend execution with `await` in that case.

<a id="splut.actor.future.Future.andforget"></a>

###### andforget

```python
def andforget(log)
```

Send any exception to the given log.

<a id="splut.actor.future.Future.elf"></a>

###### elf

```python
def elf()
```

Create a future awaitable by the current event loop that has the same outcome as this one.

<a id="splut.bg"></a>

### splut.bg

<a id="splut.bg.Sleeper"></a>

#### Sleeper Objects

```python
class Sleeper()
```

<a id="splut.bg.Sleeper.interrupt"></a>

###### interrupt

```python
def interrupt()
```

If a sleep is in progress that sleep returns now, otherwise the next sleep will return immediately.
This is similar behaviour to interrupting a maybe-sleeping thread in Java.

<a id="splut.bg.delay"></a>

### splut.bg.delay

