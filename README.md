# IMart Event Worker

## Pattern

```

        List event Worker                 +-----------------------+                 Buy event worker
 +-------------------------------+        |                       |        +-------------------------------+
 |     +-------------------+     |        |  xxx event worker     |        |    +---------------------+    |
 |     |                   |     |        |                       |        |    |                     |    |
 |     |     Subject       |     |        |                       |        |    |     Subject         |    |
 |     |                   |     |        +-----------------------+        |    |                     |    |
 |     +-----|------^------+     |                                         |    +------|------^-------+    |
 |           |      |            |                                         |           |      |            |
 |           |      |            |      +--------------------------+       |           |      |            |
 (list events    (excuted seq no)|      |  +--------------------+  |       (buy events |      |            |
  / seq no)  |      |            |      |  |    xxx State       |  |       |  / seq no)|   (excuted seq no)|
 |           |      |            |      |  |                    |  |       |           |      |            |
 |  +--------v------|--------+   |      |  |   Offer/Sale ...   |  |       |           |      |            |
 |  |                        |   |      |  |                    |  |       |  +--------v------|--------+   |
 |  |       Observer         |   |      |  | record seq no      |  |       |  |       Observer         |   |
 |  |                        |   |      |  |                    |  |       |  |                        |   |
 |  |                        |   |      |  +--------------------+  |       |  |                        |   |
 |  |   +----------------+   |   |      |  +--------------------+  |       |  |    +---------------+   |   |
 |  |   |  Order List    ---------------|-->    Order state     <--|----------|----| Order buy     |   |   |
 |  |   |                |-\ |   |      |  |                    |  |       |  |    |               |   |   |
 |  |   +----------------+  -\   |      |  | record seq no      |  |       |  |  /-+---------------+   |   |
 |  +------------------------+--\|      |  +--------------------+  |       | /-------------------------+   |
 +--------------------------------\     |                          |      /--------------------------------+
                                   -\   |                          |   /--
                                     --\|                          |---
                                        |\                      /--|
                                        | ->------------------<-+  |
                                        |  |                    |  |
                                        |  |    Activities      |  |
                                        |  |                    |  |
                                        |  | record seq no      |  |
                                        |  |                    |  |
                                        |  +--------------------+  |
                                        +--------------------------+
                                                 DB / Cache
```

## Collection ????????????

??????????????? prisma???????????? .env, ?????????

```
// .env
DB_URL="mysql://root:root@localhost:3306/imart"
```

```python
$ prisma db push
$ prisma generate

$ python3 -m bin.collection_data_gathering --account 0x1af632aeaa009748aa14c2271f8f9687d8cee0d91e4957e5cc575c856717bfde --node https://fullnode.testnet.aptoslabs.com/v1
```

## ??????

```
// build
docker build -t imart-event-worker:v1 -f ./Dockerfile .

// run
docker run -d -v $PWD:/app/event-worker imart-event-worker:v1
```

## ??????

```
tail -n 10 error.log
```
