import pytest
from accounts.models import user_Data

@pytest.mark.django_db
def test_create_user():
    user = user_Data.objects.create_user(
        username="John Michel",
        email="john@e273.com",
        password="securepass123",
        Phone="9565842659"
    )
    assert user.username == "John Michel"
    assert user.Email == "john@e273.com"
    assert user.check_password("securepass123")
    assert user.is_active is True
