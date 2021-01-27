import time
import sqlite3
import logging
import datetime
import threading
import pandas as pd
from ta import momentum, trend
from ta import volatility
from concurrent.futures import ThreadPoolExecutor
from binance.client import Client
from BotIndicator.Utility import client, conn

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-s %(message)s')

def markets(bases):
    pass

def signal():
    pass

def marketChoice(interval):
    products = client.get_exchange_info()
    #print(products['symbols'])
    data = products['symbols']
    criptos = []
    for elemento in data:
        #print(elemento['symbol'], elemento['market'])
        if elemento['quoteAsset'] == 'USDT':
            criptos.append(elemento['symbol'])
    #print(criptos)
    print("Elejimos las USDT")

    ascendientes = []
    moneda = []
    # tickers = client.get_ticker(symbol='OGNUSDT')
    for i in criptos:
        try:
            #print(i)
            tickers = client.get_ticker(symbol=i)
            #print(tickers)
            #print(float(tickers['quoteVolume']))
            if float(tickers['quoteVolume']) > 700000:  #float(tickers['priceChangePercent']) >= 0.3 and
                ascendientes.append(tickers['symbol'])
                moneda.append(i)
        except:
            pass
    #print(len(ascendientes))
    print("Tenemos los Ascendientes")
    return ascendientes
    #print(ascendientes)

def indice(symbol, interval):
    #markets = []
    #print(ascendientes)
    #for j in ascendientes:
    logging.debug("Thread con la criptomoneda de: " + symbol)
    dataset = client.get_klines(symbol=symbol, interval=interval, limit=21)
    data = pd.DataFrame(dataset, dtype=float)
    data.pop(1)
    data = data.iloc[:, :5]
    data = data.rename(
        columns={0: "FechaApertura", 2: 'ValorMaximo', 3: 'ValorMinimo', 4: 'Cierre', 5: 'Volumen'})
    columns = ['FechaApertura', 'ValorMaximo', 'ValorMinimo', 'Cierre', 'Volumen']
    data = data[columns]
    data = pd.DataFrame(data, dtype=float)
    #print(data)
    valorMaximo = data['ValorMaximo']
    valorMinimo = data['ValorMinimo']
    cierre = data['Cierre']
    volumen = data['Volumen']
        #fecha = data['FechaApertura']
    a = len(data.index) - 1
    #print(a)
    rsi = momentum.rsi(cierre, n=14, fillna=False)
    #print("El RSI: " + str(rsi))
    mfi = momentum.money_flow_index(valorMaximo, valorMinimo, cierre, volumen, n=14, fillna=True)
    #print("El MFI: " + str(mfi))
    boll_high = volatility.bollinger_hband(cierre, n=20, ndev=2, fillna=True)
    #print("El BOLLINGER: " + str(boll_high))
        # boll_low = volatility.bollinger_lband(cierre, n=20, ndev=2, fillna=True)
    #print(cierre[a], boll_high[a])
    ganancia = abs(((cierre[a] * 100) / boll_high[a]) - 100)
    print(ganancia)

    print(symbol, rsi[a - 1], rsi[a], ganancia)
    print(symbol, mfi[a - 1], mfi[a], ganancia)

    #if mercados(mfi, ganancia, a, rsi):
    #     markets.append(symbol)

    #print(markets)
    if mercados(mfi, ganancia, a, rsi):
        #    market = random.choice(markets)

        #    print("Imprime el mercado elegido: " + market)

        #### VALIDAMOS LA TABLA PARA LA MONEDA SELECCIONADA

        return symbol
    else:
        print("Mercado No Apropiado")
        return False

def mercados(mfi, ganancia, a, rsi):
    if 28 >= mfi[a] > mfi[a - 1] and ganancia > 0.5 and rsi[a - 1] < rsi[a] < 40:
        return True

def signals(rsi, ema, sma, mfi, a, cierre):
    if 50 <= rsi[a] > rsi[a - 1] and rsi[a - 1] < 70 and ema[a] > sma[2] \
            and ema[a - 2] < sma[0] and mfi[a] > mfi[a - 1] and cierre[a - 1] > sma[1]:
        return True


def main():
    bd = sqlite3.connect(conn.pathDB)
    cursor = bd.cursor()
    base = 'USDT'
    intervalo = Client.KLINE_INTERVAL_5MINUTE

    while True:

        ascendientes = marketChoice(intervalo)
        #indice(ascendientes, intervalo)
        print("Imprime los ascendientes")
        print(ascendientes)
        #s = threading.Semaphore(10)
        threads = list()
        exeutor = ThreadPoolExecutor(max_workers=10)
        for i in ascendientes:
            thr = exeutor.submit(indice, i, intervalo)
            #thr = threading.Thread(target=indice, args=(i, intervalo))
            threads.append(thr)
            time.sleep(0.1)
            #thr.start()
        results = list()
        for i in threads:
            print("Imprime el valor de thread: " + str(i.result()))
            #print(i)
            #th = i.join()
            if i.result():
                results.append(i.result())

        print(results)
        if len(results) != 0:
            break

    #    for i in markets:
    ##        market = i.replace(base, "")
     #       cursor.execute("SELECT Status FROM TB_Signals Where Cripto = ?", market)
     #       if 0 == cursor.fetchone() is None:
     #           cursor.execute("INSERT INTO TB_Signal(Cripto, Base, fechaSeñal, Status) VALUES(?,?,?,?)", market, base, datetime.datetime.now(), 1)
     #           bd.commit()


      #  while True:
      #      #if bandera_compra == 1:
      #      #    cursor.execute("SELECT Mercado FROM TB_TradesTest Where idTrade = ? ", (indice,))
      #      #    market = cursor.fetchone()[0]
            #    print("El mercado seleccionado es: " + market)
            #if bandera_compra != 1:
    print("Elegimos el mercado dentro del main")
     #       market = marketChoice(intervalo)
      #      time.sleep(2)
       #     if market is not False:
        #        print("EL mercado no es falso")
         #       break
         #   #validTable(market)
        #print("Comunicacion con binance websocket")
        #socket = comunication_binance.Socket(market, intervalo)
        #print("Ejecutamos la funcion wsocket()")
        #socket.wsocket()
        #print("Salimos de la ejecucion del wsocket()")


if __name__ == '__main__':
    main()
