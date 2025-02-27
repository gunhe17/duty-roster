#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import random
import datetime
import sys

DATABASE_FILE = 'database.json'
INPUT_FILE = 'input.json'
INPUT_TEMPLATE_FILE = 'input.template.json'
LOG_FILE = 'selection_log.txt'


def create_default_database():
    """database.json 파일이 없을 경우 기본 구조로 생성합니다."""
    default_data = {"employees": []}
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(default_data, f, ensure_ascii=False, indent=4)
    print(f"[INFO] {DATABASE_FILE} 파일을 생성하였습니다.")


def create_input_template():
    """input.template.json 파일을 생성하여 input.json의 형식을 문서화합니다."""
    template = {
        "employees": [
            {
                "id": "정수형, 각 직원의 고유 ID (예: 1)",
                "name": "문자열, 직원의 이름 (예: '홍길동')",
                "chosen_number": "정수형, 직원이 선택한 번호 (참고용, 당첨 확률에 영향 없음, 예: 5)"
            }
        ]
    }
    with open(INPUT_TEMPLATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(template, f, ensure_ascii=False, indent=4)
    print(f"[INFO] {INPUT_TEMPLATE_FILE} 파일을 생성하였습니다.")


def create_default_input():
    """input.json 파일이 없을 경우 기본 구조로 생성합니다."""
    default_input = {
        "employees": [
            # 예시 데이터. 실제 사용 시 input.template.json 을 참고하여 작성해주세요.
            {"id": 1, "name": "홍길동", "chosen_number": 5},
            {"id": 2, "name": "김철수", "chosen_number": 3}
        ]
    }
    with open(INPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(default_input, f, ensure_ascii=False, indent=4)
    print(f"[INFO] {INPUT_FILE} 파일을 생성하였습니다. input.template.json 을 참고하여 내용을 수정하세요.")


def load_json(filename):
    """파일 이름에 해당하는 JSON 파일을 읽어 리턴합니다."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] {filename} 파일을 읽는 중 오류가 발생하였습니다: {e}")
        return None


def save_json(filename, data):
    """데이터를 JSON 형식으로 파일에 저장합니다."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"[ERROR] {filename} 파일에 데이터를 저장하는 중 오류가 발생하였습니다: {e}")


def add_employee(new_employee):
    """
    신입사원 추가 함수입니다.
    new_employee는 딕셔너리 형태로 {"id": int, "name": str} 등이 포함되어야 하며,
    duty_count와 consecutive는 기본값 0으로 초기화합니다.
    """
    db = load_json(DATABASE_FILE)
    if db is None:
        return
    # 중복 확인
    for emp in db["employees"]:
        if emp["id"] == new_employee["id"]:
            print(f"[INFO] 이미 존재하는 직원입니다: {new_employee['name']}")
            return
    new_entry = {
        "id": new_employee["id"],
        "name": new_employee["name"],
        "duty_count": 0,
        "consecutive": 0
    }
    db["employees"].append(new_entry)
    save_json(DATABASE_FILE, db)
    print(f"[INFO] 신규 직원 {new_employee['name']} (ID: {new_employee['id']}) 을 추가하였습니다.")


def remove_employee(employee_id):
    """
    퇴사자 삭제 함수입니다.
    employee_id에 해당하는 직원 정보를 database.json에서 삭제합니다.
    """
    db = load_json(DATABASE_FILE)
    if db is None:
        return
    original_len = len(db["employees"])
    db["employees"] = [emp for emp in db["employees"] if emp["id"] != employee_id]
    if len(db["employees"]) < original_len:
        save_json(DATABASE_FILE, db)
        print(f"[INFO] ID {employee_id}인 직원을 삭제하였습니다.")
    else:
        print(f"[INFO] ID {employee_id}인 직원을 찾지 못하였습니다.")


def log_message(message):
    """메시지를 콘솔과 로그 파일에 기록합니다."""
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_entry = f"{timestamp} {message}"
    print(log_entry)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + "\n")


def run_selection():
    """
    메인 청소 당번 선정 함수입니다.
    - input.json 파일에 담긴 직원들(각 직원의 chosen_number 정보는 참고용)로부터 참여 대상을 구성합니다.
    - 콘솔 입력을 통해 이번 달 추첨 주차 수를 입력받습니다.
    - 각 주마다 아직 당번에 선정되지 않았으며, 최근 두 달 연속 당번이었던 직원은 제외하고,
      가중치(당번 횟수가 적은 직원에게 유리)를 산출하여 무작위로 한 명을 선정합니다.
    - 한 직원은 한 달에 한 번만 당번으로 선정됩니다.
    - 선정 결과와 함께 duty_count, consecutive 값을 업데이트합니다.
    """
    # 파일 존재 여부 확인 및 생성
    if not os.path.exists(DATABASE_FILE):
        create_default_database()
    if not os.path.exists(INPUT_FILE):
        create_default_input()
    if not os.path.exists(INPUT_TEMPLATE_FILE):
        create_input_template()

    # input.json에서 참여 직원 정보 읽기
    input_data = load_json(INPUT_FILE)
    if input_data is None or "employees" not in input_data:
        log_message("[ERROR] input.json 파일의 형식이 올바르지 않습니다.")
        return

    # database.json 읽기
    db = load_json(DATABASE_FILE)
    if db is None or "employees" not in db:
        log_message("[ERROR] database.json 파일의 형식이 올바르지 않습니다.")
        return

    # input.json의 직원들을 database.json에 동기화 (신규 직원 추가)
    db_employee_ids = {emp["id"] for emp in db["employees"]}
    for inp_emp in input_data["employees"]:
        if inp_emp["id"] not in db_employee_ids:
            add_employee({"id": inp_emp["id"], "name": inp_emp["name"]})

    # 최신의 database.json 불러오기
    db = load_json(DATABASE_FILE)

    # 이번 달 추첨 주차 수 입력 (예: 몇 주 동안 청소 당번을 정할 것인지)
    while True:
        try:
            weeks = int(input("이번 달 청소 당번 추첨 주차 수를 입력해 주세요 (예: 4): "))
            if weeks < 1:
                raise ValueError
            break
        except ValueError:
            print("올바른 정수를 입력해 주세요.")

    # 이번 달 선정된 직원의 ID를 기록 (한 직원은 한 달에 단 한 번만 선정)
    selected_this_month = set()

    # 매 주마다 당번 선정
    weekly_results = []
    for week in range(1, weeks + 1):
        # eligible: input.json에 참여하며 아직 선정되지 않았고, 최근 두 달 연속 당번이 아니신 분
        eligible = []
        for emp in db["employees"]:
            # input.json에 참여하는 직원인지 확인 (id 기준)
            if any(emp["id"] == inp["id"] for inp in input_data["employees"]):
                if emp["id"] in selected_this_month:
                    continue  # 이미 이번 달에 선정됨
                if emp.get("consecutive", 0) >= 2:
                    continue  # 최근 2개월 연속 당번인 경우 이번 달 선정 제외
                eligible.append(emp)

        if not eligible:
            log_message(f"[WARN] 주차 {week}: 선정 가능한 직원이 없습니다. (조건에 맞는 직원이 부족합니다.)")
            continue

        # 가중치 산출: 각 직원의 effective_count = max(duty_count, baseline)
        # baseline: eligible 직원들의 duty_count 평균 (평균이 0이면 1로 대체)
        total = sum(emp.get("duty_count", 0) for emp in eligible)
        avg = total / len(eligible) if eligible else 0
        baseline = avg if avg > 0 else 1

        weights = []
        for emp in eligible:
            duty = emp.get("duty_count", 0)
            effective = duty if duty > baseline else baseline
            # 당번 횟수가 적을수록 높은 확률: weight = 1/(effective + 1)
            weight = 1 / ((effective + 1) ** 50)
            weights.append(weight)
            print(f"weight: {weight}", "duty", duty, "baseline", baseline)

        chosen = random.choices(eligible, weights=weights, k=1)[0]
        selected_this_month.add(chosen["id"])
        weekly_results.append({
            "week": week,
            "id": chosen["id"],
            "name": chosen["name"],
            "duty_count_before": chosen.get("duty_count", 0)
        })
        log_message(f"주차 {week}: {chosen['name']} (ID: {chosen['id']})님이 선정되었습니다.")

        # 당번 횟수는 즉시 증가시키지 않고, 최종 업데이트 단계에서 한 번에 처리

    # 이번 달 선정 결과를 토대로 database 업데이트
    # 이번 달에 선정된 직원은 duty_count 증가, consecutive += 1
    # 선정되지 않은 직원은 consecutive 초기화(0) 처리
    for emp in db["employees"]:
        if emp["id"] in selected_this_month:
            emp["duty_count"] = emp.get("duty_count", 0) + 1
            emp["consecutive"] = emp.get("consecutive", 0) + 1
        else:
            emp["consecutive"] = 0

    save_json(DATABASE_FILE, db)

    # 최종 결과 출력 (표 형식으로 단정하게 출력)
    print("\n=== 이번 달 청소 당번 선정 결과 ===")
    print(f"{'주차':<5}{'직원 ID':<10}{'이름':<15}{'당번 전 횟수':<15}")
    for res in weekly_results:
        print(f"{res['week']:<5}{res['id']:<10}{res['name']:<15}{res['duty_count_before']:<15}")
    print("==================================\n")
    log_message("이번 달 청소 당번 선정이 완료되었습니다.")


def main():
    """
    프로그램의 메인 함수입니다.
    추가로 명령행 인수를 통해 신입사원 추가, 퇴사자 삭제 기능을 사용할 수 있습니다.
    인수가 없으면 청소 당번 선정 기능을 실행합니다.
    """
    # 명령행 인수가 있을 경우 간단한 메뉴 제공
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'add' and len(sys.argv) == 4:
            try:
                emp_id = int(sys.argv[2])
                emp_name = sys.argv[3]
                add_employee({"id": emp_id, "name": emp_name})
            except ValueError:
                print("직원 ID는 정수여야 합니다.")
        elif cmd == 'remove' and len(sys.argv) == 3:
            try:
                emp_id = int(sys.argv[2])
                remove_employee(emp_id)
            except ValueError:
                print("직원 ID는 정수여야 합니다.")
        else:
            print("사용법:")
            print("  청소 당번 선정 실행: python cleaning_duty.py")
            print("  신입사원 추가: python cleaning_duty.py add [id] [이름]")
            print("  퇴사자 삭제: python cleaning_duty.py remove [id]")
    else:
        run_selection()


if __name__ == '__main__':
    main()