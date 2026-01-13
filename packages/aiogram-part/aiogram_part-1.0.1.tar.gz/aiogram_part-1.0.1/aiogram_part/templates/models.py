class ModelTemplates:
    @staticmethod
    def get_model_template(name: str) -> str:
        class_name = name.capitalize()
        table_name = name.lower() + "s"
        
        return f'''from tortoise import fields
from tortoise.models import Model

class {class_name}(Model):
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "{table_name}"
    
    def __str__(self):
        return f"{class_name}(id={{self.id}})"
'''
    
    @staticmethod
    def get_crud_template(name: str) -> str:
        class_name = name.capitalize()
        
        return f'''from typing import Optional
from database.models.{name.lower()} import {class_name}

class {class_name}CRUD:
    @staticmethod
    async def create(**kwargs) -> {class_name}:
        return await {class_name}.create(**kwargs)
    
    @staticmethod
    async def get(id: int) -> Optional[{class_name}]:
        return await {class_name}.filter(id=id).first()
    
    @staticmethod
    async def get_all() -> list[{class_name}]:
        return await {class_name}.all()
    
    @staticmethod
    async def update(id: int, **kwargs) -> Optional[{class_name}]:
        await {class_name}.filter(id=id).update(**kwargs)
        return await {class_name}.get(id=id)
    
    @staticmethod
    async def delete(id: int) -> bool:
        deleted = await {class_name}.filter(id=id).delete()
        return deleted > 0
    
    @staticmethod
    async def count() -> int:
        return await {class_name}.all().count()
'''
