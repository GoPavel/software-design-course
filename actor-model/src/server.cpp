#include <iostream>
#include <chrono>

#include <memory>

#include "caf/all.hpp"
#include "caf/io/all.hpp"

#include "server.h"

using std::cout;
using std::cerr;
using std::endl;
using std::chrono::seconds;

using namespace caf;
using namespace caf::io;

std::string aggregate_result(std::vector<Response> & responses)
{
   std::ostringstream ss;
   for (auto const & r: responses)
      if (r)
         ss << r << "\n";
   return ss.str();
}

std::future<Response> http_get(std::string const & query)
{
   std::promise<Response> p;
   auto f = p.get_future();
   p.set_value(42);
   return f;
}

search_worker::behavior_type google_search_worker()
{
   return {
      [=](std::string const & q)
      {
         auto fut = http_get(q);
         fut.wait();
         return fut.get();
      }
   };
}

search_worker::behavior_type yandex_search_worker()
{
   return {
      [=](std::string const & q)
      {
         auto fut = http_get(q);
         fut.wait();
         return fut.get();
      }
   };
}

search_worker::behavior_type bing_search_worker()
{
   return {
      [=](std::string const & q)
      {
         auto fut = http_get(q);
         fut.wait();
         return fut.get();
      }
   };
}

behavior meta_search_impl(stateful_actor<search_state> * self, broker * spawner)
{
   aout(self) << "Created meta_search_actor" << endl;
   auto gw = self->spawn(google_search_worker);
   auto yw = self->spawn(yandex_search_worker);
   auto bw = self->spawn(bing_search_worker);
   return {
      [=](query_atom, std::string const & query) mutable
      {
         std::array<search_worker, 3> ws{gw, yw, bw};
         for (auto const & w: ws)
            self->monitor(w);
         for (int i = 0; i < 3; ++i)
         {
            aout(self) << "meta_search_actor got query_atom" << endl;
            self->request(ws[i], infinite, query).then(
               [=](Response rsp) mutable
               {
                  auto & responses = self->state.responses;
                  aout(self) << "Request #" << i << " processed: " << rsp << endl;
                  responses.push_back(std::move(rsp));
                  aout(self) << "not processed yet: " << 3 - responses.size() << endl;
                  if (responses.size() == 3)
                  {
                     aout(self) << "Got all result" << endl;
                     self->send(spawner, return_atom::value, std::move(responses));
                     self->quit();
                  }
               });
         }
      },
      [=](timeout_query_atom)
      {
         auto & responses = self->state.responses;
         aout(self) << "Timeout exceeded, already collected " << responses.size() << " results" << endl;
         self->send(spawner, return_atom::value, std::move(responses));
         self->quit();
      }
   };
}

behavior connection_worker(broker * self, connection_handle hdl)
{
   aout(self) << "New worker created" << endl;
   self->configure_read(hdl, receive_policy::at_most(1024));
   return {
      [=](const new_data_msg & msg)
      {
         std::string query(msg.buf.begin(), msg.buf.end());
         aout(self) << "Worker got query: " << query << endl;
         auto meta_search_actor = self->spawn(meta_search_impl, self);
         self->monitor(meta_search_actor);
         self->send(meta_search_actor, query_atom::value, query);
         self->delayed_send(meta_search_actor, seconds(10), timeout_query_atom::value);
      },
      [=](const connection_closed_msg &)
      {
         self->quit();
      },
      [=](return_atom, std::vector<Response> result)
      {
         std::string payload = aggregate_result(result);
         aout(self) << "Respond result payload:\n" << payload << endl;
         self->write(hdl, payload.size(), payload.c_str());
         self->quit();
      }
   };
}

behavior server(broker * self)
{
   return {
      [=](const new_connection_msg & ncm)
      {
         aout(self) << "Start new connection, spawn worker" << endl;
         auto worker = self->fork(connection_worker, ncm.handle);
         self->monitor(worker);
         self->link_to(worker);
      }
   };
}

