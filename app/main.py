from fastapi import FastAPI
from app.routers.routes_auth import router as auth_router
from app.routers.routes_users import router as users_router
from app.routers.routes_books import router as books_router
from app.routers.routes_loans import router as loans_router

app = FastAPI(title="Library Lending API", version="1.0.0")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(books_router)
app.include_router(loans_router)

@app.get("/")
def root():
    return {"message": "Library Lending API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}
