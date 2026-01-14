# DESIGN

### Worlds

A **World** is a single environment within which RPC requests can be made or satisfied, and resources serialized or deserialized. More precisely, these operations happen relative to a **Frame** within a **World**.

A **World** has a **WorldID**. Currently this is an incrementing integer, but it should eventually be a UUID.

A **World** also tracks currently executing **Frames**, via a **FrameManager**, which is a dictionary mapping **FrameIDs** to those **Frames**.

A **FrameManager** has a **root Frame** which is considered to be infinitely long-lived.

Currently **FrameManagers** only have a single root frame, but this limitation will be lifted for 0.2.

### Resources 

A **Resource** is a Python function, class, object, module, or coroutine. 

A **LocalRID** is Python’s`id(resource)`. It is stable while the resource exists, but once the resource is garbage collected, the **LocalRID** might get re-used for another resource. 

Just knowing a **LocalRID** doesn’t tell you what **World** the resource is from.

A **GlobalRID** is a universally unique ID for a resource, that never gets re-used even if the resource it refers to has been garbage collected. 

Knowing a **GlobalRID** does tell you which world the resource is from, and which **Frame** within that world it is from.

How this is achieved is by having **GlobalRID := tuple[WorldID, FrameID, LocalRID]**.

Over the course of time there might be more than one **GlobalRID** for a given resource, since it might participate in two frames A and B that are unrelated (e.g. neither A ≤ B nor B ≤ A).

### Frames

A **Frame** consists of a translation between **LocalRIDs**, **GlobalRIDs**, and actual local **Resources**.

A **Frame** has a **FrameID** that is unique within that world.

A **Frame** has a **parent** **Frame**.

**Frames** are created when one world makes a **Request** to another world. These frames are created with unique **FrameID**. The Request contains the new **FrameID** and the parent **FrameID**.

When this call is executed in the second world, a corresponding **Frame** is created in the second world with that new **FrameID**, that inherits all its bindings from the (matched) parent Frame.

A **Frame** maintains two dictionaries that map:

* **LocalRIDs** to **Resources**
* **LocalRIDs** to **GlobalRIDs**

### Requests

**Requests** are serialized with respect to a given **Frame.**

When a resource is serialized that does not yet have a **GlobalRID,** the above two dictionaries are updated, a **resource definition message** is produced that will update the dictionaries for the matched frame in the remote World. 

When a resource is serialized that already has a **GlobalRID**, a **resource reference message** is produced that only contains the **GlobalRID**.

**Requests** are deserialized in the remote world with respect to a matched frame (which will be created in the remote world using the given parent frame, looked up by ID).

Deserializing **resource definition messages** will cause a virtual resource to be created, and inserted into the above two dictionaries.

Deserializing resource reference messages will merely look up that GlobalRID to obtain the resource, which must have been defined in a previous message (in this new Frame or in some parent Frame of it).
