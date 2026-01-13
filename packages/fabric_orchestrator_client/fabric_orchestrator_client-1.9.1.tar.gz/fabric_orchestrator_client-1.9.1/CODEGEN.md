# Generating the Client Code
Due to a BUG in swagger-code-gen, Please follow the steps below

That said, there's a bug in the Python generator of Swagger Codegen 3.x, it doesn't generate the code for Bearer authentication in OpenAPI 3.0 definitions. 
As a workaround, edit your OpenAPI YAML file and replace this part

```
  securitySchemes:
    bearerAuth:     
      type: http
      scheme: bearer
      bearerFormat: JWT  
```

to

```
  securitySchemes:
    sso_auth:
      type: apiKey
      in: header
      name: Authorization
```
Then generate a new Python client from the modified API definition.


Reference for more details [here](https://stackoverflow.com/questions/57920052/how-to-set-the-bearer-token-in-the-python-api-client-generated-by-swagger-codege)
