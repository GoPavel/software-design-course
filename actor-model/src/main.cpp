#include "caf/all.hpp"
#include "caf/io/all.hpp"

#include "server.h"

using namespace caf;
using std::cout;
using std::cerr;
using std::endl;

class config : public actor_system_config {
public:
   uint16_t port = 8083;

   config() {
      opt_group{custom_options_, "global"}
         .add(port, "port,p", "set port")
         .add<std::string>("console", "colored")
         ;
   }
};

void caf_main(actor_system& system, const config& cfg) {
   auto server_actor = system.middleman().spawn_server(server, cfg.port);
   if (!server_actor) {
      cerr << "*** cannot spawn server: "
           << system.render(server_actor.error()) << endl;
      return;
   }
   cout << "*** listening on port " << cfg.port << endl;
   cout << "*** to quit the program, simply press <enter>" << endl;
   // wait for any input
   std::string dummy;
   std::getline(std::cin, dummy);
   // kill server
   anon_send_exit(*server_actor, exit_reason::user_shutdown);
}

CAF_MAIN(io::middleman)