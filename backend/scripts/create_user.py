import asyncio
import sys

sys.path.append(".")  # so `app` is importable when running this script directly

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole


async def create_user(email: str, password: str, role: UserRole) -> None:
    async with AsyncSessionLocal() as session:
        user = User(
            email=email,
            hashed_password=hash_password(password),
            role=role,
        )
        session.add(user)
        await session.commit()
        print(f"Created user: {user.email} ({user.role.value}) — id={user.id}")


if __name__ == "__main__":
    asyncio.run(create_user("admin@example.com", "changeme123", UserRole.ADMIN))