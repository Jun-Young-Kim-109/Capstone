#video_recorder.py
import cv2
import pygame
import sys
from threading import Thread
import time
import datetime
import obd

class VideoCaptureThread(Thread):
    def __init__(self, src=0, width=800, height=480):
        super(VideoCaptureThread, self).__init__()
        self.cap = cv2.VideoCapture(src)
        if not self.cap.isOpened():
            print("Error: Camera is not opened.")
            sys.exit(1)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.frame = None
        self.running = True

    def run(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame

    def stop(self):
        self.running = False
        self.cap.release()

class VideoRecorderThread(Thread):
    def __init__(self, obd_connection, obd_connected, src=0, frame_rate=15, width=800, height=480):
        super(VideoRecorderThread, self).__init__()
        self.obd_connection = obd_connection
        self.obd_connected = obd_connected
        self.src = src
        self.frame_rate = frame_rate
        self.width = width
        self.height = height
        self.running = True

    def run(self):
        video_recorder_main(self.obd_connection, self.obd_connected, self.src, self.frame_rate, self.width, self.height)

    def stop(self):
        self.running = False
    
def add_info_to_frame(frame, fps, obd_error_shown, obd_connected, obd_connection):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(frame, current_time, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(frame, f"FPS: {fps}", (500, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    speed_text = rpm_text = throttle_text = load_text = "N/A"

    if obd_connected and obd_connection.is_connected():
        try:
            speed_response = obd_connection.query(obd.commands.SPEED)
            rpm_response = obd_connection.query(obd.commands.RPM)
            throttle_response = obd_connection.query(obd.commands.THROTTLE_POS)
            load_response = obd_connection.query(obd.commands.ENGINE_LOAD)

            speed_text = f"{int(speed_response.value.to('km/h').magnitude)} km/h" if speed_response.value is not None else "N/A"
            rpm_text = f"{int(rpm_response.value.magnitude)} RPM" if rpm_response.value is not None else "N/A"
            throttle_text = f"{int(throttle_response.value.magnitude)}%" if throttle_response.value is not None else "N/A"
            load_text = f"{int(load_response.value.magnitude)}%" if load_response.value is not None else "N/A"
        except Exception as e:
            if not obd_error_shown:
                print(f"OBD-II error: {e}")
                obd_error_shown = True
    elif not obd_error_shown:
        print("OBD-II connection not established.")
        obd_error_shown = True
    
    cv2.putText(frame, f"Speed: {speed_text} RPM: {rpm_text} Throttle: {throttle_text} Load: {load_text}", (60, frame.shape[0]-50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    return frame, obd_error_shown

def video_recorder_main(obd_connection, obd_connected, src=0, frame_rate=15, width=800, height=480):

    pygame.init()
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    # "뒤로 가기" 버튼 이미지 불러오기 및 크기 조정
    back_button_image = pygame.image.load("/home/pi/Desktop/JUN/back_button.png")
    back_button_image = pygame.transform.scale(back_button_image, (50, 50))  # 크기 조정 예시
    back_button_rect = back_button_image.get_rect(topleft=(730, 40))  # 버튼 위치 설정
    video_thread = VideoCaptureThread(src, width, height)
    video_thread.start()

    recording = False
    out = None
    last_update_time = time.time()
    frame_count = 0
    fps = 0
    obd_error_shown = False

    while True:
        frame_count += 1
        current_time = time.time()
        if current_time - last_update_time >= 1:
            fps = frame_count
            frame_count = 0
            last_update_time = current_time

        if video_thread.frame is not None:
            frame = video_thread.frame.copy()
            frame, obd_error_shown = add_info_to_frame(frame, fps, obd_error_shown, obd_connected, obd_connection)  # OBD 정보를 프레임에 추가
            frame = cv2.resize(frame, (width, height))

            if recording:
                if out is None:
                    current_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                    video_filename = f"{current_time_str}.avi"
                    out = cv2.VideoWriter(video_filename, cv2.VideoWriter_fourcc(*'XVID'), frame_rate, (width, height))
                out.write(frame)
            elif out is not None:
                out.release()
                out = None

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            screen.blit(frame, (0, 0))
            screen.blit(back_button_image, back_button_rect)
            pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if recording and out:
                    out.release()
                video_thread.stop()
                pygame.quit()
                sys.exit(0)
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button_rect.collidepoint(event.pos):
                    # "뒤로 가기" 버튼 클릭 시
                    if recording and out:
                        out.release()  # 녹화 중단 및 저장
                    video_thread.stop()
                    return  # 메인 화면으로 돌아가기
                    
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    recording = not recording
                    if recording:
                        current_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                        video_filename = f"{current_time_str}.avi"
                        out = cv2.VideoWriter(video_filename, cv2.VideoWriter_fourcc(*'XVID'), frame_rate, (width, height))
                    else:
                        if out:
                            out.release()
                            out = None
                elif event.key == pygame.K_q:
                    if recording and out:
                        out.release()
                    video_thread.stop()
                    pygame.quit()
                    sys.exit(0)

        clock.tick(frame_rate)

    video_thread.stop()
    if recording and out:
        out.release()
    pygame.quit()

        
if __name__ == "__main__":
    video_recorder_main(connection=obd_connection, src=0, frame_rate=15, width=800, height=480)
 
