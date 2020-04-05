## Event-source fitness center

### Overview

Three services (manager_admin, report service, turnstile service) over one store with events.

#### Feathers
##### Dynamic typed event

We can create a new service without reloading entire system. But there is some trade-off.
When we create a new event type, we must register it to `EVENT_TYPE_TO_EVENT_CLASS`. 
It allows Mongo client to deserialize and validate documents. But so the success of deserialization 
depend on loaded models (from other modules).

##### CQRS

If service needs only read-only query to event-database then it can use `EventReader` or make subclass. Also potentially, it allows using different data models over `EventReader` and `EventWriter`.

.
#### Example

```bash
$ python manager_admin.py create Pavel 
Ticket created with number: 28

$ python turnstile.py 28 --in
FAIL  

$ python manager_admin.py extend 28 --day 100   # set a deadline of 100 days from now

$ python turnstile.py 28 --in
OK
$ python turnstile.py 28 --out

$ python report.py update # recalc daily reports for last 3 days and save to store
{'day': '2020-04-05 00:00:00', 'mean_visit_duration': 0.0, 'visit_freq': 0.08333333333333333}
{'day': '2020-04-04 00:00:00', 'mean_visit_duration': 0, 'visit_freq': 0.0}
{'day': '2020-04-03 00:00:00', 'mean_visit_duration': 0, 'visit_freq': 0.0}
```
