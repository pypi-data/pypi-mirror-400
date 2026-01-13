"""
Empty Message Schema
"""
from .rpc_fields import rpc_fields

Empty = {
	"type": "object",
	"allOf": [
		{"$ref": "#/definitions/rpc_fields"}
	],
    "unevaluatedProperties": False,
    "definitions": {
        "rpc_fields": rpc_fields
    }
}
