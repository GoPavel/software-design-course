package ru.ifmo.golovin.rain.exchange;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import ru.ifmo.golovin.rain.exchange.dao.Dao;
import ru.ifmo.golovin.rain.exchange.models.Company;

@RestController
public class Controller {
    private final Dao db;

    public Controller(Dao dao) {
        System.out.println("Controller initializing...");
        this.db = dao;
    }

    @RequestMapping("/add_company")
    public String addCompany(String name) {
        if (this.db.addCompany(new Company(name))) {
            return "OK";
        }
        return "FAIL";
    }

    @RequestMapping("/add_stocks")
    public String addStocks(String company, int amount) {
        if (this.db.addStocks(company, amount)) {
            return "OK";
        }
        return "FAIL";
    }

    @RequestMapping("/stock_price")
    public String getStockPrice(String company) {
        int price = this.db.getStockPrice(company);
        return String.format("%s", price);
    }

    @RequestMapping("/amount_stocks")
    public String getAmountStocks(String company) {
        int cnt = this.db.getAmountStocks(company);
        return String.format("%s", cnt);
    }

    @RequestMapping("/buy_stocks")
    public String buyStocks(String company, int amount) {
        if (this.db.acquireStocks(company, amount)) {
            return "OK";
        }
        return "FAIL";
    }

    @RequestMapping("/sale_stocks")
    public String saleStocks(String company, int amount) {
        if (this.db.releaseStocks(company, amount)) {
            return "OK";
        }
        return "FAIL";
    }

    @RequestMapping("/reset_stock_price")
    public String resetStockPrice(String company, int price) {
        if (this.db.resetStockPrice(company, price)) {
            return "OK";
        }
        return "FAIL";
    }

}
