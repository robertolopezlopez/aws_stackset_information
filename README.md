# PoC: gathering information about an AWS CloudFormation Stack-Set

In this proof of concept I am trying to find out the feasibility of finding detailed information about a CloudFormation Stack-Set.

## Overall requirements

* Check how long does it take to get the accounts, given a stack-set ID
    * list of accounts where the stack-set is deployed
    * performance metrics

## Chosen stack

* FastAPI with Uvicorn
    * Automatic OpenAPI support
    * Type annotations for validation and serialization
    * Live reload of code changes
    * `async` support
    * Small overhead and high performance

## Configuration

* `setup.conf`
    * Mandatory.
    * Modeled upon `setup.conf.example`.
    * There is just one parameter to set: `aws_region`.

## API

* `GET /ping`
* `GET /status`
    * Mandatory parameters:
        * `stack_set_id`
            * Type: UUID
            * CloudFormation Stack-Set ID
    * Optional parameters
        * `num_requests`
            * Type: integer
            * Default value: 1

We can fetch the API definition under `/api/v1/openapi.json`

```json
{
    "openapi": "3.1.0",
    "info": {
        "title": "FastAPI",
        "version": "0.1.0"
    },
    "servers": [
        {
            "url": "/api/v1"
        }
    ],
    "paths": {
        "/ping": {
            "get": {
                "tags": [
                    "ping",
                    "ping"
                ],
                "summary": "Ping",
                "operationId": "ping_ping_get",
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {
                            "application/json": {
                                "schema": {}
                            }
                        }
                    }
                }
            }
        },
        "/status": {
            "get": {
                "tags": [
                    "status",
                    "status"
                ],
                "summary": "Get Status",
                "operationId": "get_status_status_get",
                "parameters": [
                    {
                        "name": "stack_set_id",
                        "in": "query",
                        "required": true,
                        "schema": {
                            "type": "string",
                            "title": "Stack Set Id"
                        }
                    },
                    {
                        "name": "num_requests",
                        "in": "query",
                        "required": false,
                        "schema": {
                            "type": "integer",
                            "default": 1,
                            "title": "Num Requests"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "title": "Response Get Status Status Get"
                                }
                            }
                        }
                    },
                    "422": {
                        "description": "Validation Error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPValidationError"
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "components": {
        "schemas": {
            "HTTPValidationError": {
                "properties": {
                    "detail": {
                        "items": {
                            "$ref": "#/components/schemas/ValidationError"
                        },
                        "type": "array",
                        "title": "Detail"
                    }
                },
                "type": "object",
                "title": "HTTPValidationError"
            },
            "ValidationError": {
                "properties": {
                    "loc": {
                        "items": {
                            "anyOf": [
                                {
                                    "type": "string"
                                },
                                {
                                    "type": "integer"
                                }
                            ]
                        },
                        "type": "array",
                        "title": "Location"
                    },
                    "msg": {
                        "type": "string",
                        "title": "Message"
                    },
                    "type": {
                        "type": "string",
                        "title": "Error Type"
                    }
                },
                "type": "object",
                "required": [
                    "loc",
                    "msg",
                    "type"
                ],
                "title": "ValidationError"
            }
        }
    }
}
```

## Serve

```shell
~ $ uvicorn app:app --reload
```
