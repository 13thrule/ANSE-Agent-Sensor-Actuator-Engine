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


def test_audit_timeline_empty(client, auth_headers):
    """Test audit timeline endpoint when no events exist."""
    response = client.get('/api/audit/timeline', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['timeline'] == []
    assert data['count'] == 0


def test_audit_timeline_with_events(app, client, auth_headers):
    """Test audit timeline endpoint with events."""
    with app.app_context():
        # Create audit events
        event1 = AuditEvent(
            timestamp=datetime.utcnow(),
            agent_id='agent-001',
            tool_name='capture_frame',
            status='success',
            severity='low',
            input_args='{"width": 640, "height": 480}',
            output='{"frame_id": "frame-1"}'
        )
        event2 = AuditEvent(
            timestamp=datetime.utcnow(),
            agent_id='agent-002',
            tool_name='record_audio',
            status='failure',
            severity='medium',
            input_args='{"duration": 5}',
            output='{"error": "no device"}'
        )
        db.session.add(event1)
        db.session.add(event2)
        db.session.commit()
    
    response = client.get('/api/audit/timeline?limit=10', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['count'] == 2
    assert data['timeline'][0]['agent_id'] == 'agent-001'
    assert data['timeline'][0]['tool'] == 'capture_frame'


def test_audit_timeline_filter_by_agent(app, client, auth_headers):
    """Test audit timeline filtering by agent."""
    with app.app_context():
        event1 = AuditEvent(
            timestamp=datetime.utcnow(),
            agent_id='agent-001',
            tool_name='capture_frame',
            status='success',
            severity='low',
            input_args='{}',
            output='{}'
        )
        event2 = AuditEvent(
            timestamp=datetime.utcnow(),
            agent_id='agent-002',
            tool_name='record_audio',
            status='success',
            severity='low',
            input_args='{}',
            output='{}'
        )
        db.session.add(event1)
        db.session.add(event2)
        db.session.commit()
    
    response = client.get('/api/audit/timeline?agent_id=agent-001', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['count'] == 1
    assert data['timeline'][0]['agent_id'] == 'agent-001'


def test_audit_timeline_filter_by_tool(app, client, auth_headers):
    """Test audit timeline filtering by tool."""
    with app.app_context():
        event1 = AuditEvent(
            timestamp=datetime.utcnow(),
            agent_id='agent-001',
            tool_name='capture_frame',
            status='success',
            severity='low',
            input_args='{}',
            output='{}'
        )
        event2 = AuditEvent(
            timestamp=datetime.utcnow(),
            agent_id='agent-001',
            tool_name='record_audio',
            status='success',
            severity='low',
            input_args='{}',
            output='{}'
        )
        db.session.add(event1)
        db.session.add(event2)
        db.session.commit()
    
    response = client.get('/api/audit/timeline?tool=capture_frame', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['count'] == 1
    assert data['timeline'][0]['tool'] == 'capture_frame'


def test_get_audit_event(app, client, auth_headers):
    """Test getting a specific audit event."""
    with app.app_context():
        event = AuditEvent(
            timestamp=datetime.utcnow(),
            agent_id='agent-001',
            tool_name='capture_frame',
            status='success',
            severity='low',
            input_args='{"width": 640}',
            output='{"frame_id": "f1"}'
        )
        db.session.add(event)
        db.session.commit()
        event_id = event.id
    
    response = client.get(f'/api/audit/{event_id}', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['agent_id'] == 'agent-001'
    assert data['tool_name'] == 'capture_frame'


def test_get_audit_event_not_found(client, auth_headers):
    """Test getting non-existent event."""
    response = client.get('/api/audit/999', headers=auth_headers)
    assert response.status_code == 404


def test_replay_audit_event(app, client, auth_headers):
    """Test replaying an audit event."""
    with app.app_context():
        event = AuditEvent(
            timestamp=datetime.utcnow(),
            agent_id='agent-001',
            tool_name='capture_frame',
            status='success',
            severity='low',
            input_args='{}',
            output='{}'
        )
        db.session.add(event)
        db.session.commit()
        event_id = event.id
    
    response = client.post(f'/api/audit/replay/{event_id}', 
                          headers=auth_headers,
                          json={})
    assert response.status_code == 200
    data = response.get_json()
    assert data['event_id'] == event_id
    assert data['tool'] == 'capture_frame'
    assert data['replay_mode'] == 'simulated'
    assert data['status'] == 'success'


def test_replay_audit_event_not_found(client, auth_headers):
    """Test replaying non-existent event."""
    response = client.post('/api/audit/replay/999',
                          headers=auth_headers,
                          json={})
    assert response.status_code == 404


def test_audit_stats(app, client, auth_headers):
    """Test audit statistics endpoint."""
    with app.app_context():
        # Create various events
        event1 = AuditEvent(
            timestamp=datetime.utcnow(),
            agent_id='agent-001',
            tool_name='capture_frame',
            status='success',
            severity='low',
            input_args='{}',
            output='{}'
        )
        event2 = AuditEvent(
            timestamp=datetime.utcnow(),
            agent_id='agent-001',
            tool_name='record_audio',
            status='success',
            severity='low',
            input_args='{}',
            output='{}'
        )
        event3 = AuditEvent(
            timestamp=datetime.utcnow(),
            agent_id='agent-002',
            tool_name='capture_frame',
            status='failure',
            severity='high',
            input_args='{}',
            output='{}'
        )
        db.session.add_all([event1, event2, event3])
        db.session.commit()
    
    response = client.get('/api/audit/stats', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['total_events'] == 3
    assert data['successful_events'] == 2
    assert data['failed_events'] == 1
    assert data['success_rate'] == pytest.approx(66.66, abs=0.1)
    assert len(data['tool_usage']) > 0
    assert len(data['agent_activity']) > 0


def test_export_audit_trail_json(app, client, auth_headers):
    """Test exporting audit trail as JSON."""
    with app.app_context():
        event = AuditEvent(
            timestamp=datetime.utcnow(),
            agent_id='agent-001',
            tool_name='capture_frame',
            status='success',
            severity='low',
            input_args='{}',
            output='{}'
        )
        db.session.add(event)
        db.session.commit()
    
    response = client.get('/api/audit/export?format=json', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'export_timestamp' in data
    assert 'event_count' in data
    assert data['event_count'] == 1
    assert 'events' in data


def test_export_audit_trail_filtered(app, client, auth_headers):
    """Test exporting audit trail filtered by agent."""
    with app.app_context():
        event1 = AuditEvent(
            timestamp=datetime.utcnow(),
            agent_id='agent-001',
            tool_name='capture_frame',
            status='success',
            severity='low',
            input_args='{}',
            output='{}'
        )
        event2 = AuditEvent(
            timestamp=datetime.utcnow(),
            agent_id='agent-002',
            tool_name='record_audio',
            status='success',
            severity='low',
            input_args='{}',
            output='{}'
        )
        db.session.add_all([event1, event2])
        db.session.commit()
    
    response = client.get('/api/audit/export?format=json&agent_id=agent-001', 
                         headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['event_count'] == 1
    assert data['events'][0]['agent_id'] == 'agent-001'


def test_export_audit_trail_unsupported_format(client, auth_headers):
    """Test exporting with unsupported format."""
    response = client.get('/api/audit/export?format=pdf', headers=auth_headers)
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data


