package ru.ifmo.golovin.rain.exchange.models;


public class Company {
    public final String name;
    public int amount_stocks = 0;
    public int owned_stocks = 0;
    public int price = 1;

    public Company(String name) {
        this.name = name;
    }
}
