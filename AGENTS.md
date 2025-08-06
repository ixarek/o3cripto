0. ВСЕГДА ДЕЛАЙ ТЕСТЫ НА КАЖДОМ ЭТАПЕ! (ВСЕГДА!)

1. Сейчас идёт этап настройки торгового клиента Bybit. Необходимо получить баланс.
   Пример настроек можно взять из https://github.com/ixarek/bybitbotgpt.git. (пройдено)

2. Баланс получен успешно. Проблема была в неправильном .env файле. (пройдено)

3. Сейчас идёт этап разработки торгового бота. Требуется создать бота, который будет торговать на парах BTCUSDT, ETHUSDT, SOLUSDT, XRPUSDT, DOGEUSDT и BNBUSDT. Бот должен использовать лучшие практики торговли. Можешь посмотреть в интернете, как это делается. Выполняй тесты и записывай в зависимости все модули, которые требуются для выполнения тестов. Сейчас тебе нужно выполнить задачу выставления и закрытия ордера. Ордера должны быть выставлены от 80 до 120 долларов. Плечо от 10 до 20 (следовательно, цена позиции от 800 до 2400 долларов). Сделай код, проведи тесты. (пройдено)

4. Сейчас нужно взять последние 50 свечей (5‑минутки) каждой позиции и выяснить, куда идёт курс валюты. Данные должны передаваться в лог (валюта активно продается и цена уменьшается или наоборот). (пройдено)

5. Сейчас надо добавить метод торговли. Предложи варианты, которые больше всего подходят на 2025 год (для автономной работы бота). (пройдено)

6. Текст ИИ (Добавлен автоматический запуск стратегии пересечения скользящих средних: main теперь перебирает все разрешённые пары и вызывает trade_with_ma, логируя успешные сделки и ошибки). По факту имеются ошибки:
   ERROR:__main__:BTCUSDT: trade failed: leverage not modified (ErrCode: 110043) (ErrTime: 07:38:02).
   Request → POST https://api-demo.bybit.com/v5/position/set-leverage: {"category": "linear", "symbol": "BTCUSDT", "buyLeverage": "10", "sellLeverage": "10"}.
   ERROR:__main__:ETHUSDT: trade failed: leverage not modified (ErrCode: 110043) (ErrTime: 07:38:02).
   Request → POST https://api-demo.bybit.com/v5/position/set-leverage: {"category": "linear", "symbol": "ETHUSDT", "buyLeverage": "10", "sellLeverage": "10"}.
   ERROR:__main__:SOLUSDT: trade failed: leverage not modified (ErrCode: 110043) (ErrTime: 07:38:03).
   Request → POST https://api-demo.bybit.com/v5/position/set-leverage: {"category": "linear", "symbol": "SOLUSDT", "buyLeverage": "10", "sellLeverage": "10"}.
   ERROR:__main__:XRPUSDT: trade failed: leverage not modified (ErrCode: 110043) (ErrTime: 07:38:03).
   Request → POST https://api-demo.bybit.com/v5/position/set-leverage: {"category": "linear", "symbol": "XRPUSDT", "buyLeverage": "10", "sellLeverage": "10"}.
   ERROR:__main__:DOGEUSDT: trade failed: leverage not modified (ErrCode: 110043) (ErrTime: 07:38:04).
   Request → POST https://api-demo.bybit.com/v5/position/set-leverage: {"category": "linear", "symbol": "DOGEUSDT", "buyLeverage": "10", "sellLeverage": "10"}.
   ERROR:__main__:BNBUSDT: trade failed: leverage not modified (ErrCode: 110043) (ErrTime: 07:38:04).
   Request → POST https://api-demo.bybit.com/v5/position/set-leverage: {"category": "linear", "symbol": "BNBUSDT", "buyLeverage": "10", "sellLeverage": "10"}.

   Необходимо найти причину и исправить. Запустить у себя bot.py и проверить работу. (пройдено)

7. Сейчас получилось выставить позиции DOGEUSDT и XRPUSDT (но SL и TP не установлены), также есть ошибки в bot.py
   INFO:__main__:BTCUSDT: actively bought, price increases
   INFO:__main__:ETHUSDT: actively bought, price increases
   INFO:__main__:SOLUSDT: actively bought, price increases
   INFO:__main__:XRPUSDT: actively bought, price increases
   INFO:__main__:DOGEUSDT: actively bought, price increases
   INFO:__main__:BNBUSDT: actively bought, price increases
   INFO:__main__:BTCUSDT: leverage already set to 10
   ERROR:__main__:BTCUSDT: trade failed: The number of contracts exceeds maximum limit allowed: too large, order_qty:100000000000 > max_qty:11900000000 (ErrCode: 10001) (ErrTime: 07:56:17).
   Request → POST https://api-demo.bybit.com/v5/order/create: {"category": "linear", "symbol": "BTCUSDT", "side": "Buy", "orderType": "Market", "qty": "1000", "timeInForce": "ImmediateOrCancel"}.
   INFO:__main__:ETHUSDT: leverage already set to 10
   ERROR:__main__:ETHUSDT: trade failed: The number of contracts exceeds maximum limit allowed: too large, order_qty:100000000000 > max_qty:72400000000 (ErrCode: 10001) (ErrTime: 07:56:17).
   Request → POST https://api-demo.bybit.com/v5/order/create: {"category": "linear", "symbol": "ETHUSDT", "side": "Buy", "orderType": "Market", "qty": "1000", "timeInForce": "ImmediateOrCancel"}.
   INFO:__main__:SOLUSDT: leverage already set to 10
   ERROR:__main__:SOLUSDT: trade failed: ab not enough for new order (ErrCode: 110007) (ErrTime: 07:56:18).
   Request → POST https://api-demo.bybit.com/v5/order/create: {"category": "linear", "symbol": "SOLUSDT", "side": "Buy", "orderType": "Market", "qty": "1000", "timeInForce": "ImmediateOrCancel"}.
   INFO:__main__:XRPUSDT: leverage already set to 10
   INFO:__main__:XRPUSDT: order placed {'retCode': 0, 'retMsg': 'OK', 'result': {'orderId': 'bcfb4672-9ebf-484e-8ea4-308e09c595b5', 'orderLinkId': ''}, 'retExtInfo': {}, 'time': 1754466979110}
   INFO:__main__:DOGEUSDT: leverage already set to 10
   INFO:__main__:DOGEUSDT: order placed {'retCode': 0, 'retMsg': 'OK', 'result': {'orderId': '7af412fe-c77a-48d8-97f7-0b71626bee07', 'orderLinkId': ''}, 'retExtInfo': {}, 'time': 1754466980415}
   INFO:__main__:BNBUSDT: leverage already set to 10
   ERROR:__main__:BNBUSDT: trade failed: ab not enough for new order (ErrCode: 110007) (ErrTime: 07:56:21).
   Request → POST https://api-demo.bybit.com/v5/order/create: {"category": "linear", "symbol": "BNBUSDT", "side": "Buy", "orderType": "Market", "qty": "1000", "timeInForce": "ImmediateOrCancel"}. (пройдено частично).
   8. Исправлено: добавлено округление количества до шага биржи, позиции по всем парам успешно выставляются. (пройдено)
   9. Смотря на уровни поддержки и общий тренд 5 минутных, а также 15 минутных свечей, установить SL TP позиций. Также ввести проверку, что позицию нельзя выставить без SL TP. SL TP должны быть выставлены исходя из логики и могут быть разного %. Возможно потребуется добавить дополнительные индикаторы для проверки корректности выставления SL TP. (работаем тут!)
