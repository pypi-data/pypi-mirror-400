"""
Authentication Key Message Schema
"""
from .rpc_fields import rpc_fields

AuthKey = {
	"type": "object",
	"allOf": [
		{"$ref": "#/definitions/rpc_fields"},
	],
	"properties": {
		"key": {"type": "string"},
		"token": {"type": "boolean"}
	},
    "unevaluatedProperties": False,
    "definitions": {
        "rpc_fields": rpc_fields
    },
  	"required": ["key"]
}
