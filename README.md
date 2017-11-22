# REST Sample Code
Example code snippets for using Kooltra's RESTful API.

# Setup
- Make sure you have Python3, including pip3.
- If you don't, on Mac, do `brew install python3`, on Windows, go [here](https://www.python.org/downloads/)
- Make sure you have the `requests` library. If you don't, do `pip3 install requests`.
- Make sure you have a Connected App set up in your Salesforce org where you can obtain
clientID, client secret, etc.
- Create a `credentials.json` file according to the example file `credentials.json.example`
with your actual Salesforce credentials. Append your security token to your password in the
password field.

# Run
- *Please read the code and the values before you run them*
- Run `python3 accounts.py` to POST some accounts to your org. The account codes are currently
hard-coded to be of the form `EODxxx` and in an entity called 'MT4TEST'. If you need them to
be different, change them in the code.
- Run `python3 trades.py` to POST some trades to your org.
- Run `python3 mt4eod.py` to run the MT4 EOD process with the `EODx` accounts in your org.
The process will get the positions from the AccountsPositions API then issue the requests.
