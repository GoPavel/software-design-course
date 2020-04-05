## Event-source fitness center

### Overview

Three services (manager_admin, report service, turnstile service) over one store with events.

### Feathers
#### Dynamic typed event

We can create a new service without reloading entire system. But there is some trade-off.
When we create a new event type, we must register it to `EVENT_TYPE_TO_EVENT_CLASS`. 
It allows Mongo client to deserialize and validate documents. But so the success of deserialization 
depend on loaded models (from other modules).