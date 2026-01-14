# Warp Housekeeping

## Remove redundancy

There is a growing redundancy, in which there is a 'pure python' version of a 
data structure and a msgspec version of the same structure. 

* Virtual resource definitions: `warpc.virtual.ResourceData` <-> `warpc.messages.ResourceDataMsg`
* Virtual resource requests: `warpc.virtual.VRequest` <-> `warpc.messages.ResourceRequestMsg`

This is done to pipeline the process of building RPC into two phases, 
one involving mainly virtualization, resources, and their descriptions
(but no messages / frames), and the second involving resource descriptions
and messages and RPC. 

If we did not do this, the code that e.g. decomposes a class into a definition,
namely `warpc.virtual.to_class_definition`, would also have to encode the 
elements of the description recursively.

S
