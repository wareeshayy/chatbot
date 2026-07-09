"""FAQ management service."""

from uuid import UUID

from app.database.repositories.misc_repo import FAQRepository
from app.models.faq import FAQ
from app.models.user import User
from app.schemas.faq import FAQCreateRequest, FAQUpdateRequest
from app.utils.exceptions import NotFoundError
from app.utils.pagination import ServicePage


class FAQService:
    def __init__(self) -> None:
        self.faq_repo = FAQRepository()

    async def list_faqs(
        self,
        page: int = 1,
        page_size: int = 50,
        category: str | None = None,
        published_only: bool = True,
    ) -> ServicePage[FAQ]:
        offset = (page - 1) * page_size
        faqs, total = await self.faq_repo.list_faqs(offset, page_size, category, published_only)
        return ServicePage.create(faqs, total, page, page_size)

    async def get_faq(self, faq_id: UUID, published_only: bool = False) -> FAQ:
        faq = await self.faq_repo.get_by_id(faq_id)
        if not faq or (published_only and not faq.is_published):
            raise NotFoundError("FAQ", faq_id)
        return faq

    async def create_faq(self, data: FAQCreateRequest, admin: User) -> FAQ:
        faq = FAQ(**data.model_dump(), created_by=admin.id)
        return await self.faq_repo.create(faq)

    async def update_faq(self, faq_id: UUID, data: FAQUpdateRequest) -> FAQ:
        faq = await self.get_faq(faq_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(faq, field, value)
        await faq.save()
        return faq

    async def delete_faq(self, faq_id: UUID) -> None:
        faq = await self.get_faq(faq_id)
        await self.faq_repo.delete(faq)
