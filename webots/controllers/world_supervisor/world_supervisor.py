from controller import Supervisor
import random, math

ROCK_COUNT = 40
AREA = 16.0        # total square side (±8m)
SAFE_RADIUS = 2.0  # avoid spawning right on top of the rover

def rock_node(def_name, x, z, rot, scale, r, g, b):
    y = scale * 0.25  # Half the box height to sit on ground
    size = scale * 0.5
    return f'''DEF {def_name} Solid {{
  translation {x} {y} {z}
  rotation 0 1 0 {rot}
  children [
    Shape {{
      appearance PBRAppearance {{
        baseColor {r} {g} {b}
        roughness 1
        metalness 0
      }}
      geometry Box {{
        size {size} {size*0.5} {size}
      }}
    }}
  ]
  name "{def_name}"
  boundingObject Box {{
    size {size} {size*0.5} {size}
  }}
}}'''

def main():
    sup = Supervisor()
    timestep = int(sup.getBasicTimeStep())
    root = sup.getRoot()
    children = root.getField('children')

    # Remove previously spawned rocks
    for i in reversed(range(children.getCount())):
        node = children.getMFNode(i)
        try:
            def_name = node.getDef()
        except Exception:
            def_name = None
        if def_name and def_name.startswith('HAZ_ROCK_'):
            children.removeMF(i)

    # Spawn new rocks
    for idx in range(ROCK_COUNT):
        # pick a safe position away from the start
        while True:
            x = random.uniform(-AREA/2, AREA/2)
            z = random.uniform(-AREA/2, AREA/2)
            if math.hypot(x, z) > SAFE_RADIUS:
                break
        rot = random.uniform(0, math.pi * 2)
        scale = random.uniform(0.4, 1.2)
        r, g, b = 0.8, 0.35 + random.uniform(-0.05, 0.05), 0.3
        def_name = f'HAZ_ROCK_{idx}'
        children.importMFNodeFromString(-1, rock_node(def_name, x, z, rot, scale, r, g, b))

    print(f"[supervisor] spawned {ROCK_COUNT} rocks")

    while sup.step(timestep) != -1:
        pass

if __name__ == "__main__":
    main()
