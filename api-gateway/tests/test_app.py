def test_app_creation(app):
    assert app is not None
    assert app.config["TESTING"] == True


def test_models_import():
    from models import (
        AgentIPAddress,
        FailedAttempt,
        IPAddressLoginAttempt,
        Session,
        TokenBlacklist,
        Verification,
    )

    assert Verification is not None
    assert TokenBlacklist is not None
    assert Session is not None
    assert FailedAttempt is not None
    assert AgentIPAddress is not None
    assert IPAddressLoginAttempt is not None
