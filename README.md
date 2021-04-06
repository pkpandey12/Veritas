# Veritas

## Instructions to run app

1. Start ganache, take note of the port (by default 7545):
   * In `./Server/Blockchain`, run truffle deploy and note of the deployed contract hash.

2. Start the server application:
   1. `cd ./Server`
   2. `pipenv shell`
   3. `pipenv install`
   4. `./manage.py runserver`

3. Expose endpoint using ngrok ( install at <https://dashboard.ngrok.com/get-started/setup> ):
   1. Make sure you're in the folder where you installed ngrok and the file `./ngrok` is present
   2. `./ngrok htpp 8000`
   3. Note the link you get here and paste it in `App.js` in `./Client` in the `ngroklink` field

4. Run the expo app on Lan.
