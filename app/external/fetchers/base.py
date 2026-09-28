from abc import ABC, abstractmethod
from typing import List, Dict, Any

class RecipeFetcher(ABC):
    @abstractmethod
    async def fetch(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Return format
        [
            {
                "title: "Recipe Name",
                "instructions": "STEPS",
                "ingredients": ["ingredient 1", "ingredient 2"]
            }
        ]
        """
        pass

# 2. TheMealDB 전용 수집 및 변환기
class TheMealDBFetcher(RecipeFetcher):
    async def fetch(self, limit: int = 5) -> List[Dict[str, Any]]:
        standardized_list = []
        # httpx로 TheMealDB API 호출 로직...
        # data = response.json()
        
        # TheMealDB 전용 데이터를 표준 포맷으로 매핑
        # standardized_list.append({
        #     "title": data["strMeal"],
        #     "instructions": data["strInstructions"],
        #     "ingredients": [...]
        # })
        return standardized_list

# 3. 식품안전나라 공공데이터 전용 수집 및 변환기
class KoreanPublicFetcher(RecipeFetcher):
    async def fetch(self, limit: int = 5) -> List[Dict[str, Any]]:
        standardized_list = []
        # httpx로 식약처 API 호출 로직...
        
        # 공공데이터 전용 데이터를 표준 포맷으로 매핑
        # standardized_list.append({
        #     "title": data["RCP_NM"],
        #     "instructions": f"1. {data['MANUAL01']}\n2. {data['MANUAL02']}",
        #     "ingredients": [...]
        # })
        return standardized_list