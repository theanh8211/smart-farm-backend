# Chuyển toàn hệ thống sang chế độ tiết kiệm pin
GLOBAL_POWER_SAVE = False

def toggle_power_save():
    global GLOBAL_POWER_SAVE
    GLOBAL_POWER_SAVE = not GLOBAL_POWER_SAVE
    return {"power_save_mode": GLOBAL_POWER_SAVE}