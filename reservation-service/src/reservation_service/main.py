from fastapi import FastAPI

# Category
from reservation_service.adapters.category.category_controller import create_category_controller
from reservation_service.application.category.use_case import CategoryUseCase
from reservation_service.infrastructure.category.category_repository_impl import CategoryRepositoryImpl

# Reservation
from reservation_service.adapters.reservation.reservation_controller import create_reservation_controller
from reservation_service.application.reservation.use_case import ReservationUseCase
from reservation_service.infrastructure.reservation.reservation_repositoryImpl import ReservationRepositoryImpl
from reservation_service.domain.reservation.reservation_service import ReservationService


app = FastAPI(
    title="gestion_microservice",
    version="0.1.0",
)

#  Healthcheck (important pour Docker)
def build_status() -> dict[str, str]:
    return {"status": "reservation-service"}


@app.get("/")
def root() -> dict[str, str]:
    return build_status()


#  Wiring (hexagonal)
category_repository = CategoryRepositoryImpl()
category_use_case = CategoryUseCase(category_repository)

reservation_repository = ReservationRepositoryImpl()
reservation_service = ReservationService(reservation_repository)

#  IMPORTANT → injecter category_repository aussi
reservation_use_case = ReservationUseCase(
    reservation_service,
    category_repository
)

#  Routes
app.include_router(create_category_controller(category_use_case))
app.include_router(create_reservation_controller(reservation_use_case))