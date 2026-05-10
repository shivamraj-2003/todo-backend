from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from database import tasks_collection
from models import Task, TaskCreate, TaskUpdate, TaskStatus
from auth import get_current_user

router = APIRouter()

def serialize_task(task) -> dict:
    task["id"] = str(task["_id"])
    del task["_id"]
    return task

@router.get("/", response_model=List[dict])
async def get_tasks(
    current_user: dict = Depends(get_current_user),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    sortBy: Optional[str] = "createdAt",
    order: Optional[int] = -1 # -1 for desc, 1 for asc
):
    query = {"user_id": current_user["_id"]}
    if status:
        query["status"] = status
    if priority:
        query["priority"] = priority
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    cursor = tasks_collection.find(query).sort(sortBy, order)
    tasks = await cursor.to_list(length=100)
    
    # Check for overdue tasks
    now = datetime.utcnow()
    updated_tasks = []
    for task in tasks:
        if task.get("dueDate") and task["dueDate"] < now and task["status"] != TaskStatus.COMPLETED:
            if task["status"] != TaskStatus.OVERDUE:
                task["status"] = TaskStatus.OVERDUE
                await tasks_collection.update_one({"_id": task["_id"]}, {"$set": {"status": TaskStatus.OVERDUE}})
        updated_tasks.append(serialize_task(task))
        
    return updated_tasks

@router.post("/", response_model=dict)
async def create_task(task: TaskCreate, current_user: dict = Depends(get_current_user)):
    task_dict = task.dict()
    task_dict["user_id"] = current_user["_id"]
    task_dict["createdAt"] = datetime.utcnow()
    task_dict["updatedAt"] = datetime.utcnow()
    
    result = await tasks_collection.insert_one(task_dict)
    return serialize_task(task_dict)

@router.put("/{task_id}", response_model=dict)
async def update_task(task_id: str, task_update: TaskUpdate, current_user: dict = Depends(get_current_user)):
    update_data = {k: v for k, v in task_update.dict().items() if v is not None}
    update_data["updatedAt"] = datetime.utcnow()
    
    result = await tasks_collection.update_one(
        {"_id": ObjectId(task_id), "user_id": current_user["_id"]},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    updated_task = await tasks_collection.find_one({"_id": ObjectId(task_id)})
    return serialize_task(updated_task)

@router.delete("/{task_id}")
async def delete_task(task_id: str, current_user: dict = Depends(get_current_user)):
    result = await tasks_collection.delete_one({"_id": ObjectId(task_id), "user_id": current_user["_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}

@router.get("/analytics")
async def get_analytics(current_user: dict = Depends(get_current_user)):
    pipeline = [
        {"$match": {"user_id": current_user["_id"]}},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    cursor = tasks_collection.aggregate(pipeline)
    results = await cursor.to_list(length=10)
    
    stats = {status.value: 0 for status in TaskStatus}
    for res in results:
        stats[res["_id"]] = res["count"]
    
    return stats
