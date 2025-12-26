from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from app.schemas import PostCreate,PostResponse
from app.db import Post,get_async_session,create_db_and_tables
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import shutil
import os
import uuid
import tempfile

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/upload")
async def upload_file(
    file:UploadFile = File(...),
    caption:str = Form(""),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        with tempfile.NamedTemporaryFile(delete=False,suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path -=temp_file
            shutil.copyfileobj(file.file,temp_file)

        upload_result = imagekit.upload_file(
            file=open(temp_file_path,"rb"),
            file_name=file.filename,
            options=UploadFileRequestOptions(
                use_unique_file_name=True,
                tags=["backend-upload"]
            )
        )

    post = Post(
        caption=caption,
        url="dummy url",
        file_type="photo",
        file_name="dummy name"
    )
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post

@app.get("/feed")
async def get_feed(
       session: AsyncSession = Depends(get_async_session)
):
    result =await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts=[row[0] for row in result.all()]

    posts_data =[]
    for post in posts:
        posts_data.append(
            {
                "id":str(post.id),
                "caption":post.caption,
                "url":post.url,
                "file_type":post.file_type,
                "file_name":post.file_name,
                "created_at":post.created_at.isoformat()
            }
        )
    return {"posts": posts_data}