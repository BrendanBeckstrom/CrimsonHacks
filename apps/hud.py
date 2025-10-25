import os, socket, struct, time
import numpy as np
import streamlit as st
from ai.perception.seg_stub import obstacle_risk

HOST = os.getenv('ROVER_HOST', '127.0.0.1')
PORT = int(os.getenv('ROVER_PORT', '5555'))

@st.cache_resource
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    return s

def send(sock, cmd:str):
    payload = cmd.encode('utf-8')
    sock.sendall(len(payload).to_bytes(4, 'big') + payload)

def get_frame(sock):
    send(sock, 'GET_FRAME')
    hdr = sock.recv(12)
    h = int.from_bytes(hdr[0:4],'big')
    w = int.from_bytes(hdr[4:8],'big')
    c = int.from_bytes(hdr[8:12],'big')
    buf = b''
    n = h*w*c
    while len(buf) < n:
        buf += sock.recv(n-len(buf))
    arr = np.frombuffer(buf, dtype=np.uint8).reshape((h,w,c))
    return arr

st.set_page_config(layout="wide")
sock = connect()
col1, col2 = st.columns(2)
frame_slot = col1.empty()
mask_slot = col2.empty()

while True:
    frame = get_frame(sock)
    l,c,r = obstacle_risk(frame)
    frame_slot.image(frame[:,:,::-1], caption=f"Camera — risk L/C/R: {l:.2f}/{c:.2f}/{r:.2f}", channels='BGR')
    # simple bar viz
    mask_slot.bar_chart({'risk':[l,c,r]})
    time.sleep(0.05)
