import random
import json
from typing import List, Dict

HISTORY_FILE = "cleaning_history.json"

class User:
    def __init__(self, name: str, history_count: int = 0):
        self.name = name
        self.history_count = history_count

    def to_dict(self):
        return {"name": self.name, "history_count": self.history_count}

    @staticmethod
    def from_dict(data: Dict):
        return User(data["name"], data["history_count"])


class HistoryManager:
    @staticmethod
    def load(user_names: List[str]) -> List[User]:
        """JSON 파일에서 사용자 히스토리를 불러옵니다."""
        users = {name: User(name) for name in user_names}
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                history = json.load(file)
                for record in history:
                    if record["name"] in users:
                        users[record["name"]].history_count = record["history_count"]
        except FileNotFoundError:
            pass  # 파일이 없으면 초기 히스토리를 그대로 유지
        return list(users.values())

    @staticmethod
    def save(users: List[User]):
        """사용자 히스토리를 JSON 파일로 저장합니다."""
        # 이름 기준으로 정렬
        sorted_users = sorted(users, key=lambda u: u.name)
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump([user.to_dict() for user in sorted_users], file, ensure_ascii=False, indent=4)


class DutyAssigner:
    def __init__(self, users: List[User]):
        self.users = users

    def assign(self, num_weeks: int) -> Dict[str, List[User]]:
        """청소 당번을 주차별로 배정합니다."""
        assignments = {}
        user_pool = self.users.copy()

        for week in range(1, num_weeks + 1):
            if len(user_pool) < 2:
                break
            # 가중치 기반 샘플링
            weights = [1 / (user.history_count + 1) for user in user_pool]
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights]

            # random.sample과 가중치로 사용자 2명 선택
            assigned = random.choices(user_pool, weights=normalized_weights, k=2)

            # 중복 제거 후 추가
            while len(set(assigned)) < 2:
                assigned = random.choices(user_pool, weights=normalized_weights, k=2)

            assignments[f"{week}주차"] = assigned
            # 선정된 사용자 히스토리 업데이트
            for user in assigned:
                user.history_count += 1
            # 선정된 사용자 제거
            user_pool = [u for u in user_pool if u not in assigned]

        return assignments

    def get_remaining_users(self, assignments: Dict[str, List[User]]) -> List[User]:
        """남은 사용자 목록을 반환합니다."""
        assigned_users = {user for week in assignments.values() for user in week}
        return [user for user in self.users if user not in assigned_users]



class CleaningDutyApp:
    def __init__(self, users: list, num_weeks: int):
        self.user_names = users
        self.num_weeks = num_weeks

    def run(self):
        # 히스토리 로드
        users = HistoryManager.load(self.user_names)

        # 당번 배정
        assigner = DutyAssigner(users)
        assignments = assigner.assign(self.num_weeks)
        remaining_users = assigner.get_remaining_users(assignments)

        # 결과 출력
        self.print_results(assignments, remaining_users)

        # 히스토리 저장
        HistoryManager.save(users)

    @staticmethod
    def print_results(assignments: Dict[str, List[User]], remaining_users: List[User]):
        print("청소 당번 배정:")
        for week, assigned in assignments.items():
            print(f"{week}: {', '.join(user.name for user in assigned)}")
        print("\nPass 인원:")
        print(", ".join(user.name for user in remaining_users))
        print("\n최종 히스토리:")
        for user in remaining_users + [u for week in assignments.values() for u in week]:
            print(f"{user.name}: {user.history_count}회 선정")


if __name__ == "__main__":
    CleaningDutyApp(
        users=[
            "정재인",
            "안예린",
            "정영진",
            "이현준",
            "홍혜린",
            "김건희",
            "안유민",
            "이신실",
            "소요섭",
            "김종원",
            "임소영",
            "홍성균",
            "김태형",
            "최지훈",
            "홍혜린",
            "조수진",
            "전은아",
            "최지혜",
            "김주한",
            "석정도",
        ],
        num_weeks=4
    ).run()


