from typing import List, Optional
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Pond

class PondRepository:    
    @staticmethod
    def create_pond(owner: User, name: str, image_name: Optional[str], length: float, width: float, depth: float) -> Pond:
        return Pond.objects.create(
            owner=owner,
            name=name,
            image_name=image_name,
            length=length,
            width=width,
            depth=depth
        )
    
    @staticmethod
    def get_pond_by_id(pond_id: str) -> Pond:
        return get_object_or_404(Pond, pond_id=pond_id)
    
    @staticmethod
    def list_ponds_by_user(user: User) -> List[Pond]:
        return Pond.objects.filter(owner=user)