#!/usr/bin/python3


import json
import os
import pymysql
import requests
import sys


#
# prod:
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# OTRS URL
OTRS_URL = os.getenv("OTRS_URL")

# MySQL settings
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASS = os.getenv("MYSQL_PASS")
MYSQL_DB   = os.getenv("MYSQL_DB")

#if len(sys.argv) < 3:
#    print("too less arguments")
#    sys.exit (1)

conn = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, passwd=MYSQL_PASS, db=MYSQL_DB)
cur = conn.cursor()
sql = "SELECT ticket.id, ticket.tn, ticket.title, CASE WHEN customer_company.name IS NOT NULL THEN customer_company.name ELSE ticket.customer_id END AS customer FROM ticket LEFT JOIN customer_company ON (ticket.customer_id = customer_company.customer_id) WHERE tn = %s"
cur.execute(sql, sys.argv[1])

#print(cur.description)
#print()

if cur.rowcount:
    for row in cur:
      #print(row)
      id = str(row[0])
      tn = row[1]
      title = row[2]
      customer = row[3]
else:
    # exit if no matching ticket was found
    cur.close()
    conn.close()
    sys.exit (0)

cur.close()
conn.close()
ticket = '新工单！  #' + tn + '\n来自' + customer + '：' + title + '\n' + OTRS_URL + id
s = ticket
headers = {"Content-type": "application/json"}
payload = {
    "msgtype": 'text',
    "text": {
        "content": s,
    }
}

print(payload)
r = requests.post(WEBHOOK_URL, json=payload, headers=headers)

if r.status_code != 200:
    raise ValueError('Request to slack returned an error %s, the response is:\n%s' % (r.status_code, r.text))
