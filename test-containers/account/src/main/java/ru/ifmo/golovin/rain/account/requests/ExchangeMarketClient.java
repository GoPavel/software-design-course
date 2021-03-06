package ru.ifmo.golovin.rain.account.requests;

import org.springframework.stereotype.Component;

import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

@Component
public class ExchangeMarketClient {
    final HttpClient client;
    final URI baseUri;

    public ExchangeMarketClient() throws URISyntaxException {
        System.out.println("ExchangeMarketClient initializing...");
        this.client = HttpClient.newHttpClient();
        this.baseUri = new URI("http://localhost:8080");
    }

    public int measure_price(String companyName, int count) throws IOException, InterruptedException {
        URI query_uri = this.baseUri.resolve(String.format("/stock_price?company=%s", companyName));
        System.out.println("Measuring income");
        System.out.println(String.format("ASK %s", query_uri));
        HttpRequest req = HttpRequest.newBuilder()
                .uri(query_uri)
                .GET()
                .build();
        HttpResponse<String> resp = this.client.send(req, HttpResponse.BodyHandlers.ofString());
        System.out.println("Got: " + resp);
        System.out.println("body: " + resp.body());
        int price = Integer.parseInt(resp.body());
        return price * count;
    }

    public boolean buy(String companyName, int count) throws IOException, InterruptedException {
        URI query_uri = this.baseUri.resolve(String.format("/buy_stocks?company=%s&amount=%s", companyName, count));
        System.out.println("buy stocks");
        System.out.println(String.format("ASK %s", query_uri));
        HttpRequest req = HttpRequest.newBuilder()
                .uri(query_uri)
                .GET()
                .build();
        HttpResponse<String> resp = this.client.send(req, HttpResponse.BodyHandlers.ofString());
        System.out.println("Got: " + resp);
        System.out.println("body: " + resp.body());
        return resp.body().contains("OK");
    }

    public boolean sale(String companyName, int count) throws IOException, InterruptedException {
        URI query_uri = this.baseUri.resolve(String.format("/sale_stocks?company=%s&amount=%s", companyName, count));
        System.out.println("Sale stocks");
        System.out.println(String.format("ASK %s", query_uri));
        HttpRequest req = HttpRequest.newBuilder()
                .uri(query_uri)
                .GET()
                .build();
        HttpResponse<String> resp = this.client.send(req, HttpResponse.BodyHandlers.ofString());
        System.out.println("Got: " + resp);
        System.out.println("body: " + resp.body());
        return resp.body().contains("OK");
    }

}
