package ru.ifmo.golovin.rain.account.dao;

import org.springframework.stereotype.Component;
import ru.ifmo.golovin.rain.account.models.Account;

import java.util.HashMap;

@Component
public class InMemoryDao implements Dao {
    private final HashMap<String, Account> db;

    public InMemoryDao() {
        this.db = new HashMap<>();
    }

    @Override
    public boolean createUser(String userName) {
        if (!this.db.containsKey(userName)) {
            this.db.put(userName, new Account(userName));
            return true;
        }
        System.out.println("Tried to create same user");
        return false;
    }

    @Override
    public boolean hasUser(String userName) {
        return this.db.containsKey(userName);
    }

    @Override
    public boolean addCash(String userName, int amount) {
        if (!this.db.containsKey(userName)) {
            System.out.println("Unknown user " + userName);
            return false;
        }
        this.db.get(userName).cash += amount;
        return true;
    }

    @Override
    public boolean removeCash(String userName, int amount) {
        if (!this.db.containsKey(userName)) {
            System.out.println("Unknown user " + userName);
            return false;
        }
        Account acc = this.db.get(userName);
        if (acc.cash < amount) {
            System.out.println("Tried to spend too many cash");
            return false;
        }
        this.db.get(userName).cash -= amount;
        return true;
    }

    @Override
    public Account getAccount(String userName) {
        return this.db.get(userName);
    }

    @Override
    public boolean removeStocks(String userName, String companyName, int count) {
        if (!this.db.containsKey(userName)) {
            System.out.println("Unknown user " + userName);
            return false;
        }
        Account acc = this.db.get(userName);
        int cur_stocks = acc.stocks.getOrDefault(companyName, 0);
        if (cur_stocks < count) {
            System.out.println("Try to buy too many stocks");
            return false;
        }
        acc.stocks.put(companyName, cur_stocks - count);
        return true;
    }

    @Override
    public boolean addStocks(String userName, String companyName, int count) {
        if (!this.db.containsKey(userName)) {
            System.out.println("Unknown user " + userName);
            return false;
        }
        Account acc = this.db.get(userName);
        acc.stocks.put(companyName, count);
        return true;
    }
}
