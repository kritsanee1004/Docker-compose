# Docker-compose

### Build  a micro-service :

```sh
$ docker-compose build
```

### Lunch service :

```sh
$ docker-compose up -d

```
### Start service
```sh
$ docker exec -it insert-mongodb1 bash

mongo insert-mongodb1:27041

> cfg={
{
	"_id" : "RS",
	"members" : [
		{
			"_id" : 0,
			"host" : "insert-mongodb1:27041"
		},
		{
			"_id" : 1,
			"host" : "query-mongodb2:27041"
		},
		{
			"_id" : 2,
			"host" : "query-mongodb3:27041"
		}
	]
}
> rs.initiate(cfg);
{ "ok" : 1 }
RS:SECONDARY> rs.status()


```
### Stop service :

```sh
$ docker-compose down
```


