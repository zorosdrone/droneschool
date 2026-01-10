from pymavlink import mavutil
import time

# 接続
# ""tcp:172.30.96.1:5762"",
# ""tcp:172.30.96.1:5772"",
# ""tcp:172.30.96.1:5782"",

master: mavutil.mavfile = mavutil.mavlink_connection(
    # "127.0.0.1:14551",  source_system=1, source_component=90)
    "tcp:172.30.96.1:5762",  source_system=1, source_component=90)

master.wait_heartbeat()
print("接続完了")

# GUIDEDにモード変更
mode = 'GUIDED'
master.set_mode_apm(master.mode_mapping()[mode])

# モード変更を確認
while True:
    if master.flightmode == mode:
        break
    master.recv_msg()
print("モード変更完了")

# アーム
master.arducopter_arm()
master.motors_armed_wait()
print("アーム完了")

# 目標地点　35.879768, 140.348495
# 下記は初期位置
# target_lat = 35.876991
# target_lon = 140.348026
target_lat = 35.879768
target_lon = 140.348495

# 移動コマンド送信
master.mav.set_position_target_global_int_send(
    0,
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
    0b0000111111111000,
    int(target_lat * 1e7), int(target_lon * 1e7), 0,
    0, 0, 0, 0, 0, 0, 0, 0)

# メッセージレート変更: GLOBAL_POSITION_INT(33)を10Hzで受信
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
    0, 33, 100000, 0, 0, 0, 0, 0)

# GLOBAL_POSITION_INT メッセージを要求
# master.mav.global_position_int_send(0, 0, 0, 0, 0, 0, 0, 0, 0)

# 目標地点への到達を確認
while True:
    # GLOBAL_POSITION_INT から位置を取得
    recieved_msg = master.recv_match(
        type='GLOBAL_POSITION_INT', blocking=True)
    current_lat = recieved_msg.lat / 1e7
    current_lon = recieved_msg.lon / 1e7

    print(f"現在地: lat={current_lat}, lon={current_lon}")

    if abs(current_lat - target_lat) < 0.00001 and abs(current_lon - target_lon) < 0.00001:
        print("目標地点に到達")
        break

    time.sleep(0.1)

# 切断
master.close()
