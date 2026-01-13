from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np

from anywidget_glsl import uniform
from anywidget_glsl.widget import ToyGLSL


def _carve_maze(cells_w: int, cells_h: int, *, seed: int | None = None) -> np.ndarray:
    """
    Generate a perfect maze (single-path) using randomized DFS on a grid of
    cells (cells_w x cells_h). The resulting image has odd dimensions with
    1-pixel corridors and 1-pixel walls.

    Returns an RGBA uint8 image with channels:
      R: walls (255 = wall, 0 = empty)
      G: start (255 at start cell center)
      B: goal  (255 at goal cell center)
      A: 255
    """
    if cells_w < 2 or cells_h < 2:
        raise ValueError("cells_w and cells_h must be >= 2")

    rng = random.Random(seed)

    # Grid dimensions with walls between cells: size = 2*N + 1
    W = 2 * cells_w + 1
    H = 2 * cells_h + 1

    # Start fully walled
    grid = np.ones((H, W), dtype=np.uint8) * 255

    # Helper: carve a cell and the wall between
    def carve(cx: int, cy: int, nx: int, ny: int) -> None:
        x0, y0 = 2 * cx + 1, 2 * cy + 1
        x1, y1 = 2 * nx + 1, 2 * ny + 1
        grid[y0, x0] = 0
        grid[y1, x1] = 0
        wx, wy = (x0 + x1) // 2, (y0 + y1) // 2
        grid[wy, wx] = 0

    # Randomized DFS
    stack: list[tuple[int, int]] = []
    visited = np.zeros((cells_h, cells_w), dtype=bool)
    sx, sy = 0, 0
    ex, ey = cells_w - 1, cells_h - 1
    stack.append((sx, sy))
    visited[sy, sx] = True

    while stack:
        cx, cy = stack[-1]
        neighbors: list[tuple[int, int]] = []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < cells_w and 0 <= ny < cells_h and not visited[ny, nx]:
                neighbors.append((nx, ny))
        if not neighbors:
            stack.pop()
            continue
        nx, ny = rng.choice(neighbors)
        carve(cx, cy, nx, ny)
        visited[ny, nx] = True
        stack.append((nx, ny))

    # Ensure cell centers are open
    for cy in range(cells_h):
        for cx in range(cells_w):
            grid[2 * cy + 1, 2 * cx + 1] = 0

    # Start/goal marks
    start_px = (2 * sx + 1, 2 * sy + 1)
    goal_px = (2 * ex + 1, 2 * ey + 1)

    rgba = np.zeros((H, W, 4), dtype=np.uint8)
    rgba[..., 0] = grid  # walls in R
    rgba[..., 1] = 0
    rgba[..., 2] = 0
    rgba[..., 3] = 255
    rgba[start_px[1], start_px[0], 1] = 255
    rgba[goal_px[1], goal_px[0], 2] = 255
    return rgba


@dataclass
class MazeConfig:
    cells_w: int = 32
    cells_h: int = 18
    seed: int | None = None


