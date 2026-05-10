from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, tasks

app = FastAPI(title="Shivam Todo API")

# Configure CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://your-netlify-site-name.netlify.app", # REPLACE with your actual Netlify URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])

@app.get("/")
async def root():
    return {"message": "Welcome to Shivam Todo API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
