from typing import override
from uuid import uuid4

from src.types.user import User, UserId
from src.types.user_provider import UserNotFoundError, UserProvider

my_user_id = UserId(uuid4())
me = User(id=my_user_id, given_name="Randall Kleiser", timezone="America/New_York")

adams_user_id = UserId(uuid4())
adams_user = User(id=adams_user_id, given_name="Adam Smork", timezone="America/New_York")

sallys_user_id = UserId(uuid4())
sallys_user = User(id=sallys_user_id, given_name="Sally Li", timezone="America/Los_Angeles")

pauls_user_id = UserId(uuid4())
pauls_user = User(id=pauls_user_id, given_name="Paul Smith", timezone="America/New_York")

mock_users = {
    my_user_id: me,
    adams_user_id: adams_user,
    sallys_user_id: sallys_user,
    pauls_user_id: pauls_user,
}

print("Using mock users:")
for user_id, user in mock_users.items():
    print(f"- {user.given_name} ({user_id})")
print()


class MockUserProvider(UserProvider):
    @override
    def get_user(self, user_id: UserId) -> User:
        user = mock_users[user_id]
        if user is None:  # type: ignore[unreachable]
            raise UserNotFoundError(user_id)
        return user
