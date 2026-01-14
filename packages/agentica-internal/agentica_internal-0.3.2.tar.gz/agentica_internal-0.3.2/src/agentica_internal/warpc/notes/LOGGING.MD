# LOGGING

To get work warp to emit log message to STDOUT, use:

* via an environment variable:
  * `AGENTICA_LOG_TAGS=1` to enable all logging
  * `AGENTICA_LOG_TAGS=ALL` ditto, with extra noisy stuff enabled
  * `AGENTICA_LOG_TAGS=DIR` to only enable loggers matching a directive
  * `SANDBOX_LOG_TAGS=DIR` overrides what log tags are enabled within the sandbox
  * `NOCOLOR=1` will turn off all coloring in log output

Programmatically within Python:
* `set_log_tags(spec)` where `spec` is:
  * `True` to enable most logging
  * `False` to disable all logging
  * `'DIR'` to give specific directives
*  `DebugWorld.connected_pair(..., logging=spec)` as above
* `set_log_tags` returns a reset function that will reset the current log tags to their original value.
* log tags are stored in a `ContextVar` that is thread-local.

### Customizing where logs are written

Via an environment variable:
* `AGENTICA_LOG="file1;file2"` write logs to the given files
* `AGENTICA_LOG="file1#pattern;..."` only write log lines that match the given pattern
* `SANDBOX_LOG_PATH="file_template.log"` for session manager, write each sandbox log to a file:
  * the file template can contain params `{sid}, {uid}` and `{sid_ts}`, `{sid_ymd}` etc.

Programmatically within Python:
* `set_log_streams(*io_specs)` will totally override where logs are written, this
  returns a reset function that will reset the current log streams to the original value.
* `add_log_stream(io_spec)` will add a new output stream.
* `io_spec` can be:
  * `'stdout', 'stderr'` to refer to the true system file handles
  * `'XXX/file.txt'` to open a file with uncolored output
  * `'XXX/file.log'` to open a file with ANSI colored output
  * `list object` to append strings to an existing list
* `with_log_streams` is a context manager that sets and unsets the current streams

### Redirecting logs to a single function

* `set_write_log_fn(fn)` supersedes the current streams with a function that is
  provided the log string; returns a reset function.
* `with_write_log_fn` via context manager

These are used inside the sandbox to redirect all log output to the host via the
`write_log` function provided to the guest.

### Tag directives

For `AGENTICA_LOG_TAGS`:
* `ALL`: enable all logging
* `<CLASSNAME>`: logging associated with a particular class (`SDKWorld, AgentWorld, Sandbox,
Context`, etc.)
* `ENCR`: encoding of resources into `ResourceData` objects
* `DECR`: decoding of `ResourceData` objects into resources
* `REPR`: lines starting with `<<<` or `>>>` to indicate commands send to REPL and their results
* `VIRT`: lines starting with `<--` and `-->` to indicate requests and responses triggered by virtual resources
* `TS`:   TypeScript
* `DIR1+DIR2+...`: enable multiple directives
* `+DIRS`: augment the existing log tags

The following groups of related classes are defined:
* `CORE`: REPL interaction and virtual resource callbacks
* `CODEC`: encoding and decoding of resources
* `VIRTUAL`: virtual resource callbacks
* `WORLD`: any and all worlds
* `SERVER`: server related classes
* `SANDBOX`: sandbox related classes
* `AGENT`: agent related: repl, agent world, virtualization
* `SDK`: agent, function, and client world
