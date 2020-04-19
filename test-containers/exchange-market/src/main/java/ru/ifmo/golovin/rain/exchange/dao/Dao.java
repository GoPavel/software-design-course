package ru.ifmo.golovin.rain.exchange.dao;

import ru.ifmo.golovin.rain.exchange.models.Company;

public interface Dao {

    boolean addCompany(Company company);

    boolean addStocks(String companyName, int amount);

    int getStockPrice(String companyName);

    int getAmountStocks(String companyName);

    boolean acquireStocks(String companyName, int amount);

    boolean releaseStocks(String companyName, int amount);

    boolean resetStockPrice(String companyName, int price);
}
