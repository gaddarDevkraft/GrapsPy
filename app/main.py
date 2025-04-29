from fastapi import FastAPI
from app.config.database import engine
import app.models.blog_model as model
from app.route import blog_route, user_route

app = FastAPI()

model.BASE.metadata.create_all(bind = engine)


app.include_router(blog_route.router)
app.include_router(user_route.router)




#for the debugging
# import uvicorn
# if __name__ == "__main__":
#     uvicorn.run(app, host = "0.0.0.0", port = 8000)
