import os, socket, struct, time, argparse
import pygame

HOST = os.getenv('ROVER_HOST', '127.0.0.1')
PORT = int(os.getenv('ROVER_PORT', '5555'))

parser = argparse.ArgumentParser()
parser.add_argument('--latency_ms', type=int, default=0)
args = parser.parse_args()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

def send(cmd:str):
    payload = cmd.encode('utf-8')
    s.sendall(struct.pack('!I', len(payload)) + payload)

pygame.init()
screen = pygame.display.set_mode((400, 200))
clock = pygame.time.Clock()

vel_map = {
    'STOP': (0.0, 0.0),
    'FWD': (2.5, 2.5),
    'LEFT': (0.5, 2.0),
    'RIGHT': (2.0, 0.5),
    'HARD_LEFT': (-3.0, 3.0),
    'HARD_RIGHT': (3.0, -3.0),
}

current = 'STOP'
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w): current = 'FWD'
            elif event.key in (pygame.K_LEFT, pygame.K_a): current = 'LEFT'
            elif event.key in (pygame.K_RIGHT, pygame.K_d): current = 'RIGHT'
            elif event.key in (pygame.K_q,): current = 'HARD_LEFT'
            elif event.key in (pygame.K_e,): current = 'HARD_RIGHT'
            elif event.key in (pygame.K_SPACE, pygame.K_DOWN, pygame.K_s): current = 'STOP'
            elif event.key in (pygame.K_ESCAPE, pygame.K_x): running = False
    vl, vr = vel_map[current]
    if args.latency_ms > 0:
        time.sleep(args.latency_ms/1000)
    send(f"SET_V {vl} {vr}")
    clock.tick(20)

pygame.quit()
