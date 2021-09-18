Problems

* DB
  * there can't be a user and a db with the same name (seems to me so)
  * so I've changed username to speggu
  * import wants to write to db test (why?!)
* API
  * cant connect to another db than hardcoded spegg
* Vue resolves API at http://localhost:8080/api/v1/Subject instead of API-Host
* do we need Traeffik?

to test the API

``` shell

make api-proxy
curl -v http://localhost:8080/api/v1/info
curl -v http://localhost:8080/api/v1/Subject
curl -v http://localhost:8080/api/v1/Resource
```
