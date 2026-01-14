# How futures are handled in warp

Futures are a bit of a special case, for several reasons:

1. they often come in matched pairs in an `AgentWorld` and an `SDKWorld`, where both are "real" 
   futures whose states are lazily synchronized
2.  unlike ordinary RPC in which one world requests that things happen in the world ("pull"), 
   futures allow one world (the one owning a future) *telling* the other world that a future 
   was completed ("push")
3. there are TWO ways that concrete Futures can arise:
   1. They are explicitly passed as arguments to remote functions, or returned from remote functions
   2. They are *immediately* created to *represent* the result of a remote call

Because of 3.2), a future can exist locally before the matched remote future exists, which means 
that the *calling world* must *define* a unique FutureID that the *executing world* should use
to refer that future.

## API Surface

The API surface involved is:

`BaseWorld` (via `WorldP`):
    `register_future`:   ensure that an existing future will send `FutureEventMsgs`
    `unregister_future`: undoes the above
    `send_future_event`: callback which sends `FutureEventMsgs` for registered futures
    `future_from_id`:    lookup an existing future or create a new one with a given `FutureID`
    `send_event`:        eventually send an `EventMsg`, but return immediately

Note: `register_future` requires that the future have a field `FUTURE_ID`, this is
set by `Frame.future_to_id` if it does not exist already.

`Frame` (via `EncoderP` and `DecoderP`)
    `future_from_id`: just redirects to the `world.future_from_id` for the frame's world
    `future_to_id`:   attaches a unique ID if one does not exist, and calls `world.register_future`

`virtual_async.py`:
    `register_virtual_future`:   adds done_callback so that agent can cancel a remote future
    `unregister_virtual_future`: undoes the above
    `send_future_request`:       callback which sends `FutureRequestMsg` when set locally

* For case 3.1, the two following functions are involved:
    * `Frame.future_to_id` is called when *describing* a local future, which ensures that the 
      future's local completion will *send* a `FutureEventMsg` to synchronize the remote future
    * `Frame.future_from_id` is called when *creating* a matched future, which ensures that 
      received `FutureEventMsgs` will cause the matched future to complete.

* For case 3.2, the FutureID is actually chosen to be the MessageID of the request message, 
  since that is known by both sides, and in particular is *chosen* by the requester. Such 
  futures should *not* cause `FutureEventMsgs` to be sent. In theory, that should also allow 
  cancellation by the requester, but we won't hook that up for now. 

Case 3.2 is accomplished via the `async_mode` attribute of the `Request` that originates RPC. A 
`Request` is a pure-python representations of RPC before it is encoded into a message 
(into a `FramedRequestMsg` containing a `RequestMsg`, specifically). 

The `async_mode` attribute of the `Request` can take on the values `'coro'`, `'future'`, `'sync'`, 
and `None`. For the value of`'future'`, the request will satisfy this RPC recipe: 

1) schedule a `FramedRequestMsg` to be sent *at some point*. when the other side receives the 
   `FramedRequestMsg`, it will decode back into a `request` with `async_mode='future'`, which will 
   cause the result to be awaited, formed into a `FramedResponseMsg`, and sent back
2) immediately return a `Future` whose `future_id` is this message ID
3) also ensure that the eventual `FramedRequestMsg`'s corresponding entry in the `awaiting` 
   dictionary of `Future[FramedResponseMsg]`s, has *that* future's done_callback set to a 
   function that will decode the response and use it to set future returned in step 2.

Case 3.2 is handled via `world.execute_outgoing_request_async`. 

## How local virtual resource requests engage this machinery:

`BaseWorld` has these methods that are used by `Frame.remote_resource_request_result`:
    `execute_outgoing_request_sync`: 
        sends a `FramedRequestMsg` and blocks until the `FramedResponseMsg`
    `execute_outgoing_request_coro`: 
        returns a `Coroutine[None, None, FramedResponseMsg`]; the coroutine does the above
    `execute_outgoing_request_future`:
        schedules a `FramedRequestMsg` and returns a `Future[FramedResponseMsg]`

