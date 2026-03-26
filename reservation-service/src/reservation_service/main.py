# main.py
from fastapi import FastAPI
from reservation_service.adapters.category.category_controller import create_category_controller
from reservation_service.application.category.use_case import CategoryUseCase
from reservation_service.infrastructure.category.category_repository_impl import CategoryRepositoryImpl
from reservation_service.adapters.reservation.reservation_controller import create_reservation_controller
from reservation_service.application.reservation.use_case import ReservationUseCase
from reservation_service.infrastructure.reservation.reservation_repositoryImpl import ReservationRepositoryImpl
from reservation_service.domain.reservation.reservation_service import ReservationService

app = FastAPI()

# wiring (hexagonal)
repository = CategoryRepositoryImpl()
use_case = CategoryUseCase(repository)
reservation_repository = ReservationRepositoryImpl()
reservation_service = ReservationService(reservation_repository)
reservation_use_case = ReservationUseCase(reservation_service, repository)

# register route
app.include_router(create_category_controller(use_case))
app.include_router(create_reservation_controller(reservation_use_case))