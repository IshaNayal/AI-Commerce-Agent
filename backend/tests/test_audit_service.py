from uuid import uuid4

from backend.app.schemas.merchant import MerchantCreate
from backend.app.services.merchant_services import MerchantService
from backend.app.services.audit_service import AuditService


def test_create_audit_log(db):
    merchant = MerchantService(db).create(
        MerchantCreate(name="Audit Test", slug="audit-test", email="audit@test.com")
    )
    service = AuditService(db)
    
    log = service.log_action(
        action="TEST_ACTION",
        merchant_id=merchant.id,
        entity_type="TEST_ENTITY",
        entity_id=uuid4(),
        details={"key": "value"}
    )
    
    assert log.id is not None
    assert log.action == "TEST_ACTION"
    assert log.details == {"key": "value"}
    assert log.merchant_id == merchant.id


def test_list_audit_logs(db):
    merchant = MerchantService(db).create(
        MerchantCreate(name="Audit Test 2", slug="audit-test-2", email="audit2@test.com")
    )
    service = AuditService(db)
    
    service.log_action(action="ACTION_1", merchant_id=merchant.id)
    service.log_action(action="ACTION_2", merchant_id=merchant.id)
    
    logs = service.list_by_merchant(merchant.id)
    assert len(logs) == 2
    assert logs[0].action == "ACTION_2" # latest first
    assert logs[1].action == "ACTION_1"
