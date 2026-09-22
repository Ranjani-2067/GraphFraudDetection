// Review-2 demonstration queries. All values are examples and can be replaced with parameters.
MATCH (a:Account)-[:SENT]->(t:Transaction)-[:RECEIVED_BY]->(b:Account)
RETURN a.account_id AS sender, b.account_id AS receiver, t.txn_id, t.amount, t.timestamp
ORDER BY t.timestamp DESC LIMIT 20;

MATCH (a:Account)-[:USED_DEVICE]->(d:Device)<-[:USED_DEVICE]-(b:Account)
WHERE a.account_id < b.account_id
RETURN a.account_id, b.account_id, d.device_id;

MATCH p=(a:Account {account_id:'ACC00001'})-[:SENT|RECEIVED_BY*1..8]->(b:Account)
WHERE a<>b
RETURN [n IN nodes(p) WHERE n:Account | n.account_id] AS account_chain, length(p) AS hops
ORDER BY hops LIMIT 20;