These three methods are the building blocks used by the function 
`Frame.remote_resource_request_result`, which is the synchronous interface that virtual resource 
requests use to actually execute RPC synchronously. Which one to call depends on the `async_mode`
of the underlying `Request` object that was sent to the virtual resource handle via 
`handle @ request`, as follows:

* If a request is marked as `sync_mode='coro'`, it will use `execute_outgoing_request_coro` to 
  *immediately* return a coroutine.
* If a request is marked as `sync_mode='future'`, it will use `execute_outgoing_request_future` 
  to immediately return a `Future`.
* Otherwise, it is an ordinary synchronous request.

## How futures interact with AgentWorld

By default, as soon as an agent awaits a virtual future (likely via `asyncio.run()` of its own 
`async def main()` that contains an `await future`), the entire agent event loop WILL go to sleep 
and never wake up.  

That is because futures are the single place where 'being woken up' has to happen "from outside",
usually via another task in the event loop calling `set_result` or `cancel`. Conceptually the 
"other task" is remote, on the SDK side. The customer sets their future, which triggers a 
`FutureEventMsg` to be sent to the AgentWorld, which causes `warp_recv_bytes` to return. 
Working backward, this implies that a task was running in the `AgentWorld`, and this task MUST be 
the transient "futures task" that `AgentWorld.start_futures_task` creates.

The "futures task" is the mechanism that underlies the awkward 'hybrid mode' that `AgentWorld` is 
forced to deal use. If an agent decides to use asyncio, and it awaits something that is behind RPC,
we have to start the futures task that will block the (only) thread via warp_recv_bytes and keep 
the agent thread responsive. 

In other places, this is done via `AgentWorld.start_futures_task`, which runs 
`AgentWorld.futures_task` in an `asyncio.Task`. This task will run a message loop until all the 
futures currently outstanding are complete, and takes over the duties that are normally performed by 
`run_until_mid`. It introduces an `asyncio.sleep(0)` to ensure that the `recv_msg` is only called  
a last resort once all other tasks have run. This ensures we will not block on `warp_recv_bytes`
until there is nothing else to do -- NOTE that even this is incorrect, as a *local* `asyncio.sleep` 
task will never be able to interrupt this last-resort blocking call, so at best this is a temporary
solution.

(For background, `run_until_mid` is what allows virtual resource requests to execute synchronously,
and the futures task is the corresponding idea when asyncio is active in the agent world. They 
co-operate: within an asyncio task, we can still call `run_until_mid` whenever we want, whereas 
nested message loops are not possible in asyncio despite this being an obviously useful 
thing that I believe trio DOES support.)

Hence, `AgentWorld` needs to start up a` futures_task` as soon as a virtual future is awaited. To do
this, virtual futures are not actually instances of `Future` but rather of `core.futures.
HookableFuture` that intercept various calls, including calls to `__await__`.

## GatheringFutures

As mentioned in the previous paragraph, virtual futures inside `AgentWorld` need to intercept
calls to `await` to ensure that the `futures_task` is running. But due to the behavior of 
`asyncio.gather`, they must also intercept calls to `add_done_callback`, because `asyncio.gather`
creates a `GatheringFuture` rather than an ordinary future (which merely changes the behavior of
`.cancel`). `GatheringFuture` does not ever directly await its children (which one would it await?).
Instead, it calls `add_done_callback` on all of them, with the function being a count-decrementer.

## Potential simplifications

1. Have the 'awaiting' futures dict values be just `Future`, instead of `Future[FramedResponseMsg]` 
   and we receive a `FramedResponseMsg` we immediately decode it into a `Result` and use that 
   Result to set the `Future` directly. This would avoid the need for two separate dicts, but 
   would tie AgentWorld into using asyncio futures from the beginning, which may make the hybrid 
   msg-loop + asyncio behavior unworkable? Or maybe not.

2. Delete the older `FutureResultMsg <: SidebandMsg` in favor of `FutureEventMsg`, they are 
   basically the same functionality

3. Add a polling interface to the `ExecEnv` WA world interface so that ExecEnv can run a 
   "native" event loop that is always running a background asyncio task, this will allow us to 
   support `await` natively in the REPL without forcing the agent to use `asyncio.run`, which 
   will massively simplify the hybrid mode implemented by `AgentWorld`.
