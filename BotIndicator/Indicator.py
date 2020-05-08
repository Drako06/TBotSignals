import time

from binance.client import Client
#import math
import random
from ta import momentum
from ta import volatility
from BotIndicator.Utility import client, bd
#from BotIndicator.CheckTable import validTable
#from BotIndicator import comunication_binance
import pandas as pd
import sqlite3
#from RFunctions.CheckTable import validTable

#from RFunctions.comunication_binance import wsocket



def marketChoice(interval):

    products = client.get_products()
    #market = 'MATICUSDT'

    data = products['data']
    criptos = []
    for elemento in data:
        #print(elemento['symbol'], elemento['market'])
        if elemento['market'] == 'USDT':
            criptos.append(elemento['symbol'])
    #print(criptos)
    print("Elejimos las USDT")

    ascendientes = []
    # tickers = client.get_ticker(symbol='OGNUSDT')
    for i in criptos:
        try:
            #print(i)
            tickers = client.get_ticker(symbol=i)
            #print(tickers)
            #print(float(tickers['quoteVolume']))
            if float(tickers['quoteVolume']) > 700000:  #float(tickers['priceChangePercent']) >= 0.3 and
                ascendientes.append([tickers['symbol'], tickers['priceChangePercent']])
        except:
            pass
    #print(len(ascendientes))
    print("Tenemos los Ascendientes")
    #print(ascendientes)

    """
    ascendientes = ['VETUSDT', 'MATICUSDT', 'XLMUSDT', 'BULLUSDT'] #, 'TRXUSDT', 'IOSTUSDT'
                    #'EOSUSDT']  # , 'ETCUSDT', 'BNBUSDT', 'XLMUSDT', 'MATICUSDT']
    """
    markets = []

    #ascendientes = ['VETUSDT', 'MATICUSDT', 'BULLUSDT', 'BEARUSDT', 'XLMUSDT', 'TRXUSDT', 'ICXUSDT']
    for j, k in ascendientes:
        dataset = client.get_klines(symbol=j, interval=interval, limit=20)
        data = pd.DataFrame(dataset, dtype=float)
        data.pop(1)
        data = data.iloc[:, :5]
        data = data.rename(
            columns={0: "FechaApertura", 2: 'ValorMaximo', 3: 'ValorMinimo', 4: 'Cierre', 5: 'Volumen'})
        columns = ['FechaApertura', 'ValorMaximo', 'ValorMinimo', 'Cierre', 'Volumen']
        data = data[columns]
        #a = len(data.index)

        #row = [fecha, maximo, minimo, cierre, volumen]
        # print(data.loc[len(data.index)])
        #data.loc[len(data.index)] = row
        data = pd.DataFrame(data, dtype=float)
        valorMaximo = data['ValorMaximo']
        valorMinimo = data['ValorMinimo']
        cierre = data['Cierre']
        volumen = data['Volumen']
        fecha = data['FechaApertura']
        a = len(data.index) - 1
        rsi = momentum.rsi(cierre, n=14, fillna=False)
        mfi = momentum.money_flow_index(valorMaximo, valorMinimo, cierre, volumen, n=14, fillna=True)
        boll_high = volatility.bollinger_hband(cierre, n=20, ndev=2, fillna=True)
        #boll_low = volatility.bollinger_lband(cierre, n=20, ndev=2, fillna=True)
        ganancia = abs(((cierre[a] * 100) / boll_high[a]) - 100)

        print(j, rsi[a-1], rsi[a], ganancia)
        print(j, mfi[a-1], mfi[a], ganancia)

        if 28 >= mfi[a] > mfi[a - 1] and ganancia > 0.5 and rsi[a-1] < rsi[a] < 40:
            markets.append(j)

    print(markets)
    if len(markets) != 0:
        market = random.choice(markets)

        print("Imprime el mercado elegido: " + market)

    #### VALIDAMOS LA TABLA PARA LA MONEDA SELECCIONADA

        return market
    else:
        print("No se han encontrado Mercados disponibles")
        return False
    #validTable(market)


    #### CREAMOS UNA INSTANCIA DE LA CLASE DE COMUNICACION CON EL WEBSOCKET


    """se hardcodea el mercado para volver a una tabla donde se quiere seguir"""


    #market = ['VETUSDT', 'MATICUSDT', 'XLMUSDT', 'BULLUSDT', 'BEARUSDT']
    #market = 'VETUSDT'
    #market = random.choice(market)
    print("Imprime el mercado elegido: " + market)
    #market = 'XLMUSDT'
    return market

    #return tableName




def main():
    cursor = bd.cursor()


    while True:
        cursor.execute("SELECT MAX(idTrade) FROM TB_TradesTest")  # + self.market)
        indice = cursor.fetchone()[0]
        print("El maximo Indice es de: " + str(indice))
        cursor.execute("SELECT BanderaCompra FROM TB_TradesTest  Where idTrade = ?", (indice,))
        # + self.market + " Where idTrade = ?", (self.indice, ))
        bandera_compra = cursor.fetchone()[0]
        print("El status de bandera compra es: " + str(bandera_compra))
        print("Iniciamos el intervalo dentro del main")
        intervalo = Client.KLINE_INTERVAL_5MINUTE
        while True:
            if bandera_compra == 1:
                cursor.execute("SELECT Mercado FROM TB_TradesTest Where idTrade = ? ", (indice,))
                market = cursor.fetchone()[0]
                print("El mercado seleccionado es: " + market)
            if bandera_compra != 1:
                print("Elegimos el mercado dentro del main")
                market = marketChoice(intervalo)
                time.sleep(2)
            if market is not False:
                print("EL mercado no es falso")
                break
            #validTable(market)
        #print("Comunicacion con binance websocket")
        #socket = comunication_binance.Socket(market, intervalo)
        #print("Ejecutamos la funcion wsocket()")
        #socket.wsocket()
        #print("Salimos de la ejecucion del wsocket()")


if __name__ == '__main__':
    main()
