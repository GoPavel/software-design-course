package ru.ifmo.golovin.rain.account.dao;

import ru.ifmo.golovin.rain.account.models.Account;

public interface Dao {

    boolean createUser(String userName);

    boolean hasUser(String userName);

    boolean addCash(String userName, int amount);

    boolean removeCash(String userName, int amount);

    Account getAccount(String userName);

    boolean removeStocks(String userName, String companyName, int count);

    boolean addStocks(String userName, String companyName, int count);
}
