import pytest
import json
from unittest.mock import patch, MagicMock


class TestHealthCheck:
    """Test health check endpoint"""

    def test_health_check_success(self, client):
        """Test successful health check"""
        response = client.get('/')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert data['version'] == '1.0.0'
        assert data['database'] == 'connected'

    @patch('app.get_db_connection')
    def test_health_check_db_failure(self, mock_get_db, client):
        """Test health check when database connection fails"""
        mock_get_db.side_effect = Exception("Database connection failed")

        response = client.get('/')
        assert response.status_code == 500

        data = json.loads(response.data)
        assert data['status'] == 'unhealthy'
        assert 'error' in data


class TestGetUsers:
    """Test GET /api/users endpoint"""

    @patch('app.get_db_connection')
    def test_get_users_success(self, mock_get_db, client):
        """Test successful retrieval of users"""
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock user data
        mock_users = [
            {
                'id': 1,
                'name': 'John Doe',
                'email': 'john@example.com',
                'age': 30,
                'created_at': MagicMock(),
                'updated_at': MagicMock()
            },
            {
                'id': 2,
                'name': 'Jane Smith',
                'email': 'jane@example.com',
                'age': 25,
                'created_at': MagicMock(),
                'updated_at': MagicMock()
            }
        ]

        # Configure mock cursor
        mock_cursor.fetchall.return_value = mock_users
        mock_users[0]['created_at'].isoformat.return_value = '2023-01-01T00:00:00'
        mock_users[0]['updated_at'].isoformat.return_value = '2023-01-01T00:00:00'
        mock_users[1]['created_at'].isoformat.return_value = '2023-01-02T00:00:00'
        mock_users[1]['updated_at'].isoformat.return_value = '2023-01-02T00:00:00'

        response = client.get('/api/users')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) == 2
        assert data['count'] == 2
        assert data['data'][0]['name'] == 'John Doe'
        assert data['data'][1]['name'] == 'Jane Smith'

    @patch('app.get_db_connection')
    def test_get_users_db_error(self, mock_get_db, client):
        """Test get users when database error occurs"""
        mock_get_db.side_effect = Exception("Database error")

        response = client.get('/api/users')
        assert response.status_code == 500

        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data


class TestCreateUser:
    """Test POST /api/users endpoint"""

    def test_create_user_success(self, client, sample_user_data):
        """Test successful user creation"""
        with patch('app.get_db_connection') as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_get_db.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            # Mock no existing user with email
            mock_cursor.fetchone.return_value = None

            # Mock user creation
            mock_user = (1, 'Test User', 'test@example.com', 25,
                        MagicMock(), MagicMock())
            mock_cursor.fetchone.return_value = mock_user
            mock_user[4].isoformat.return_value = '2023-01-01T00:00:00'
            mock_user[5].isoformat.return_value = '2023-01-01T00:00:00'

            response = client.post('/api/users',
                                 data=json.dumps(sample_user_data),
                                 content_type='application/json')

            assert response.status_code == 201

            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['name'] == 'Test User'
            assert data['data']['email'] == 'test@example.com'
            assert data['data']['age'] == 25

    def test_create_user_missing_data(self, client):
        """Test user creation with missing data"""
        response = client.post('/api/users',
                             data=json.dumps({}),
                             content_type='application/json')

        assert response.status_code == 400

        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data

    def test_create_user_invalid_email(self, client):
        """Test user creation with invalid email"""
        invalid_data = {
            'name': 'Test User',
            'email': 'invalid-email',
            'age': 25
        }

        response = client.post('/api/users',
                             data=json.dumps(invalid_data),
                             content_type='application/json')

        assert response.status_code == 400

        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data

    def test_create_user_duplicate_email(self, client, sample_user_data):
        """Test user creation with duplicate email"""
        with patch('app.get_db_connection') as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_get_db.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            # Mock existing user with same email
            mock_cursor.fetchone.return_value = (1,)

            response = client.post('/api/users',
                                 data=json.dumps(sample_user_data),
                                 content_type='application/json')

            assert response.status_code == 409

            data = json.loads(response.data)
            assert data['success'] is False
            assert 'Email already exists' in data['error']

    def test_create_user_empty_name(self, client):
        """Test user creation with empty name"""
        invalid_data = {
            'name': '',
            'email': 'test@example.com',
            'age': 25
        }

        response = client.post('/api/users',
                             data=json.dumps(invalid_data),
                             content_type='application/json')

        assert response.status_code == 400

        data = json.loads(response.data)
        assert data['success'] is False
        assert 'name' in data.get('field', '')

    def test_create_user_invalid_age(self, client):
        """Test user creation with invalid age"""
        invalid_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'age': 'not-a-number'
        }

        response = client.post('/api/users',
                             data=json.dumps(invalid_data),
                             content_type='application/json')

        assert response.status_code == 400

        data = json.loads(response.data)
        assert data['success'] is False
        assert 'age' in data.get('field', '')


class TestErrorHandlers:
    """Test error handlers"""

    def test_404_error(self, client):
        """Test 404 error handler"""
        response = client.get('/nonexistent-endpoint')
        assert response.status_code == 404

        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error'] == 'Endpoint not found'

    def test_405_error(self, client):
        """Test 405 error handler"""
        response = client.post('/')  # GET only endpoint
        assert response.status_code == 405

        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error'] == 'Method not allowed'


class TestValidation:
    """Test input validation"""

    def test_validate_required_success(self):
        """Test successful required validation"""
        from utils.validation import validate_required

        result = validate_required("test", "test_field")
        assert result == "test"

    def test_validate_required_failure(self):
        """Test required validation failure"""
        from utils.validation import validate_required, ValidationError

        with pytest.raises(ValidationError) as exc_info:
            validate_required(None, "test_field")

        assert "test_field is required" in str(exc_info.value)

    def test_validate_email_success(self):
        """Test successful email validation"""
        from utils.validation import validate_email

        result = validate_email("test@example.com", "email")
        assert result == "test@example.com"

    def test_validate_email_failure(self):
        """Test email validation failure"""
        from utils.validation import validate_email, ValidationError

        with pytest.raises(ValidationError) as exc_info:
            validate_email("invalid-email", "email")

        assert "Invalid email format" in str(exc_info.value)

    def test_validate_string_length_success(self):
        """Test successful string length validation"""
        from utils.validation import validate_string_length

        result = validate_string_length("test", min_length=2, max_length=10, field_name="test")
        assert result == "test"

    def test_validate_string_length_min_failure(self):
        """Test string length validation minimum failure"""
        from utils.validation import validate_string_length, ValidationError

        with pytest.raises(ValidationError) as exc_info:
            validate_string_length("a", min_length=2, field_name="test")

        assert "must be at least 2 characters" in str(exc_info.value)

    def test_validate_string_length_max_failure(self):
        """Test string length validation maximum failure"""
        from utils.validation import validate_string_length, ValidationError

        with pytest.raises(ValidationError) as exc_info:
            validate_string_length("thisisaverylongstring", max_length=10, field_name="test")

        assert "must be at most 10 characters" in str(exc_info.value)


if __name__ == '__main__':
    pytest.main([__file__])