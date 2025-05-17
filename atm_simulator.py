# atm_simulator.py
import os
import random
import time
import requests
import json
from datetime import datetime, timezone

# --- КОНФИГУРАЦИЯ ---
# Получаем из переменных окружения
ATM_ID_IN_DB = os.environ.get("ATM_ID_IN_DB")
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api/v1") # Для локального теста без Docker
SIMULATOR_API_KEY = os.environ.get("SIMULATOR_API_KEY")

# Проверки обязательных переменных окружения
if not ATM_ID_IN_DB:
    print("CRITICAL: ATM_ID_IN_DB environment variable not set. Exiting.")
    exit(1)

# LOG_ENDPOINT формируется на основе API_BASE_URL и ATM_ID_IN_DB
LOG_ENDPOINT = f"{API_BASE_URL}/atms/{ATM_ID_IN_DB}/logs/"

# --- Справочники ID (на основе ваших данных) ---
LOG_LEVEL_IDS = {
    "DEBUG": 1,
    "INFO": 2,
    "WARN": 3,
    "ERROR": 4,
    "CRITICAL": 5
}

EVENT_TYPE_IDS = {
    "COMMUNICATION_ERROR": 13,
    "CARD_JAMMED": 11,
    "PRINTER_ERROR": 12,
    "INVALID_PIN_ATTEMPT": 10,
    "TAMPER_DETECTED": 9,
    "COMPONENT_FAILURE": 7,
    "LOW_CASH_LEVEL": 8,
    "SYSTEM_BOOT": 5,
    "SYSTEM_SHUTDOWN": 6,
    "BALANCE_INQUIRY": 3,
    "CASH_WITHDRAWAL": 1,
    "DEPOSIT": 2,
    "PAYMENT": 4
}

# --- Функции симулятора ---

