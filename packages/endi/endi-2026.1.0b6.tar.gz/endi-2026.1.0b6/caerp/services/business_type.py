from typing import List

from sqlalchemy import select

from caerp.models.project.types import BusinessType
from caerp.services.project.types import base_project_type_allowed


def get_active_business_type_ids(request) -> List[BusinessType]:
    return [
        btype
        for btype in request.dbsession.execute(
            select(BusinessType).where(BusinessType.active.is_(True))
        )
        .scalars()
        .all()
        if base_project_type_allowed(request, btype)
    ]
