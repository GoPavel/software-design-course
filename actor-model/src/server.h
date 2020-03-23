#pragma once

#include "caf/all.hpp"
#include "caf/io/all.hpp"

using namespace caf;
using namespace caf::io;

using query_atom = atom_constant<atom("query")>;
using timeout_query_atom = atom_constant<atom("timeout")>;
using return_atom = atom_constant<atom("return")>;

using Response = int;

using search_worker = typed_actor<replies_to<std::string>::with<Response>>;

search_worker::behavior_type google_search_worker();

search_worker::behavior_type yandex_search_worker();

search_worker::behavior_type bing_search_worker();

struct search_state
{
   std::vector<Response> responses;
};

behavior meta_search_impl(stateful_actor<search_state>* self, broker* spawner);


behavior connection_worker(broker* self, connection_handle hdl);

behavior server(broker* self);

