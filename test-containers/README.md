## test-containers

### Build and run test

```bash
mvn -am -pl exchange-market package
mvn -am -pl account test
```

### API examples

#### exchange-market

- `/add_company?name=spacex`
- `/add_stocks?company=spacex`
- `/stock_price?company=spacex` 

return current stock price
- `/amount_stocks?company=spacex&amount=1` 

return amount stock, that available to sale

- `/buy_stocks?company=spacex&amount=1`
- `/sale_stocks?company=spacex&amount=1`
- `reset_stock_price?company=spacex&price=2`

Replace price of stocks with new value

#### account

- `/add_account?name=Bob`

create new account

- `/add_cash?name=Bob&amount=50`

add cash on account

- `/info?name=Bob`

example of response:
```bash
User: bob
Cash: 95
Stocks:
  company: spacex, count: 5
```

- `/buy?name=Bob&company=spacex&count=5`
- `/sale?name=Bob&company=spacex&count=5`