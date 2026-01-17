from fastapi import APIRouter
from api.v1 import endpoints, feature_flags


router = APIRouter(prefix="/api/v1", tags=["v1"])

router.include_router(endpoints.router)
router.include_router(feature_flags.router)
