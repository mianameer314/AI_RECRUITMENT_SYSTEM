# Dashboard analytics queries
from app.db.mongo import db
from datetime import datetime, timedelta

class DashboardService:

    @staticmethod
    async def get_overview():
        jobs = await db.jobs.count_documents({})
        users = await db.users.count_documents({"role": "candidate"})
        admins = await db.users.count_documents({"role": "admin"})
        applications = await db.applications.count_documents({})
        return {
            "total_jobs": jobs,
            "total_candidates": users,
            "total_admins": admins,
            "total_applications": applications
        }

    @staticmethod
    async def get_jobs_per_location():
        pipeline = [
            {"$group": {"_id": "$location", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        return await db.jobs.aggregate(pipeline).to_list(length=5)

    @staticmethod
    async def get_applications_per_job():
        pipeline = [
            {"$group": {"_id": "$job_id", "applications": {"$sum": 1}}},
            {"$sort": {"applications": -1}},
            {"$limit": 10}
        ]
        return await db.applications.aggregate(pipeline).to_list(length=10)

    @staticmethod
    async def get_daily_applications():
        last_7_days = datetime.utcnow() - timedelta(days=7)
        pipeline = [
            {"$match": {"created_at": {"$gte": last_7_days}}},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        return await db.applications.aggregate(pipeline).to_list(length=7)

    @staticmethod
    async def get_most_applied_jobs():
        pipeline = [
            {"$group": {"_id": "$job_id", "total": {"$sum": 1}}},
            {"$sort": {"total": -1}},
            {"$limit": 5}
        ]
        return await db.applications.aggregate(pipeline).to_list(length=5)

    @staticmethod
    async def get_most_active_candidates():
        pipeline = [
            {"$group": {"_id": "$username", "total_applications": {"$sum": 1}}},
            {"$sort": {"total_applications": -1}},
            {"$limit": 5}
        ]
        return await db.applications.aggregate(pipeline).to_list(length=5)

    @staticmethod
    async def get_applications_status_breakdown():
        pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        return await db.applications.aggregate(pipeline).to_list(length=10)

    @staticmethod
    async def get_recent_activity():
        latest_jobs = await db.jobs.find().sort("created_at", -1).limit(5).to_list(length=5)
        latest_apps = await db.applications.find().sort("created_at", -1).limit(5).to_list(length=5)
        return {
            "recent_jobs": latest_jobs,
            "recent_applications": latest_apps
        }

