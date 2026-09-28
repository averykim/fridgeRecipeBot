import csv
from typing import List, Dict, Any
from app.external.fetchers.base import RecipeFetcher

class CSVPublicFetcher(RecipeFetcher):
    def __init__(self, file_path: str):
        self.file_path = file_path

    async def fetch(self, limit: int = 5) -> List[Dict[str, Any]]:
        standardized_recipes = []
        
        # httpx 대신 내장 csv 모듈을 사용해 로컬 파일 읽기
        with open(self.file_path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            
            for i, row in enumerate(reader):
                if i >= limit:
                    break
                    
                # 공공데이터 CSV의 컬럼명(예: RCP_NM, MANUAL01)을 우리 표준으로 매핑
                standardized_recipes.append({
                    "title": row.get("RCP_NM", "제목 없음"),
                    "description": "공공데이터 레시피",
                    "instructions": row.get("MANUAL01", ""),
                    "cooking_time": 30,
                    "difficulty": "Medium",
                    # CSV의 긴 텍스트 재료를 리스트로 쪼개는 로직이 필요하다면 여기서 처리
                    "ingredients": [row.get("RCP_PARTS_DTLS", "")] 
                })
                
        return standardized_recipes
    
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