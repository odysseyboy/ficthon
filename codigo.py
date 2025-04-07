import cv2
import mediapipe as mp
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Inicializa o controle de volume do Windows
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volume_range = volume.GetVolumeRange()  # Range típico: (-65.25, 0.0)

# Configurações do MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)  # Apenas 1 mão
mp_drawing = mp.solutions.drawing_utils

# Inicia a webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        continue

    # Converte BGR para RGB e processa
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Desenha os landmarks da mão
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Obtém a coordenada Y do dedo indicador (landmark 8)
            index_finger_y = hand_landmarks.landmark[8].y

            # Normaliza a posição Y para o volume (0% a 100%)
            min_y = 0.2  # Valor mínimo (dedo na parte inferior da tela)
            max_y = 0.8  # Valor máximo (dedo na parte superior)
            
            # Inverte o cálculo (quanto maior o Y, menor o volume)
            vol_percent = int(((max_y - index_finger_y) / (max_y - min_y)) * 100)
            vol_percent = max(0, min(100, vol_percent))  # Limita entre 0 e 100

            # Define o volume no sistema
            volume.SetMasterVolumeLevelScalar(vol_percent / 100, None)

            # Mostra o volume e a posição Y na tela
            cv2.putText(frame, f"Volume: {vol_percent}%", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Posicao Y: {index_finger_y:.2f}", (10, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    cv2.imshow("Controle de Volume por 1 Dedo", frame)
    if cv2.waitKey(5) & 0xFF == 27:  # ESC para sair
        break

cap.release()
cv2.destroyAllWindows()