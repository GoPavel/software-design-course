#define CAF_SUITE actor-model

#include "chrono"

#include "caf/all.hpp"
#include "caf/io/all.hpp"
#include "caf/test/dsl.hpp"
#include "caf/test/unit_test_impl.hpp"

//#define CATCH_CONFIG_MAIN
//#include "catch2/catch.hpp"

#include "server.h"

using namespace caf;
using namespace caf::io;
using std::chrono::seconds;

using test_atom = atom_constant<atom("test")>;

struct fixture
{
   caf::actor_system_config cfg;
   caf::actor_system sys;
   caf::scoped_actor self;

   fixture()

      : cfg()
      , sys(cfg.load<io::middleman>())
      , self(sys)
   {
      assert (sys.has_middleman());
   }
};
CAF_TEST_FIXTURE_SCOPE(actor_tests, fixture)

   CAF_TEST(simple test google_search_worker)
   {
      auto act = self->spawn(google_search_worker);
      std::string q = "hello";
      self->request(act, infinite, q).receive(
         [=](Response rsp)
         {
            CAF_CHECK(rsp == 42);
         },
         [&](caf::error & err)
         {
            // Must not happen, stop test.
            CAF_FAIL(sys.render(err));
         });
   }


   behavior mock_connection_broker(broker * self)
   {
      return {
         [=](return_atom, std::vector<Response> result)
         {
            for (auto const & rsp: result) {
               CAF_CHECK(rsp == 42);
            }
            self->quit();
         },
         [=](test_atom){
            std::string query = "Hello";
            auto meta_search_actor = self->spawn(meta_search_impl, self);
            self->monitor(meta_search_actor);
            self->send(meta_search_actor, query_atom::value, query);
            self->delayed_send(meta_search_actor, seconds(10), timeout_query_atom::value);
         }
      };
   }
   CAF_TEST(simple test meta_search)
   {
      auto mock_broker = sys.middleman().spawn_broker(mock_connection_broker);
      self->send(mock_broker, test_atom::value);
      self->wait_for(mock_broker);
   }

CAF_TEST_FIXTURE_SCOPE_END()