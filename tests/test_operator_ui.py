"""Tests for operator UI backend."""

import pytest
import json
import base64
from datetime import datetime, timedelta
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from operator_ui.app import create_app, db
from operator_ui.models import Agent, ApprovalToken, AuditEvent


@pytest.fixture
def app():
    """Create test app."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def auth_headers():
    """Create basic auth headers."""
    credentials = base64.b64encode(b'admin:admin').decode()
    return {
        'Authorization': f'Basic {credentials}',
        'Content-Type': 'application/json'
    }


def test_app_creation(app):
    """Test app can be created."""
    assert app is not None
    assert app.config['TESTING'] is True


def test_health_endpoint(client):
    """Test public health endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'running'


def test_api_health_requires_auth(client):
    """Test API health endpoint requires authentication."""
    response = client.get('/api/health')
    assert response.status_code == 401


def test_api_health_with_auth(client, auth_headers):
    """Test API health endpoint with auth."""
    response = client.get('/api/health', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'operational'


def test_list_agents_empty(client, auth_headers):
    """Test listing agents when none exist."""
    response = client.get('/api/agents', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['agents'] == []


def test_list_agents_with_data(app, client, auth_headers):
    """Test listing agents with data."""
    with app.app_context():
        agent = Agent(
            id='agent-001',
            agent_type='scripted',
            status='active'
        )
        db.session.add(agent)
        db.session.commit()
    
    response = client.get('/api/agents', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['agents']) == 1
    assert data['agents'][0]['id'] == 'agent-001'


def test_get_agent_not_found(client, auth_headers):
    """Test getting non-existent agent."""
    response = client.get('/api/agents/nonexistent', headers=auth_headers)
    assert response.status_code == 404


def test_get_agent_found(app, client, auth_headers):
    """Test getting existing agent."""
    with app.app_context():
        agent = Agent(
            id='agent-001',
            agent_type='scripted',
            status='active'
        )
        db.session.add(agent)
        db.session.commit()
    
    response = client.get('/api/agents/agent-001', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == 'agent-001'
    assert data['agent_type'] == 'scripted'


def test_list_audit_empty(client, auth_headers):
    """Test listing audit events when none exist."""
    response = client.get('/api/audit', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['events'] == []


def test_list_audit_with_data(app, client, auth_headers):
    """Test listing audit events with data."""
    with app.app_context():
        event = AuditEvent(
            agent_id='agent-001',
            tool_name='capture_frame',
            status='success'
        )
        db.session.add(event)
        db.session.commit()
    
    response = client.get('/api/audit', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['events']) == 1
    assert data['events'][0]['tool_name'] == 'capture_frame'


def test_audit_filter_by_agent(app, client, auth_headers):
    """Test filtering audit events by agent."""
    with app.app_context():
        event1 = AuditEvent(agent_id='agent-001', tool_name='capture_frame', status='success')
        event2 = AuditEvent(agent_id='agent-002', tool_name='record_audio', status='success')
        db.session.add_all([event1, event2])
        db.session.commit()
    
    response = client.get('/api/audit?agent_id=agent-001', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['events']) == 1
    assert data['events'][0]['agent_id'] == 'agent-001'


def test_issue_approval_missing_fields(client, auth_headers):
    """Test issuing approval token with missing fields."""
    response = client.post(
        '/api/approve',
        headers=auth_headers,
        data=json.dumps({})
    )
    assert response.status_code == 400


def test_issue_approval_agent_not_found(client, auth_headers):
    """Test issuing approval token for non-existent agent."""
    response = client.post(
        '/api/approve',
        headers=auth_headers,
        data=json.dumps({
            'agent_id': 'nonexistent',
            'scope': 'camera'
        })
    )
    assert response.status_code == 404


def test_issue_approval_success(app, client, auth_headers):
    """Test successfully issuing approval token."""
    with app.app_context():
        agent = Agent(id='agent-001', agent_type='scripted', status='active')
        db.session.add(agent)
        db.session.commit()
    
    response = client.post(
        '/api/approve',
        headers=auth_headers,
        data=json.dumps({
            'agent_id': 'agent-001',
            'scope': 'camera',
            'ttl_seconds': 300
        })
    )
    assert response.status_code == 201
    data = response.get_json()
    assert 'token' in data
    assert data['scope'] == 'camera'
    assert 'expires_at' in data


def test_list_tokens(app, client, auth_headers):
    """Test listing approval tokens."""
    with app.app_context():
        agent = Agent(id='agent-001', agent_type='scripted', status='active')
        db.session.add(agent)
        db.session.flush()
        
        token_obj, token_str = ApprovalToken.generate(
            agent_id='agent-001',
            scope='camera',
            secret_key='test-secret'
        )
        db.session.add(token_obj)
        db.session.commit()
    
    response = client.get('/api/tokens/agent-001', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['tokens']) == 1
    assert data['tokens'][0]['scope'] == 'camera'


def test_revoke_token(app, client, auth_headers):
    """Test revoking an approval token."""
    with app.app_context():
        agent = Agent(id='agent-001', agent_type='scripted', status='active')
        db.session.add(agent)
        db.session.flush()
        
        token_obj, token_str = ApprovalToken.generate(
            agent_id='agent-001',
            scope='camera',
            secret_key='test-secret'
        )
        db.session.add(token_obj)
        db.session.commit()
        token_id = token_obj.id
    
    response = client.post(f'/api/tokens/{token_id}/revoke', headers=auth_headers)
    assert response.status_code == 200
    
    # Verify revoked
    with app.app_context():
        token = ApprovalToken.query.filter_by(id=token_id).first()
        assert token.revoked is True


def test_token_verify_valid(app):
    """Test token verification with valid token."""
    with app.app_context():
        agent = Agent(id='agent-001', agent_type='scripted', status='active')
        db.session.add(agent)
        db.session.flush()
        
        token_obj, token_str = ApprovalToken.generate(
            agent_id='agent-001',
            scope='camera',
            ttl_seconds=300,
            secret_key='test-secret'
        )
        db.session.add(token_obj)
        db.session.commit()
        
        verified_token, is_valid = ApprovalToken.verify(token_str, 'test-secret')
        assert is_valid is True
        assert verified_token is not None


def test_token_verify_expired(app):
    """Test token verification with expired token."""
    with app.app_context():
        agent = Agent(id='agent-001', agent_type='scripted', status='active')
        db.session.add(agent)
        db.session.flush()
        
        token_obj, token_str = ApprovalToken.generate(
            agent_id='agent-001',
            scope='camera',
            ttl_seconds=-1,  # Already expired
            secret_key='test-secret'
        )
        db.session.add(token_obj)
        db.session.commit()
        
        verified_token, is_valid = ApprovalToken.verify(token_str, 'test-secret')
        assert is_valid is False


def test_token_verify_wrong_signature(app):
    """Test token verification with wrong signature."""
    with app.app_context():
        agent = Agent(id='agent-001', agent_type='scripted', status='active')
        db.session.add(agent)
        db.session.flush()
        
        token_obj, token_str = ApprovalToken.generate(
            agent_id='agent-001',
            scope='camera',
            secret_key='test-secret'
        )
        db.session.add(token_obj)
        db.session.commit()
        
        verified_token, is_valid = ApprovalToken.verify(token_str, 'wrong-secret')
        assert is_valid is False


def test_audit_event_from_dict(app):
    """Test creating audit event from dict."""
    with app.app_context():
        event_dict = {
            'timestamp': datetime.utcnow().isoformat(),
            'agent_id': 'agent-001',
            'tool': 'capture_frame',
            'status': 'success',
            'details': {'frame_id': 'frame-123'}
        }
        
        event = AuditEvent.from_audit_event(event_dict)
        assert event.agent_id == 'agent-001'
        assert event.tool_name == 'capture_frame'
        assert event.status == 'success'


def test_agent_to_dict(app):
    """Test agent serialization."""
    with app.app_context():
        agent = Agent(
            id='agent-001',
            agent_type='scripted',
            status='active'
        )
        db.session.add(agent)
        db.session.commit()
        
        agent_dict = agent.to_dict()
        assert agent_dict['id'] == 'agent-001'
        assert agent_dict['agent_type'] == 'scripted'
        assert agent_dict['status'] == 'active'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
