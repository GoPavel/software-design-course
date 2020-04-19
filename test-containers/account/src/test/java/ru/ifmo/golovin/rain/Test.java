package ru.ifmo.golovin.rain;

import org.junit.Assert;
import org.junit.ClassRule;
import org.testcontainers.containers.FixedHostPortGenericContainer;
import org.testcontainers.containers.GenericContainer;
import ru.ifmo.golovin.rain.account.dao.InMemoryDao;
import ru.ifmo.golovin.rain.account.requests.ExchangeMarketClient;
import ru.ifmo.golovin.rain.account.requests.Handlers;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;


public class Test {
    @ClassRule
    public static GenericContainer simpleWebServer
            = new FixedHostPortGenericContainer("exchange-market:1.0-SNAPSHOT")
            .withFixedExposedPort(8080, 8080)
            .withExposedPorts(8080);

    public static ExchangeMarketClient exchange;

    private static void init_market(String company, int amount, int price) throws Exception {
        HttpRequest request1 = HttpRequest.newBuilder()
                .uri(new URI("http://localhost:8080/add_company?name=" + company))
                .GET()
                .build();
        HttpResponse<String> response1 = HttpClient.newHttpClient().send(request1, HttpResponse.BodyHandlers.ofString());
        Assert.assertEquals("OK", response1.body());

        HttpRequest request2 = HttpRequest.newBuilder()
                .uri(new URI(String.format("http://localhost:8080/add_stocks?company=%s&amount=%s", company, amount)))
                .GET()
                .build();
        HttpResponse<String> response2 = HttpClient.newHttpClient().send(request2, HttpResponse.BodyHandlers.ofString());
        Assert.assertEquals("OK", response2.body());

        HttpRequest request3 = HttpRequest.newBuilder()
                .uri(new URI(String.format("http://localhost:8080/reset_stock_price?company=%s&price=%s", company, price)))
                .GET()
                .build();
        HttpResponse<String> response3 = HttpClient.newHttpClient().send(request3, HttpResponse.BodyHandlers.ofString());
        Assert.assertEquals("OK", response3.body());
    }

