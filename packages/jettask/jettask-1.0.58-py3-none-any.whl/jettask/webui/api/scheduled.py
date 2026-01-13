"""
定时任务模块 - 定时任务管理、执行和监控
使用 Jettask App 的调度方法实现任务管理
"""
from fastapi import APIRouter, HTTPException, Request, Query
from typing import Optional
import logging

router = APIRouter(prefix="/scheduled", tags=["scheduled"])
logger = logging.getLogger(__name__)




@router.get(
    "/schedules",
    summary="获取定时任务列表",
    description="获取当前命名空间下所有定时任务的列表",
    responses={
        200: {
            "description": "成功返回定时任务列表",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": [
                            {
                                "id": 1,
                                "scheduler_id": "my_task_001",
                                "queue_name": "email_queue",
                                "task_type": "interval",
                                "interval_seconds": 60,
                                "enabled": True,
                                "next_run_time": "2025-10-19T12:00:00Z"
                            }
                        ],
                        "total": 1
                    }
                }
            }
        },
        500: {"description": "服务器内部错误"}
    }
)
async def list_schedules(
    request: Request,
    enabled: Optional[bool] = Query(None, description="筛选启用/禁用状态"),
    queue_name: Optional[str] = Query(None, description="筛选队列名称"),
    task_type: Optional[str] = Query(None, description="筛选任务类型（interval/cron/once）")
):
    try:
        ns = request.state.ns

        jettask_app = await ns.get_jettask_app()

        filters = {}
        if enabled is not None:
            filters['enabled'] = enabled
        if queue_name:
            filters['queue_name'] = queue_name
        if task_type:
            filters['task_type'] = task_type

        tasks = await jettask_app.list_schedules(**filters)

        result = []
        for task in tasks:
            task_dict = {
                "id": task.id,
                "scheduler_id": task.scheduler_id,
                "queue_name": task.queue_name,
                "task_type": task.task_type,
                "namespace": task.namespace,
                "enabled": task.enabled,
                "priority": task.priority,
                "description": task.description,
                "next_run_time": task.next_run_time.isoformat() if task.next_run_time else None,
                "last_run_time": task.last_run_time.isoformat() if task.last_run_time else None,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            }

            if task.interval_seconds:
                task_dict["interval_seconds"] = task.interval_seconds
            if task.cron_expression:
                task_dict["cron_expression"] = task.cron_expression

            if task.task_args:
                task_dict["task_args"] = task.task_args
            if task.task_kwargs:
                task_dict["task_kwargs"] = task.task_kwargs

            result.append(task_dict)

        logger.info(f"获取定时任务列表: namespace={ns.name}, count={len(result)}")
        return {
            "success": True,
            "data": result,
            "total": len(result)
        }

    except Exception as e:
        logger.error(f"获取定时任务列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/schedules/register",
    summary="注册定时任务",
    description="批量注册定时任务",
    status_code=201,
    responses={
        201: {
            "description": "定时任务注册成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "成功注册 2 个定时任务",
                        "registered_count": 2
                    }
                }
            }
        },
        400: {
            "description": "请求参数错误",
            "content": {
                "application/json": {
                    "example": {"detail": "调度配置无效: 必须指定 interval_seconds、cron_expression 或 next_run_time 之一"}
                }
            }
        },
        500: {"description": "服务器内部错误"}
    }
)
async def register_schedules(request: Request):
    try:
        ns = request.state.ns

        jettask_app = await ns.get_jettask_app()

        body = await request.json()
        schedules_data = body.get('schedules', [])
        skip_if_exists = body.get('skip_if_exists', True)

        if not schedules_data:
            raise HTTPException(status_code=400, detail="schedules 列表不能为空")

        from jettask.scheduler.definition import Schedule
        from datetime import datetime

        schedules = []
        for data in schedules_data:
            if not data.get('scheduler_id'):
                raise HTTPException(status_code=400, detail="scheduler_id 是必填字段")
            if not data.get('queue'):
                raise HTTPException(status_code=400, detail="queue 是必填字段")

            next_run_time = data.get('next_run_time')
            if isinstance(next_run_time, str):
                next_run_time = datetime.fromisoformat(next_run_time.replace('Z', '+00:00'))

            try:
                schedule = Schedule(
                    scheduler_id=data['scheduler_id'],
                    queue=data['queue'],
                    interval_seconds=data.get('interval_seconds'),
                    cron_expression=data.get('cron_expression'),
                    next_run_time=next_run_time,
                    args=data.get('args', []),
                    kwargs=data.get('kwargs', {}),
                    priority=data.get('priority'),
                    timeout=data.get('timeout', 300),
                    max_retries=data.get('max_retries', 3),
                    retry_delay=data.get('retry_delay', 60),
                    enabled=data.get('enabled', True),
                    description=data.get('description'),
                    tags=data.get('tags', []),
                    metadata=data.get('metadata', {}),
                    skip_if_exists=skip_if_exists
                )
                schedules.append(schedule)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"调度配置无效: {str(e)}")

        registered_count = await jettask_app.register_schedules(schedules)

        logger.info(f"注册定时任务: namespace={ns.name}, count={registered_count}")
        return {
            "success": True,
            "message": f"成功注册 {registered_count} 个定时任务",
            "registered_count": registered_count
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"注册定时任务失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/schedules/{scheduler_id}",
    summary="修改定时任务",
    description="通过 scheduler_id 修改指定的定时任务配置",
    responses={
        200: {
            "description": "任务修改成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "定时任务已更新",
                        "scheduler_id": "my_task_001"
                    }
                }
            }
        },
        404: {
            "description": "任务不存在",
            "content": {
                "application/json": {
                    "example": {"detail": "定时任务 'my_task_001' 不存在"}
                }
            }
        },
        500: {"description": "服务器内部错误"}
    }
)
async def update_schedule(request: Request, scheduler_id: str):
    try:
        ns = request.state.ns

        body = await request.json()

        from jettask.db.models import ScheduledTask

        pg_session = await ns.get_pg_session()
        try:
            task = await ScheduledTask.get_by_scheduler_id(pg_session, scheduler_id)
            if not task:
                raise HTTPException(status_code=404, detail=f"定时任务 '{scheduler_id}' 不存在")

            if 'enabled' in body:
                task.enabled = body['enabled']
            if 'interval_seconds' in body:
                task.interval_seconds = body['interval_seconds']
            if 'cron_expression' in body:
                task.cron_expression = body['cron_expression']
            if 'args' in body:
                task.task_args = body['args']
            if 'kwargs' in body:
                task.task_kwargs = body['kwargs']
            if 'priority' in body:
                task.priority = body['priority']
            if 'timeout' in body:
                task.timeout = body['timeout']
            if 'max_retries' in body:
                task.max_retries = body['max_retries']
            if 'retry_delay' in body:
                task.retry_delay = body['retry_delay']
            if 'description' in body:
                task.description = body['description']

            await ScheduledTask.update_task(pg_session, task)
            await pg_session.commit()

            logger.info(f"定时任务已更新: scheduler_id={scheduler_id}, namespace={ns.name}")
            return {
                "success": True,
                "message": "定时任务已更新",
                "scheduler_id": scheduler_id
            }

        finally:
            await pg_session.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"修改定时任务失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/schedules/{scheduler_id}",
    summary="删除定时任务",
    description="通过 scheduler_id 删除指定的定时任务",
    responses={
        200: {
            "description": "任务删除成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "定时任务已删除",
                        "scheduler_id": "my_task_001"
                    }
                }
            }
        },
        404: {
            "description": "任务不存在",
            "content": {
                "application/json": {
                    "example": {"detail": "定时任务 'my_task_001' 不存在"}
                }
            }
        },
        500: {"description": "服务器内部错误"}
    }
)
async def remove_schedule(request: Request, scheduler_id: str):
    try:
        ns = request.state.ns

        jettask_app = await ns.get_jettask_app()

        success = await jettask_app.remove_schedule(scheduler_id)

        if success:
            logger.info(f"定时任务已删除: scheduler_id={scheduler_id}, namespace={ns.name}")
            return {
                "success": True,
                "message": "定时任务已删除",
                "scheduler_id": scheduler_id
            }
        else:
            raise HTTPException(status_code=404, detail=f"定时任务 '{scheduler_id}' 不存在")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除定时任务失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


__all__ = ['router']
