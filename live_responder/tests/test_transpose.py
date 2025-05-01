import unittest
from unittest.mock import MagicMock
from live_responder.transpose import transpose_to_sandbox
from live_responder.config import EmbeddingConfig

class TestTranspose(unittest.TestCase):

	def test_transpose_to_sandbox(self):
		mock_config = MagicMock(spec=EmbeddingConfig)
		mock_config.transpose_sql_schema_token = "ai_sandbox"
		
		input_statement = "SELECT * FROM ai_sandbox.users WHERE id = 1; SELECT other_col FROM other_schema.orders; SELECT name FROM ai_sandbox.products;"
		expected_output = "SELECT * FROM ai_sandbox.users([[user_id]]) WHERE id = 1; SELECT other_col FROM other_schema.orders; SELECT name FROM ai_sandbox.products([[user_id]]);"

		actual_output = transpose_to_sandbox(mock_config, input_statement)
		self.assertEqual(actual_output, expected_output)

if __name__ == '__main__':
	unittest.main() 