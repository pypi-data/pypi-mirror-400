import pytest
from unittest.mock import patch, MagicMock
import json
import os
from deala.deala_io import deala_io  # Importiere die Klasse

class TestDealaIO:
    def setup_method(self):
        self.deala = deala_io()

    def test_create_db_existing_database(self):
        # Test, wenn DB schon existiert (Name in bw.databases)
        with patch('brightway2.databases', ['existing_db']), patch('builtins.print') as mock_print:
            result = self.deala.create_DB('existing_db')
            assert result is None
            mock_print.assert_called_once_with('existing_db is already included')

    def test_create_db_new_database(self):
        # Test, wenn DB nicht existiert -> soll erstellt werden
        with patch('brightway2.databases', []), patch('brightway2.Database') as MockDatabase:
            mock_db_instance = MagicMock()
            MockDatabase.return_value = mock_db_instance

            result = self.deala.create_DB('new_db')

            MockDatabase.assert_called_with('new_db')
            mock_db_instance.register.assert_called_once()
            assert result == mock_db_instance