class MazeSolver(ToyGLSL):
    """
    GPU BFS-style maze exploration demo built with ToyGLSL.

    Uniforms:
      - maze: sampler2D with R=walls(255), G=start(255), B=goal(255)

    Passes:
      1) Solve: backbuffer iteration flood-filling from start (stores visited,
         approximate distance, and goal-reached flag).
      2) Present: visualize walls, frontier, visited heat, start/goal.
    """

    time: bool = True
    mouse: bool = False
    keyboard: bool = False

    # Input maze texture (required)
    maze = uniform.Texture2D().tag(sync=True)

    class Solve(ToyGLSL):
        time: bool = True
        backbuffer: bool = True
        _glsl = r"""
        // Output encodes: R=visited, G=distance (0..1 approx), B=goalReached
        void mainImage(out vec4 fragColor, in vec2 fragCoord){
          vec2 uv = fragCoord / iResolution.xy;
          vec4 mazePix = texture(maze, uv);
          bool wall  = mazePix.r > 0.5;
          bool start = mazePix.g > 0.5;
          bool goal  = mazePix.b > 0.5;

          vec4 prev = texture(iBackbuffer, uv);
          float visited_prev = prev.r;
          float dist_prev = prev.g;
          float goal_prev = prev.b;

          // First frame: initialize state
          if (iFrame <= 1) {
            // Initialize: only start is visited
            float v = start ? 1.0 : 0.0;
            float d = 0.0;
            float g = 0.0;
            fragColor = vec4(v, d, g, 1.0);
            return;
          }

          float visited = visited_prev;
          float dist = dist_prev;

          if (visited_prev < 0.5 && !wall) {
            vec2 px = 1.0 / iResolution.xy;
            float vn = texture(iBackbuffer, uv + vec2( 0.0, -px.y)).r;
            float vs = texture(iBackbuffer, uv + vec2( 0.0,  px.y)).r;
            float ve = texture(iBackbuffer, uv + vec2(  px.x, 0.0)).r;
            float vw = texture(iBackbuffer, uv + vec2(-px.x, 0.0)).r;
            float any_neigh = max(max(vn, vs), max(ve, vw));
            if (any_neigh > 0.5) {
              visited = 1.0;
              float dn = texture(iBackbuffer, uv + vec2( 0.0, -px.y)).g;
              float ds = texture(iBackbuffer, uv + vec2( 0.0,  px.y)).g;
              float de = texture(iBackbuffer, uv + vec2(  px.x, 0.0)).g;
              float dw = texture(iBackbuffer, uv + vec2(-px.x, 0.0)).g;
              float mind = min(min(dn, ds), min(de, dw));
              dist = mind + (1.0/255.0);
            }
          }

          float goalReached = goal_prev;
          if (goal && visited > 0.5) goalReached = 1.0;
          fragColor = vec4(visited, dist, goalReached, 1.0);
        }
        """

    class Present(ToyGLSL):
        time: bool = True
        _glsl = r"""
        vec3 heatmap(float t){
          // simple blue->cyan->yellow->red ramp
          t = clamp(t, 0.0, 1.0);
          return clamp(vec3(3.0*t-1.5, 2.0*t, -3.0*t+1.5), 0.0, 1.0);
        }
        void mainImage(out vec4 fragColor, in vec2 fragCoord){
          vec2 uv = fragCoord / iResolution.xy;
          vec4 mazePix = texture(maze, uv);
          bool wall  = mazePix.r > 0.5;
          bool start = mazePix.g > 0.5;
          bool goal  = mazePix.b > 0.5;

          vec4 s = texture(iPrevPass, uv);
          float visited = s.r;
          float dist = s.g;
          float goalReached = s.b;

          vec3 col = vec3(0.1);
          if (wall) col = vec3(0.05);
          else if (visited > 0.5) col = 0.15 + 0.85*heatmap(dist);
          else col = vec3(0.2);

          // Frontier highlight: visited and has an unvisited neighbor
          if (!wall && visited > 0.5) {
            vec2 px = 1.0 / iResolution.xy;
            float vn = texture(iPrevPass, uv + vec2(0.0, -px.y)).r;
            float vs = texture(iPrevPass, uv + vec2(0.0,  px.y)).r;
            float ve = texture(iPrevPass, uv + vec2( px.x, 0.0)).r;
            float vw = texture(iPrevPass, uv + vec2(-px.x, 0.0)).r;
            float unvisited_near = 1.0 - min(min(vn, vs), min(ve, vw));
            if (unvisited_near > 0.5) col = mix(col, vec3(0.1, 1.0, 0.4), 0.7);
          }

          if (start) col = vec3(0.2, 0.8, 1.0);
          if (goal)  col = mix(col, vec3(1.0, 0.2, 0.4), 0.9);
          if (goalReached > 0.5) col = mix(col, vec3(1.0, 1.0, 1.0), 0.3);

          fragColor = vec4(col, 1.0);
        }
        """

    # Pass order
    _buffers = (Solve, Present)

    def __init__(
        self,
        *,
        config: MazeConfig | None = None,
        width: int | None = None,
        height: int | None = None,
        seed: int | None = None,
        **kwargs,
    ):
        """
        Create a maze solver widget.

        - config: MazeConfig(cells_w, cells_h, seed) determines maze size.
        - width/height: canvas size in CSS pixels (optional).
        - seed: overrides MazeConfig.seed for reproducibility.
        """
        cfg = config or MazeConfig()
        if seed is not None:
            cfg = MazeConfig(cells_w=cfg.cells_w, cells_h=cfg.cells_h, seed=seed)
        # Generate maze texture
        tex = _carve_maze(cfg.cells_w, cfg.cells_h, seed=cfg.seed)
        self.maze = tex
        # Default canvas size to the maze texture's pixel dimensions
        h, w = tex.shape[:2]
        if width is None:
            kwargs["width"] = w
        if height is None:
            kwargs["height"] = h
        super().__init__(**kwargs)
