# rai_lotto

This is a demonstration of how you can use the YapRai API ([https://yapraiwallet.space]) to build a simple web service - in this case an hourly lottery.
The code is tested but a little rough around the edges.

The lottery uses a single raiblocks (XRB) address which the contestent sends 1XRB to, every hour the server collects the new transaction history, identifies
the contestent addresses (each transaction is an entry) and then randomly selects one address and sends the whole lottery fund to that address. Data is stored
in a tinyDB database for record keeping.

To setup you'll need to be running python3 and flask, you can get a YapRai API id_key by contact us on the raiblocks slack on #yaprai_api (you will also need
a YapRai wallet account). Move settings.py.example to settings.py and fill in the id_key and the fund address you are going to use.

The lottery code is free to use and could be made alot more efficient and also graphically look a lot better... 