    static {
        try {
            exchange = new ExchangeMarketClient();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @org.junit.Test
    public void test_test() throws Exception {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(new URI("http://localhost:8080/add_company?name=foo"))
                .GET()
                .build();

        HttpResponse<String> response = HttpClient.newHttpClient().send(request, HttpResponse.BodyHandlers.ofString());
        Assert.assertEquals("OK", response.body());
    }

    @org.junit.Test
    public void test_fail_buy() throws Exception {
        Handlers handles = new Handlers(new InMemoryDao(), exchange);
        String resp1 = handles.doAddAccount("Bob");
        Assert.assertEquals("OK", resp1);
        String resp2 = handles.doAddAccount("Bob");
        Assert.assertEquals("FAIL", resp2);

        String resp3 = handles.doAddAccount("Bob");
        Assert.assertEquals("FAIL", resp3);

        String info = handles.doInfo("Bob");
        Assert.assertEquals("User: Bob\nCash: 0\nStocks:\n", info);
    }

    @org.junit.Test
    public void test_buy() throws Exception {
        init_market("spacex", 10, 1);
        Handlers handlers = new Handlers(new InMemoryDao(), exchange);
        String resp1 = handlers.doAddAccount("John");
        Assert.assertEquals("OK", resp1);

        String resp2 = handlers.doAddCash("John", 100);
        Assert.assertEquals("OK", resp2);

        String resp3 = handlers.doBuy("John", "spacex", 10);
        Assert.assertEquals("OK", resp3);

        String info = handlers.doInfo("John");
        Assert.assertEquals("User: John\nCash: 90\nStocks:\n  company: spacex, count: 10\n", info);
    }

    @org.junit.Test
    public void test_buy_and_sale() throws Exception {
        init_market("ITMO", 10, 1);
        Handlers handlers = new Handlers(new InMemoryDao(), exchange);
        String resp1 = handlers.doAddAccount("John");
        Assert.assertEquals("OK", resp1);

        String resp2 = handlers.doAddCash("John", 100);
        Assert.assertEquals("OK", resp2);

        String resp3 = handlers.doBuy("John", "ITMO", 10);
        Assert.assertEquals("OK", resp3);

        String info1 = handlers.doInfo("John");
        Assert.assertEquals("User: John\nCash: 90\nStocks:\n  company: ITMO, count: 10\n", info1);

        HttpRequest req = HttpRequest.newBuilder()
                .uri(new URI(String.format("http://localhost:8080/reset_stock_price?company=%s&price=%s", "ITMO", 2)))
                .GET()
                .build();
        HttpResponse<String> resp4 = HttpClient.newHttpClient().send(req, HttpResponse.BodyHandlers.ofString());
        Assert.assertEquals("OK", resp4.body());

        String resp5 = handlers.doSale("John", "ITMO", 10);
        Assert.assertEquals("OK", resp5);

        String info2 = handlers.doInfo("John");
        Assert.assertEquals("User: John\nCash: 110\nStocks:\n  company: ITMO, count: 0\n", info2);
    }

    @org.junit.Test
    public void test_sale_too_many() throws Exception {
        init_market("ITMO1", 10, 1);
        Handlers handlers = new Handlers(new InMemoryDao(), exchange);
        String resp1 = handlers.doAddAccount("John");
        Assert.assertEquals("OK", resp1);

        String resp2 = handlers.doAddCash("John", 100);
        Assert.assertEquals("OK", resp2);

        String resp3 = handlers.doBuy("John", "ITMO1", 10);
        Assert.assertEquals("OK", resp3);

        String info1 = handlers.doInfo("John");
        Assert.assertEquals("User: John\nCash: 90\nStocks:\n  company: ITMO1, count: 10\n", info1);

        HttpRequest req = HttpRequest.newBuilder()
                .uri(new URI(String.format("http://localhost:8080/reset_stock_price?company=%s&price=%s", "ITMO1", 2)))
                .GET()
                .build();
        HttpResponse<String> resp4 = HttpClient.newHttpClient().send(req, HttpResponse.BodyHandlers.ofString());
        Assert.assertEquals("OK", resp4.body());

        String resp5 = handlers.doSale("John", "ITMO1", 11);
        Assert.assertEquals("FAIL: not enough stocks", resp5);

        String info2 = handlers.doInfo("John");
        Assert.assertEquals("User: John\nCash: 90\nStocks:\n  company: ITMO1, count: 10\n", info2);
    }

    @org.junit.Test
    public void test_buy_too_much() throws Exception {
        init_market("ITMO2", 10, 1);
        Handlers handlers = new Handlers(new InMemoryDao(), exchange);
        String resp1 = handlers.doAddAccount("John");
        Assert.assertEquals("OK", resp1);

        String resp2 = handlers.doAddCash("John", 100);
        Assert.assertEquals("OK", resp2);

        String resp3 = handlers.doBuy("John", "ITMO2", 15);
        Assert.assertEquals("FAIL", resp3);

        String info1 = handlers.doInfo("John");
        Assert.assertEquals("User: John\nCash: 100\nStocks:\n", info1);
    }

    @org.junit.Test
    public void test_too_expensive() throws Exception {
        init_market("ITMO3", 15, 1);
        Handlers handlers = new Handlers(new InMemoryDao(), exchange);
        String resp1 = handlers.doAddAccount("John");
        Assert.assertEquals("OK", resp1);

        String resp2 = handlers.doAddCash("John", 10);
        Assert.assertEquals("OK", resp2);

        String resp3 = handlers.doBuy("John", "ITMO3", 15);
        Assert.assertEquals("FAIL", resp3);

        String info1 = handlers.doInfo("John");
        Assert.assertEquals("User: John\nCash: 10\nStocks:\n", info1);
    }
}