def generate_log_entry():
    """Генерирует случайную запись лога."""
    now_utc_iso = datetime.now(timezone.utc).isoformat()

    # Список возможных событий с их атрибутами
    # (сообщение, уровень_лога_ID, тип_события_ID, это_алерт?, payload)
    # None для event_type_id означает, что это общее событие без специфического типа
    possible_events = [
        ("Successful cash withdrawal", LOG_LEVEL_IDS["INFO"], EVENT_TYPE_IDS["CASH_WITHDRAWAL"], False, {"amount": random.randint(10, 500) * 100, "currency": "RUB", "card_last_4_digits": f"{random.randint(1000,9999)}"}),
        ("System boot sequence initiated", LOG_LEVEL_IDS["INFO"], EVENT_TYPE_IDS["SYSTEM_BOOT"], False, {"firmware_version": "v2.3.1"}),
        ("System shutdown requested by operator", LOG_LEVEL_IDS["INFO"], EVENT_TYPE_IDS["SYSTEM_SHUTDOWN"], False, {"reason": "scheduled_maintenance"}),
        ("Balance inquiry performed", LOG_LEVEL_IDS["INFO"], EVENT_TYPE_IDS["BALANCE_INQUIRY"], False, {"account_type": "savings"}),
        ("Cash deposit accepted", LOG_LEVEL_IDS["INFO"], EVENT_TYPE_IDS["DEPOSIT"], False, {"amount": random.randint(5, 100) * 100, "currency": "RUB", "envelope_id": f"DEP{random.randint(10000,99999)}"}),
        ("Payment processed for utility bill", LOG_LEVEL_IDS["INFO"], EVENT_TYPE_IDS["PAYMENT"], False, {"provider_id": "UtilityCo", "amount": random.randint(50, 2000)}),

        ("Card jammed in reader", LOG_LEVEL_IDS["ERROR"], EVENT_TYPE_IDS["CARD_JAMMED"], True, {"error_code": "CJ-001", "reader_status": "blocked"}),
        ("Printer error: out of paper", LOG_LEVEL_IDS["ERROR"], EVENT_TYPE_IDS["PRINTER_ERROR"], True, {"printer_id": "P1", "status_code": "PAPER_EMPTY"}),
        ("Component failure: keypad unresponsive", LOG_LEVEL_IDS["ERROR"], EVENT_TYPE_IDS["COMPONENT_FAILURE"], True, {"component": "keypad", "details": "no_input_detected"}),
        ("Communication error with processing center", LOG_LEVEL_IDS["ERROR"], EVENT_TYPE_IDS["COMMUNICATION_ERROR"], True, {"host": "10.0.1.55", "port": 8443, "error": "timeout"}),

        ("Multiple invalid PIN attempts", LOG_LEVEL_IDS["WARN"], EVENT_TYPE_IDS["INVALID_PIN_ATTEMPT"], True, {"attempts": 3, "card_retained": False}),
        ("Tamper sensor activated: casing opened", LOG_LEVEL_IDS["CRITICAL"], EVENT_TYPE_IDS["TAMPER_DETECTED"], True, {"sensor_id": "casing_main_door", "severity": "high"}),
        ("Low cash level in cassette A1", LOG_LEVEL_IDS["WARN"], EVENT_TYPE_IDS["LOW_CASH_LEVEL"], True, {"cassette_id": "A1-RUB-5000", "remaining_notes": random.randint(10, 50)}),

        ("Unspecified operational warning", LOG_LEVEL_IDS["WARN"], None, False, {"details": "Minor sensor fluctuation detected."}), # Пример без EventTypeID
        ("Routine maintenance check passed", LOG_LEVEL_IDS["DEBUG"], None, False, {"check_module": "dispenser_self_test"})
    ]

    chosen_event = random.choice(possible_events)
    message_base, log_level_id, event_type_id, is_alert, payload_data = chosen_event
    
    message = f"{message_base} (ATM_ID: {ATM_ID_IN_DB})"
    if payload_data:
        # Добавляем немного вариативности в payload, если он есть
        payload_data["timestamp_details"] = {"sec": datetime.now().second, "ms": datetime.now().microsecond // 1000}
        
    log_data = {
        "event_timestamp": now_utc_iso,
        "message": message,
        "log_level_id": log_level_id, # Обязательное поле
        "is_alert": is_alert,
        "payload": payload_data # Может быть None
    }

    # event_type_id является Optional[int] в ATMLogCreate, поэтому добавляем, только если он есть
    if event_type_id is not None:
        log_data["event_type_id"] = event_type_id
    
    return log_data

def send_log(log_data):
    """Отправляет данные лога на API."""
    headers = {}
    if SIMULATOR_API_KEY:
        headers["X-API-Key"] = SIMULATOR_API_KEY
    
    # Отладочный вывод перед отправкой
    # print(f"ATM {ATM_ID_IN_DB}: Preparing to send log. Endpoint: {LOG_ENDPOINT}")
    # print(f"ATM {ATM_ID_IN_DB}: Headers: {json.dumps(list(headers.keys())) if headers else 'No Headers'}")
    # print(f"ATM {ATM_ID_IN_DB}: Payload: {json.dumps(log_data, indent=2)}")

    try:
        response = requests.post(LOG_ENDPOINT, json=log_data, headers=headers, timeout=15) # Увеличил таймаут
        if response.status_code == 201:
            print(f"ATM {ATM_ID_IN_DB}: Log sent successfully: \"{log_data['message'][:70]}...\"")
        else:
            print(f"ATM {ATM_ID_IN_DB}: Failed to send log. Status: {response.status_code}, Response: {response.text}")
    except requests.exceptions.Timeout:
        print(f"ATM {ATM_ID_IN_DB}: Error sending log: Request timed out after 15 seconds.")
    except requests.exceptions.ConnectionError:
        print(f"ATM {ATM_ID_IN_DB}: Error sending log: Connection error. Is the backend running at {API_BASE_URL}?")
    except requests.exceptions.RequestException as e:
        print(f"ATM {ATM_ID_IN_DB}: Error sending log: {e}")

# --- Основной цикл симулятора ---
if __name__ == "__main__":
    print(f"ATM Simulator {ATM_ID_IN_DB} starting...")
    print(f"Target API Base URL: {API_BASE_URL}")
    print(f"Target Log Endpoint: {LOG_ENDPOINT}")
    print(f"API Key in use: {'Yes' if SIMULATOR_API_KEY else 'No (WARNING: requests might be unauthorized)'}")

    # Проверка, что все ID из справочников не None (важно для избежания ошибок)
    if not all(val is not None for val in LOG_LEVEL_IDS.values()):
        print("CRITICAL ERROR: One or more LogLevel IDs are not defined correctly in LOG_LEVEL_IDS.")
        exit(1)
    # Для EVENT_TYPE_IDS такая проверка не нужна, так как мы можем отправлять None

    print("-" * 30)

    while True:
        try:
            log_entry = generate_log_entry()
            send_log(log_entry)
            sleep_duration = random.uniform(15, 60)  # Интервал между логами
            print(f"ATM {ATM_ID_IN_DB}: Next log in {sleep_duration:.1f} seconds.")
            time.sleep(sleep_duration)
        except KeyboardInterrupt:
            print(f"\nATM Simulator {ATM_ID_IN_DB} stopping...")
            break
        except Exception as e:
            print(f"ATM {ATM_ID_IN_DB}: An unexpected error occurred in the main loop: {e}")
            print(f"ATM {ATM_ID_IN_DB}: Restarting loop after 10 seconds...")
            time.sleep(10)