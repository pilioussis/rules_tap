curl
	-X POST "http://localhost:8003/context" 
	-H "Content-Type: application/json"
	-d '{"query": "What answers can a user see?", "k": 3}'