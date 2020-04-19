package ru.ifmo.golovin.rain.account.requests;

import org.springframework.stereotype.Component;
import ru.ifmo.golovin.rain.account.dao.Dao;
import ru.ifmo.golovin.rain.account.models.Account;

import java.io.IOException;
import java.util.stream.Collectors;

@Component
public class Handlers {
    final Dao db;
    final ExchangeMarketClient exchange;

    public Handlers(Dao db, ExchangeMarketClient exchange) {
        this.exchange = exchange;
        System.out.println("Handlers initializing...");
        this.db = db;
    }

    public String doAddAccount(String userName) {
        if (!this.db.createUser(userName)) {
            return "FAIL";
        }
        return "OK";
    }

    public String doAddCash(String userName, int amount) {
        if (!this.db.hasUser(userName)) {
            return "Unknown user";
        }
        if (!this.db.addCash(userName, amount)) {
            return "FAIL";
        }
        return "OK";
    }

    public String doInfo(String userName) {
        Account acc = this.db.getAccount(userName);
        if (acc == null) {
            return "Unknown user";
        }
        return String.format("User: %s\n", acc.name) +
                String.format("Cash: %s\n", acc.cash) +
                "Stocks:\n" +
                acc.stocks.entrySet()
                        .stream()
                        .map(e -> String.format("  company: %s, count: %s\n", e.getKey(), e.getValue()))
                        .collect(Collectors.joining());
    }

    public String doBuy(String userName, String companyName, int count) throws IOException, InterruptedException {
        Account acc = this.db.getAccount(userName);
        int neededCash = this.exchange.measure_price(companyName, count);
        if (neededCash > acc.cash) {
            return "FAIL";
        }
        if (!this.exchange.buy(companyName, count)) {
            return "FAIL";
        }
        if (!this.db.addStocks(userName, companyName, count)) {
            System.out.println("PANIC: partial fail");
            return "FAIL";
        }
        if (!this.db.removeCash(userName, neededCash)) {
            System.out.println("PANIC: partial fail");
            return "FAIL";
        }
        if (!this.db.addStocks(userName, companyName, count)) {
            System.out.println("PANIC: partial fail");
            return "FAIL";
        }
        return "OK";
    }

    public String doSale(String userName, String companyName, int count) throws IOException, InterruptedException {
        Account acc = this.db.getAccount(userName);
        if (acc.stocks.getOrDefault(companyName, -1) < count) {
            return "FAIL: not enough stocks";
        }
        int income = this.exchange.measure_price(companyName, count);
        if (!this.db.removeStocks(userName, companyName, count)) {
            return "FAIL";
        }
        if (!this.exchange.sale(companyName, count)) {
            System.out.println("PANIC: partial fail");
            return "FAIL";
        }
        if (!this.db.addCash(userName, income)) {
            System.out.println("PANIC: partial fail");
            return "FAIL";
        }
        return "OK";
    }
}
