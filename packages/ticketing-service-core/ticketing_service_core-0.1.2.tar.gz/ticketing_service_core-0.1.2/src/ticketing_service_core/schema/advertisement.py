"""
Advertisement Schema
"""
Advertisement = {
	"type": "object",
	"properties": {
		"host": {"type": "string"},
		"event": {"type": "string"},
		"name": {"type": "string"},
		"description": {"type": "string"},
		"status": {"type": "string"}
	},
    "unevaluatedProperties": True
}
