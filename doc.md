*glizer webhook*

- on transaction status changed
url:
[POST] https://api.glizer.app/webhooks/bot

header:
token:string

body:
event:"ON_TRANSACTION_STATUS_CHANGED"
transactionsId:string
status:success|error|pending

notes:
url, token: must be changeable in bot .env file

**token here if for glizer access**


************************************************************************

*bot api*

notes:
token, port: must be changeable in bot .env file

**token here if for bot access**


- create transaction
url:
[POST] http://localhost:PORT/transaction/create

header:
token:string

body:
[pubg load]
itemType:diamonds|golds
amount:number
pinCode:string
playerId:string

[PUBG]
loginEmail:string
loginPassword:string
amount:number
pinCode:string
playerId:string



response:
transactionsId:string
//on error: [PUBG - case of loginEmail is blocked]
error:"LOGIN_EMAIL_BLOCKED"


- get transaction status
url:
[GET] http://localhost:PORT/transaction/:transactionId

params in url:
transactionId:string

header:
token:string

response:
status:success|error|pending