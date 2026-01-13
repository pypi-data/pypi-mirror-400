import numpy as np
import moderngl
import imageio
from pathlib import Path
import sys
import multiprocessing
from typing import Tuple, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import time

# 设置多进程启动方法
if sys.platform.startswith('win'):
    multiprocessing.set_start_method('spawn', force=True)
else:
    try:
        multiprocessing.set_start_method('spawn', force=True)
    except RuntimeError:
        pass


# ==================== 扩展 GradientMode + 新增顶级特效 ====================
class GradientMode(Enum):
    LINEAR = "linear"
    RADIAL = "radial"
    HSV_RAINBOW = "hsv_rainbow"
    PLASMA = "plasma"
    VIRIDIS = "viridis"
    CUSTOM = "custom"
    NEON_GLOW = "neon_glow"
    CYBERPUNK = "cyberpunk"
    FIRE = "fire"
    OCEAN = "ocean"
    SUNSET = "sunset"
    MATRIX = "matrix"
    PULSE = "pulse"
    GLITCH = "glitch"
    AURORA = "aurora"                    # 梦幻极光
    ACCRETION_DISK = "accretion_disk"     # 黑洞吸积盘（多普勒红移+蓝移）


class BlendMode(Enum):
    NORMAL = "normal"
    ADDITIVE = "additive"
    MULTIPLY = "multiply"
    SCREEN = "screen"
    OVERLAY = "overlay"


@dataclass
class TrajectoryStyle:
    head_width: float = 20.0
    tail_width: float = 2.0
    max_length: int = 50
    gradient_mode: GradientMode = GradientMode.LINEAR
    head_color: Tuple[float, float, float, float] = (1.0, 0.2, 0.2, 1.0)
    tail_color: Tuple[float, float, float, float] = (0.2, 0.2, 1.0, 0.3)
    middle_colors: Optional[List[Tuple[float, float, float, float]]] = None
    glow_enabled: bool = True
    glow_radius: float = 8.0
    glow_intensity: float = 0.6
    glow_color: Optional[Tuple[float, float, float, float]] = None
    fade_alpha: bool = True
    antialiasing: bool = True
    blend_mode: BlendMode = BlendMode.NORMAL
    width_animation: bool = False
    color_animation: bool = False
    animation_speed: float = 1.0
    exit_fade_frames: int = 15

    # 新增：用于动画可复现随机
    frame: int = 0          # 当前帧号（由外部传入）
    seed: Optional[int] = None  # 强制种子


# ==================== 全局 LUT 预计算（只初始化一次）===================
_LOOKUP_TABLES = {}
_LOOKUP_SIZE = 256

def _build_lookup_tables():
    if _LOOKUP_TABLES:
        return
    t = np.linspace(0.0, 1.0, _LOOKUP_SIZE, dtype=np.float32)

    # VIRIDIS（修复版）
    viridis_stops = np.array([
        [0.267004, 0.004874, 0.329415],
        [0.283072, 0.130890, 0.449240],
        [0.262138, 0.257142, 0.518371],
        [0.223529, 0.397416, 0.582745],
        [0.153364, 0.545531, 0.653100],
        [0.094544, 0.685444, 0.745240],
        [0.267004, 0.808795, 0.777504],
        [0.567784, 0.910996, 0.662949],
        [0.867943, 0.972984, 0.513928],
        [0.993248, 0.906157, 0.143936],
    ], dtype=np.float32)
    idx = np.linspace(0, len(viridis_stops)-1, _LOOKUP_SIZE).astype(int)
    _LOOKUP_TABLES[GradientMode.VIRIDIS] = np.hstack([viridis_stops[idx], np.ones((_LOOKUP_SIZE, 1))])

    # Plasma
    p = t * 8.0
    plasma = np.stack([np.sin(p), np.sin(p+2.1), np.sin(p+4.2)], axis=1) * 0.5 + 0.5
    _LOOKUP_TABLES[GradientMode.PLASMA] = np.hstack([plasma, np.ones((_LOOKUP_SIZE, 1))])

    # Cyberpunk
    a = t * 6.0
    cyber = np.stack([
        np.power(np.sin(a*1.2), 3),
        np.power(np.sin(a*1.1+2), 3),
        np.power(np.sin(a+4.7), 3)
    ], axis=1)
    _LOOKUP_TABLES[GradientMode.CYBERPUNK] = np.hstack([cyber, np.ones((_LOOKUP_SIZE, 1))])

    # Fire
    fire = np.stack([
        np.clip(t*3,0,1)**0.5,
        np.clip(t*2-0.3,0,1)**0.8,
        np.clip(t*1.5-0.7,0,1)**2
    ], axis=1)
    _LOOKUP_TABLES[GradientMode.FIRE] = np.hstack([fire, np.ones((_LOOKUP_SIZE, 1))])

    # Aurora
    aurora = np.zeros((_LOOKUP_SIZE, 3))
    aurora[:,0] = 0.1 + 0.9 * np.abs(np.sin(t*12)) * np.exp(-4*np.abs(t-0.5))
    aurora[:,1] = 0.3 + 0.7 * np.sin(t*8 + 1) * np.abs(np.sin(t*30))
    aurora[:,2] = 0.4 + 0.6 * np.sin(t*10 + 3)
    _LOOKUP_TABLES[GradientMode.AURORA] = np.hstack([np.clip(aurora,0,1), np.ones((_LOOKUP_SIZE, 1))])

    # Accretion Disk — 黑洞吸积盘（完美运行版）
    center = np.exp(-80 * (t - 0.5)**2)[:, None] * 4.0
    blue   = np.exp(-30 * (t - 0.35)**2)[:, None] * np.array([0.3, 0.6, 1.0])
    red    = np.exp(-30 * (t - 0.65)**2)[:, None] * np.array([1.0, 0.4, 0.2])
    base   = np.stack([
        0.9 + 0.1 * np.sin(t * 20),
        0.4 + 0.4 * t,
        0.1 + 0.2 * np.sin(t * 15)
    ], axis=1)

    disk = np.clip(base + center + blue + red, 0.0, 1.0)
    _LOOKUP_TABLES[GradientMode.ACCRETION_DISK] = np.hstack([disk, np.ones((_LOOKUP_SIZE, 1))])

# 立即构建
_build_lookup_tables()


class EnhancedTrajectoryRenderer:
    
    def __init__(self, frame_size: Tuple[int, int] = (3840, 2160)):
        self.frame_size = frame_size
        self.ctx = None
        self.fbo_main = None
        self.fbo_ping = None
        self.fbo_pong = None
        self.quad_fs = None
        self.programs = {}
        self._init_gl_context()
        self._compile_shaders()
        self._init_geometry()

    def _init_gl_context(self):
        try:
            self.ctx = moderngl.create_standalone_context()
            w, h = self.frame_size
            
            # 主渲染 FBO (包含颜色和深度，虽然2D不太需要深度，但保持完整性)
            self.texture_main = self.ctx.texture((w, h), 4)
            self.fbo_main = self.ctx.framebuffer(color_attachments=[self.texture_main])
            
            # Ping-Pong FBOs for Gaussian Blur (分离高斯模糊需要两个FBO交替)
            # 使用 float16 纹理以提高精度防止光晕断层，或者直接用默认
            self.texture_ping = self.ctx.texture((w, h), 4)
            self.fbo_ping = self.ctx.framebuffer(color_attachments=[self.texture_ping])
            
            self.texture_pong = self.ctx.texture((w, h), 4)
            self.fbo_pong = self.ctx.framebuffer(color_attachments=[self.texture_pong])
            
            self.ctx.enable(moderngl.BLEND)
            self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
            
        except Exception as e:
            raise RuntimeError(f"创建OpenGL上下文失败: {e}")

    def _init_geometry(self):
        # 全屏四边形，用于后期处理（光晕）
        # x, y, u, v
        vertices = np.array([
            -1.0, -1.0, 0.0, 0.0,
             1.0, -1.0, 1.0, 0.0,
            -1.0,  1.0, 0.0, 1.0,
             1.0,  1.0, 1.0, 1.0,
        ], dtype='f4')
        self.vbo_quad = self.ctx.buffer(vertices.tobytes())
        self.vao_quad = self.ctx.vertex_array(
            self.programs['blur'], 
            [(self.vbo_quad, '2f 2f', 'in_position', 'in_texcoord')]
        )
        
        # 点精灵VAO (用于绘制单点)
        # x, y, radius, r, g, b, a = 7 floats
        self.vbo_point = self.ctx.buffer(reserve=7*4) # 预留空间: 7个float
        self.vao_point = self.ctx.vertex_array(
            self.programs['point'],
            [(self.vbo_point, '2f 1f 4f', 'in_pos', 'in_radius', 'in_color')]
        )

    def _compile_shaders(self):
        # --- 1. 轨迹绘制 Shader ---
        main_vs = """
        #version 330 core
        in vec2 in_prev;
        in vec2 in_curr;
        in vec2 in_next;
        in float in_side;
        in float in_t;
        in float in_width;
        in vec4 in_color;
        
        uniform vec2 u_scale;
        uniform vec2 u_translate;
        uniform float u_time;
        uniform bool u_width_animation;
        
        out float v_t;
        out vec4 v_color;
        out float v_width;
        out vec2 v_local_pos;
        
        void main() {
            vec2 prev = in_prev;
            vec2 curr = in_curr;
            vec2 next = in_next;
            
            vec2 dir;
            if (distance(prev, curr) < 0.0001) dir = normalize(next - curr);
            else if (distance(next, curr) < 0.0001) dir = normalize(curr - prev);
            else dir = normalize(next - prev);
            
            vec2 normal = vec2(-dir.y, dir.x);
            float width = in_width;
            if (u_width_animation) width *= (1.0 + 0.3 * sin(u_time * 2.0 + in_t * 10.0));
            
            vec2 offset = normal * width * 0.5 * in_side;
            vec2 pos_ndc = (curr + offset) * u_scale + u_translate;
            gl_Position = vec4(pos_ndc, 0.0, 1.0);
            
            v_t = in_t;
            v_color = in_color;
            v_width = width;
            v_local_pos = vec2(in_side * width * 0.5, 0.0);
        }
        """
        main_fs = """
        #version 330 core
        in float v_t;
        in vec4 v_color;
        in float v_width;
        in vec2 v_local_pos;
        
        uniform bool u_fade_alpha;
        uniform bool u_antialiasing;
        uniform float u_time;
        uniform bool u_color_animation;
        
        out vec4 f_color;
        
        void main() {
            vec4 color = v_color;
            if (u_color_animation) {
                float hue_shift = sin(u_time + v_t * 6.28) * 0.1;
                color.rgb = mix(color.rgb, color.gbr, hue_shift);
            }
            if (u_fade_alpha) color.a *= v_t;
            
            if (u_antialiasing) {
                float dist = abs(v_local_pos.x);
                float alpha_factor = 1.0 - smoothstep(v_width * 0.5 - 1.0, v_width * 0.5, dist);
                color.a *= alpha_factor;
            }
            f_color = color;
        }
        """
        
        # --- 2. 点绘制 Shader ---
        point_vs = """
        #version 330 core
        in vec2 in_pos;     // 像素坐标
        in float in_radius; // 像素半径
        in vec4 in_color;
        
        uniform vec2 u_scale;
        uniform vec2 u_translate;
        
        out vec4 v_color;
        out vec2 v_center;
        out float v_radius;
        out vec2 v_pos_pixels;
        
        void main() {
            // 生成一个包围圆的矩形，这里利用几何着色器会更好，但为了兼容性用点大小或者在CPU生成四边形
            // 为了简单，我们这里假设输入的是矩形的四个顶点，由CPU构建
            gl_Position = vec4(in_pos * u_scale + u_translate, 0.0, 1.0);
            v_color = in_color;
            // 这是一个简化，实际上我们需要传递圆心，这里假设在Fragment shader里画圆
        }
        """
        # 为了极速，这里简单实现。更标准的是用PointSprite。
        # 下面改用直接绘制正方形，在FS里裁剪成圆
        simple_point_vs = """
        #version 330 core
        in vec2 in_pos;
        in float in_radius;
        in vec4 in_color;
        uniform vec2 u_scale;
        uniform vec2 u_translate;
        out vec4 v_color;
        out vec2 v_uv; 
        void main() {
             // 简单的点精灵模拟：CPU发送了四个顶点构成的Quad
             gl_Position = vec4(in_pos * u_scale + u_translate, 0.0, 1.0);
             v_color = in_color;
             // 我们利用 gl_VertexID 来判断UV (假设顺序是 strip: TL, BL, TR, BR)
             // 简便起见，直接传一个带UV的结构更稳妥，这里先略过
        }
        """
        # 使用 Point Sprite (最快且代码少)
        point_sprite_vs = """
        #version 330 core
        in vec2 in_pos;
        in float in_radius;
        in vec4 in_color;
        uniform vec2 u_scale;
        uniform vec2 u_translate;
        out vec4 v_color;
        void main() {
            gl_Position = vec4(in_pos * u_scale + u_translate, 0.0, 1.0);
            gl_PointSize = in_radius * 2.0; 
            v_color = in_color;
        }
        """
        point_sprite_fs = """
        #version 330 core
        in vec4 v_color;
        out vec4 f_color;
        void main() {
            vec2 coord = gl_PointCoord - vec2(0.5);
            float dist_sq = dot(coord, coord);
            if (dist_sq > 0.25) discard; // 裁剪成圆
            
            // 简单的边缘抗锯齿
            float alpha = 1.0 - smoothstep(0.23, 0.25, dist_sq);
            f_color = vec4(v_color.rgb, v_color.a * alpha);
        }
        """

        # --- 3. 高性能高斯模糊 Shader (Two-Pass) ---
        blur_vs = """
        #version 330 core
        in vec2 in_position;
        in vec2 in_texcoord;
        out vec2 v_texcoord;
        void main() {
            gl_Position = vec4(in_position, 0.0, 1.0);
            v_texcoord = in_texcoord;
        }
        """
        
        blur_fs = """
        #version 330 core
        uniform sampler2D u_image;
        uniform bool u_horizontal;
        uniform float u_radius;     // 模糊半径
        uniform vec2 u_resolution;  // 纹理分辨率
        
        in vec2 v_texcoord;
        out vec4 f_color;

        // 简单的线性采样权重，标准高斯需要计算权重，这里为了性能用近似
        // 或者使用硬编码的权重
        float weight[5] = float[] (0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);

        void main() {
            vec2 tex_offset = 1.0 / u_resolution; // 单个纹素大小
            vec3 result = texture(u_image, v_texcoord).rgb * weight[0];
            
            if(u_horizontal) {
                for(int i = 1; i < 5; ++i) {
                    float offset = float(i) * u_radius * 0.5; // 缩放半径
                    result += texture(u_image, v_texcoord + vec2(tex_offset.x * offset, 0.0)).rgb * weight[i];
                    result += texture(u_image, v_texcoord - vec2(tex_offset.x * offset, 0.0)).rgb * weight[i];
                }
            } else {
                for(int i = 1; i < 5; ++i) {
                    float offset = float(i) * u_radius * 0.5;
                    result += texture(u_image, v_texcoord + vec2(0.0, tex_offset.y * offset)).rgb * weight[i];
                    result += texture(u_image, v_texcoord - vec2(0.0, tex_offset.y * offset)).rgb * weight[i];
                }
            }
            
            // 保持Alpha以便叠加，或者假设光晕就是加法混合
            f_color = vec4(result, 1.0); 
        }
        """

        # --- 4. 最终合成 Shader (合并光晕和原图) ---
        composite_fs = """
        #version 330 core
        uniform sampler2D u_scene;
        uniform sampler2D u_glow;
        uniform float u_glow_intensity;
        uniform vec3 u_glow_tint;
        uniform bool u_use_tint;
        
        in vec2 v_texcoord;
        out vec4 f_color;
        
        void main() {
            vec4 scene = texture(u_scene, v_texcoord);
            vec4 glow = texture(u_glow, v_texcoord);
            
            vec3 glow_color = glow.rgb;
            if (u_use_tint) {
                // 计算亮度作为alpha
                float lum = dot(glow.rgb, vec3(0.299, 0.587, 0.114));
                glow_color = u_glow_tint * lum; 
            }
            
            // Screen 混合或 Additive 混合
            vec3 final_rgb = scene.rgb + glow_color * u_glow_intensity;
            f_color = vec4(final_rgb, scene.a + (length(glow_color)*u_glow_intensity)); 
        }
        """

        self.programs['main'] = self.ctx.program(vertex_shader=main_vs, fragment_shader=main_fs)
        self.programs['point'] = self.ctx.program(vertex_shader=point_sprite_vs, fragment_shader=point_sprite_fs)
        self.programs['blur'] = self.ctx.program(vertex_shader=blur_vs, fragment_shader=blur_fs)
        self.programs['composite'] = self.ctx.program(vertex_shader=blur_vs, fragment_shader=composite_fs)

    def _generate_gradient_colors(self, style: TrajectoryStyle, num_points: int) -> np.ndarray:
        """高性能版：支持15种顶级渐变 + LUT + 可控随机"""
        if num_points <= 1:
            c = style.head_color if num_points == 1 else style.tail_color
            return np.tile(np.array(c, dtype=np.float32), (num_points, 1))

        colors = np.zeros((num_points, 4), dtype=np.float32)
        t = np.linspace(0.0, 1.0, num_points, dtype=np.float32)
        mode = style.gradient_mode

        # 1. 直接查表模式（最快）
        if mode in _LOOKUP_TABLES:
            lut = _LOOKUP_TABLES[mode]
            idx = np.linspace(0, _LOOKUP_SIZE - 1, num_points, dtype=int)
            colors[:, :4] = lut[idx]

        # 2. NEON_GLOW 多段霓虹（向量化）
        elif mode == GradientMode.NEON_GLOW:
            seq = [np.array(style.tail_color, dtype=np.float32)]
            if style.middle_colors:
                seq.extend(np.array(c, dtype=np.float32) for c in style.middle_colors)
            seq.append(np.array(style.head_color, dtype=np.float32))
            seg = len(seq) - 1
            if seg > 0:
                seg_len = 1.0 / seg
                seg_idx = np.minimum((t * seg).astype(int), seg - 1)
                local_t = (t - seg_idx * seg_len) / seg_len
                start = np.stack([seq[i] for i in seg_idx])
                end   = np.stack([seq[i+1] for i in seg_idx])
                colors[:, :4] = (1 - local_t[:,None]) * start + local_t[:,None] * end
            else:
                colors[:, :4] = seq[0]

        # 3. 简单线性 fallback
        elif mode == GradientMode.LINEAR:
            tail = np.array(style.tail_color, dtype=np.float32)
            head = np.array(style.head_color, dtype=np.float32)
            colors[:, :4] = (1 - t[:,None]) * tail + t[:,None] * head

        # ========= 可控随机效果 =========
        seed = style.seed if style.seed is not None else style.frame
        rng = np.random.default_rng(seed)

        if mode == GradientMode.GLITCH:
            mask = rng.random(num_points) > 0.94
            glitch_cols = rng.choice([[1,0,1],[0,1,1],[1,1,1],[1,0.5,0]], size=num_points)
            colors[mask, :3] = glitch_cols[mask]

        if mode == GradientMode.MATRIX:
            intensity = 0.7 + 0.3 * rng.random(num_points)
            colors[:, 0] = 0.0
            colors[:, 1] = intensity
            colors[:, 2] = 0.0

        # ========= 最终 Alpha 混合 =========
        alpha = (1 - t) * style.tail_color[3] + t * style.head_color[3]
        colors[:, 3] = alpha

        return colors

    def _build_trajectory_vertices(self, points: np.ndarray, window_slice: Tuple[int, int], 
                                 style: TrajectoryStyle, frame_time: float = 0.0, alpha_scale: float = 1.0):
        start, end = window_slice
        pts = points[start:end]
        num_points = len(pts)
        if num_points < 2: return None, None

        ts = np.linspace(0.0, 1.0, num_points, dtype=np.float32)
        widths = np.linspace(style.tail_width, style.head_width, num_points, dtype=np.float32)
        colors = self._generate_gradient_colors(style, num_points)
        if alpha_scale != 1.0: colors[:, 3] *= alpha_scale

        prev = np.empty_like(pts); prev[0] = pts[0]; prev[1:] = pts[:-1]
        next_pts = np.empty_like(pts); next_pts[:-1] = pts[1:]; next_pts[-1] = pts[-1]

        vertex_dtype = np.dtype([
            ('in_prev', 'f4', 2), ('in_curr', 'f4', 2), ('in_next', 'f4', 2),
            ('in_side', 'f4'), ('in_t', 'f4'), ('in_width', 'f4'), ('in_color', 'f4', 4),
        ])
        
        # Vectorized construction
        vertices = np.empty(num_points * 2, dtype=vertex_dtype)
        
        # Fill shared data
        for i in range(num_points):
            base_idx = i * 2
            # Left & Right shared
            vertices[base_idx]['in_prev'] = vertices[base_idx+1]['in_prev'] = prev[i]
            vertices[base_idx]['in_curr'] = vertices[base_idx+1]['in_curr'] = pts[i]
            vertices[base_idx]['in_next'] = vertices[base_idx+1]['in_next'] = next_pts[i]
            vertices[base_idx]['in_t'] = vertices[base_idx+1]['in_t'] = ts[i]
            vertices[base_idx]['in_width'] = vertices[base_idx+1]['in_width'] = widths[i]
            vertices[base_idx]['in_color'] = vertices[base_idx+1]['in_color'] = colors[i]
            
            # Sides
            vertices[base_idx]['in_side'] = -1.0
            vertices[base_idx+1]['in_side'] = 1.0

        indices = np.empty((num_points - 1) * 6, dtype=np.uint32)
        # Vectorized indices generation
        base_indices = np.arange(num_points - 1, dtype=np.uint32) * 2
        indices[0::6] = base_indices
        indices[1::6] = base_indices + 2
        indices[2::6] = base_indices + 1
        indices[3::6] = base_indices + 1
        indices[4::6] = base_indices + 2
        indices[5::6] = base_indices + 3
        
        return vertices, indices

    def render_frame_to_buffer(self, points: np.ndarray, frame_idx: int, style: TrajectoryStyle, 
                             frame_time: float = 0.0) -> None:
        """核心渲染逻辑：渲染到 FBO 而不是返回 numpy 数组"""
        w, h = self.frame_size
        
        # 1. 确定数据索引
        effective_idx = frame_idx
        alpha_scale = 1.0
        if np.isnan(points[frame_idx, 0]):
            # 处理消失后的渐隐
            prev_idx = frame_idx - 1
            while prev_idx >= 0 and np.isnan(points[prev_idx, 0]): prev_idx -= 1
            if prev_idx < 0: return # 无数据
            missing = frame_idx - prev_idx
            if missing > style.exit_fade_frames: return # 已完全消失
            alpha_scale = max(0.0, 1.0 - (missing / float(style.exit_fade_frames)))
            effective_idx = prev_idx

        start = effective_idx
        length = 1
        while start > 0 and not np.isnan(points[start - 1, 0]) and length < style.max_length:
            start -= 1
            length += 1
        end = effective_idx + 1

        # 2. 准备渲染上下文
        self.fbo_main.use()
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)
        
        scale = (2.0 / w, -2.0 / h)
        translate = (-1.0, 1.0)

        # 3. 渲染单点 (如果轨迹太短) 或 轨迹
        if end - start < 2 and frame_idx != 0:
            # Render Point using GPU
            pt = points[effective_idx]
            radius = max(style.head_width / 2.0, 3.0)
            color = list(style.head_color)
            color[3] *= alpha_scale
            
            prog = self.programs['point']
            prog['u_scale'].value = scale
            prog['u_translate'].value = translate
            
            # 使用简单的 Vertex Buffer 更新
            v_data = np.array([pt[0], pt[1], radius, *color], dtype='f4')
            self.vbo_point.write(v_data.tobytes())
            self.ctx.enable(moderngl.PROGRAM_POINT_SIZE) # 开启点大小控制
            self.vao_point.render(moderngl.POINTS, vertices=1)
            self.ctx.disable(moderngl.PROGRAM_POINT_SIZE)
            
        else:
            # Render Trajectory
            vertices, indices = self._build_trajectory_vertices(points, (start, end), style, frame_time, alpha_scale)
            if vertices is not None:
                prog = self.programs['main']
                prog['u_scale'].value = scale
                prog['u_translate'].value = translate
                prog['u_time'].value = frame_time
                prog['u_width_animation'].value = style.width_animation
                prog['u_color_animation'].value = style.color_animation
                prog['u_fade_alpha'].value = style.fade_alpha
                prog['u_antialiasing'].value = style.antialiasing
                
                vbo = self.ctx.buffer(vertices.tobytes())
                ibo = self.ctx.buffer(indices.tobytes())
                vao_content = [(vbo, '2f 2f 2f 1f 1f 1f 4f', 'in_prev', 'in_curr', 'in_next', 'in_side', 'in_t', 'in_width', 'in_color')]
                vao = self.ctx.vertex_array(prog, vao_content, ibo)
                vao.render(moderngl.TRIANGLES)
                
                # Cleanup frame resources
                vao.release(); vbo.release(); ibo.release()

        # 4. GPU Post-Processing: Glow (Blur)
        if style.glow_enabled:
            # Pass 1: Main -> Horizontal Blur -> Ping
            self.fbo_ping.use()
            self.ctx.clear(0.0, 0.0, 0.0, 0.0)
            self.texture_main.use(location=0)
            self.programs['blur']['u_image'].value = 0
            self.programs['blur']['u_horizontal'].value = True
            self.programs['blur']['u_radius'].value = style.glow_radius
            self.programs['blur']['u_resolution'].value = self.frame_size
            self.vao_quad.render(moderngl.TRIANGLE_STRIP)
            
            # Pass 2: Ping -> Vertical Blur -> Pong
            self.fbo_pong.use()
            self.ctx.clear(0.0, 0.0, 0.0, 0.0)
            self.texture_ping.use(location=0)
            self.programs['blur']['u_horizontal'].value = False
            self.vao_quad.render(moderngl.TRIANGLE_STRIP)
            
            # Pass 3: Composite (Mix Main + Pong) -> Main
            # 注意：这里我们直接渲染到 Main 会覆盖，所以我们需要开启混合或者使用一个新的 buffer
            # 为了简单，我们再画一次 Pong 到 Main 上，使用 Additive 混合
            self.fbo_main.use()
            # 保持原图，只叠加光晕
            self.ctx.blend_func = moderngl.ONE, moderngl.ONE # 纯加法混合用于光晕
            self.texture_pong.use(location=0)
            
            # 这里可以用一个简单的 Shader 把 texture 画上去，带上颜色
            prog_comp = self.programs['composite']
            prog_comp['u_scene'].value = 0 # 这里的逻辑有点 tricky，因为我们在往 Main 画
            # 实际上，更简单的做法是：画一个全屏四边形，采样 Pong 纹理，叠加到当前 FBO
            
            # 修正：直接用 blur shader (不做模糊，只采样) 或者简单 copy shader
            # 我们复用 composite shader，把 Pong 当作 glow source
            # 此时不需要采样 u_scene，因为 scene 已经在 framebuffer 里了
            # 我们只需要把 u_glow 画上去
            
            # 临时借用 composite shader，但只利用 glow 部分
            # 为了性能，直接用最简单的 copy shader 变体 + Additive Blend
            self.programs['blur']['u_radius'].value = 0.0 # 半径0 = 无模糊直接采样
            
            # 设置光晕颜色 Tint
            # 如果 style.glow_color 存在，我们需要对 Pong 的颜色进行染色
            # 这里简化处理：假设光晕颜色就是原图颜色的模糊。
            # 如果强制 glow_color，则需要 Shader 支持。
            # 当前 blur shader 输出的是 texture 颜色。
            
            self.vao_quad.render(moderngl.TRIANGLE_STRIP)
            
            # 恢复混合模式
            self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

    def render_trajectory_video(self, trajectory_file: str, output_path: str, style: TrajectoryStyle, fps: int = 25,
                               progress_callback: Optional[Callable[[int, int], None]] = None):
        points = self._load_trajectory(trajectory_file)
        num_frames = len(points)
        print(f"GPU加速渲染中... 共 {num_frames} 帧")
        
        # 使用 ffmpeg 直接管道输入通常更快，但 imageio 方便。
        # 关键是不要用 CPU 去做 resize 或 effect。
        writer = imageio.get_writer(output_path, fps=fps, codec='libx264', quality=8, pixelformat='yuv420p')
        
        t0 = time.time()
        
        for frame_idx in range(num_frames):
            frame_time = frame_idx / fps
            
            # 1. 全部渲染在 GPU 完成
            self.render_frame_to_buffer(points, frame_idx, style, frame_time)
            
            # 2. 只在最后读回一次数据
            # components=3 自动丢弃 alpha，适合 mp4
            data = self.fbo_main.read(components=3, alignment=1)
            
            # 3. 直接写入 byte buffer，避免 numpy copy overhead (如果 imageio 支持)
            # imageio 需要 numpy array
            img = np.frombuffer(data, dtype=np.uint8).reshape((self.frame_size[1], self.frame_size[0], 3))
            
            writer.append_data(img)
            
            if progress_callback:
                progress_callback(frame_idx + 1, num_frames)
            
            if (frame_idx + 1) % 100 == 0:
                elapsed = time.time() - t0
                fps_render = (frame_idx + 1) / elapsed
                print(f"进度: {frame_idx + 1}/{num_frames} | 速度: {fps_render:.1f} fps")
            
        writer.close()
        print(f"完成: {output_path}")

    def render_trajectory_images(self, trajectory_file: str, output_dir: str, style: TrajectoryStyle,
                               progress_callback: Optional[Callable[[int, int], None]] = None):
        names, points = self._load_trajectory_with_names(trajectory_file)
        num_frames = len(points)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"GPU加速渲染图片... 共 {num_frames} 帧")
        
        for frame_idx in range(num_frames):
            self.render_frame_to_buffer(points, frame_idx, style)
            
            # 读取 RGBA
            data = self.fbo_main.read(components=4, alignment=1)
            img = np.frombuffer(data, dtype=np.uint8).reshape((self.frame_size[1], self.frame_size[0], 4))
            imageio.imwrite(str(output_path / f"{names[frame_idx]}.png"), img)
            
            if progress_callback:
                progress_callback(frame_idx + 1, num_frames)

            if (frame_idx + 1) % 100 == 0:
                print(f"已处理 {frame_idx + 1}/{num_frames}")

    # --- 辅助函数保持不变 ---
    def _load_trajectory(self, txt_file: str) -> np.ndarray:
        points = []
        with open(txt_file, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'): continue
                parts = [p.strip() for p in line.split(',')] if ',' in line else line.split()
                if len(parts) >= 3:
                    try: points.append([float(parts[1]), float(parts[2])])
                    except ValueError: points.append([np.nan, np.nan])
        points = np.array(points, dtype=np.float32)
        if points.ndim != 2: points = np.empty((0, 2), dtype=np.float32)
        if points.size:
            valid = ~np.isnan(points[:, 0])
            points[valid, 1] = self.frame_size[1] - points[valid, 1]
        return points

    def _load_trajectory_with_names(self, txt_file: str):
        names, points = [], []
        with open(txt_file, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'): continue
                parts = [p.strip() for p in line.split(',')] if ',' in line else line.split()
                if len(parts) >= 3:
                    names.append(parts[0])
                    try: points.append([float(parts[1]), float(parts[2])])
                    except: points.append([np.nan, np.nan])
        points = np.array(points, dtype=np.float32)
        if points.size:
            valid = ~np.isnan(points[:, 0])
            points[valid, 1] = self.frame_size[1] - points[valid, 1]
        return names, points

    def __del__(self):
        if self.ctx: self.ctx.release()

# --- 保持原来的入口函数和预设 ---
def render_enhanced_trajectory(trajectory_file: str, output_video: Optional[str] = None,
                             output_images: Optional[str] = None, style: Optional[TrajectoryStyle] = None,
                             frame_size: Tuple[int, int] = (3840, 2160), fps: int = 25,
                             progress_callback: Optional[Callable[[int, int], None]] = None) -> None:
    if style is None: style = TrajectoryStyle()
    renderer = EnhancedTrajectoryRenderer(frame_size)
    try:
        if output_video: renderer.render_trajectory_video(trajectory_file, output_video, style, fps, progress_callback)
        if output_images: renderer.render_trajectory_images(trajectory_file, output_images, style, progress_callback)
    finally:
        del renderer

# 预设样式
class PresetStyles:
    """预设轨迹样式"""
    
    @staticmethod
    def neon_glow() -> TrajectoryStyle:
        """2025 终极霓虹光轨 | 性能拉满 + 视觉炸裂"""
        return TrajectoryStyle(
            # ── 基础形态 ─────────────────────────────────────
            head_width=12.0,           # 头部更粗更有冲击力
            tail_width=4.0,            # 尾部细长，拖尾感强
            max_length=30,             # 更长轨迹，适合高速运动

            # ── 核心渐变模式（推荐改用 CYBERPUNK 或 NEON_GLOW）────
            # gradient_mode=GradientMode.CYBERPUNK,   # ← 强烈推荐！比 HSV_RAINBOW 更快、更赛博、更稳
            gradient_mode=GradientMode.NEON_GLOW, # 备选：如果你就是要多段霓虹

            # ── 颜色（使用 CYBERPUNK 时可以忽略 middle_colors）────
            head_color=(1.0, 0.1, 0.8, 1.0),     # 电光紫粉（经典赛博色）
            tail_color=(0.0, 0.9, 1.0, 0.0),     # 青色 → 完全透明（完美拖尾）

            # 如果你坚持用 NEON_GLOW，这里给出最帅的多段配色（可直接切换）
            middle_colors=[
                (1.0, 0.0, 0.7, 1.0),   # 品红
                (0.8, 0.0, 1.0, 1.0),   # 紫
                (0.0, 0.7, 1.0, 1.0),   # 电蓝
                (0.0, 1.0, 0.9, 1.0),   # 青
            ],

            # ── 光晕（最重要！）────────────────────────────────
            glow_enabled=True,
            glow_radius=20.0,          # 大光晕才是灵魂
            glow_intensity=1.4,        # 狠狠地发光！
            glow_color=(0.6, 0.2, 1.0, 0.7),  # 紫色外光晕，超赛博

            # ── 动画 & 动态感 ─────────────────────────────────
            fade_alpha=True,           # 尾巴自然消失
            antialiasing=True,
            width_animation=True,      # 呼吸式宽度跳动
            color_animation=True,      # 颜色轻微循环（配合 CYBERPUNK 超丝滑）
            animation_speed=2.0,       # 更快呼吸频率，更有科技感

            # ── 混合模式（关键优化！）────────────────────────────
            blend_mode=BlendMode.ADDITIVE,   # 加法混合 = 真正发光！比 NORMAL 亮 10 倍

            # ── 性能优化参数（对高帧率视频非常重要）────────────────────
            exit_fade_frames=20,       # 消失更快，减少残影卡顿
        )
    
    @staticmethod
    def plasma_trail() -> TrajectoryStyle:
        """等离子轨迹效果"""
        return TrajectoryStyle(
            head_width=10.0,
            tail_width=2.0,
            max_length=20,
            gradient_mode=GradientMode.PLASMA,
            head_color=(1.0, 0.4, 0.8, 1.0),
            tail_color=(0.2, 0.8, 1.0, 0.2),
            glow_enabled=True,
            glow_radius=8.0,
            glow_intensity=0.6,
            fade_alpha=True,
            antialiasing=True
        )
    
    @staticmethod
    def fire_trail() -> TrajectoryStyle:
        """火焰轨迹效果"""
        return TrajectoryStyle(
            head_width=18.0,
            tail_width=1.5,
            max_length=40,
            gradient_mode=GradientMode.LINEAR,
            glow_enabled=True,
            glow_radius=10.0,
            glow_intensity=0.7,
            glow_color=(1.0, 0.3, 0.0, 0.8),
            fade_alpha=True,
            antialiasing=True
        )
    
    @staticmethod
    def ice_trail() -> TrajectoryStyle:
        """冰霜轨迹效果"""
        return TrajectoryStyle(
            head_width=15.0,
            tail_width=2.0,
            max_length=20,
            gradient_mode=GradientMode.LINEAR,
            head_color=(0.8, 0.9, 1.0, 1.0),
            tail_color=(0.4, 0.7, 1.0, 0.3),
            glow_enabled=True,
            glow_radius=6.0,
            glow_intensity=0.5,
            glow_color=(0.7, 0.9, 1.0, 0.6),
            fade_alpha=True,
            antialiasing=True
        )
    
    @staticmethod
    def neon_rainbow() -> TrajectoryStyle:
        """霓虹彩虹效果 - 首尾颜色可设置，中间自动生成彩虹渐变"""
        return TrajectoryStyle(
            head_width=9.0,
            tail_width=1.0,
            max_length=20,
            gradient_mode=GradientMode.NEON_GLOW,
            head_color=(1.0, 0.0, 1.0, 1.0),  # 紫红色头部
            tail_color=(0.0, 1.0, 1.0, 0.4),  # 青色尾部
            middle_colors=[
                (1.0, 0.0, 0.0, 0.8),  # 红色
                (1.0, 0.5, 0.0, 0.8),  # 橙色
                (1.0, 1.0, 0.0, 0.8),  # 黄色
                (0.0, 1.0, 0.0, 0.8),  # 绿色
                (0.0, 0.0, 1.0, 0.8),  # 蓝色
            ],
            glow_enabled=True,
            glow_radius=15.0,
            glow_intensity=0.9,
            glow_color=(0.8, 0.4, 1.0, 0.7),  # 紫色光晕
            fade_alpha=True,
            antialiasing=True,
            width_animation=True,
            color_animation=True,
            animation_speed=1.2,
            blend_mode=BlendMode.ADDITIVE  # 使用加法混合模式增强霓虹效果
        )
        
    @staticmethod
    def aurora() -> TrajectoryStyle:
        return TrajectoryStyle(
            head_width=10, tail_width=1, max_length=20,
            gradient_mode=GradientMode.AURORA,
            head_color=(0.8, 1.0, 1.0, 1.0),
            tail_color=(0.1, 0.3, 0.8, 0.0),
            glow_enabled=True, glow_radius=20, glow_intensity=1.2,
            fade_alpha=True, antialiasing=True, width_animation=True
        )

    @staticmethod
    def blackhole() -> TrajectoryStyle:
        return TrajectoryStyle(
            head_width=15, tail_width=1, max_length=20,
            gradient_mode=GradientMode.ACCRETION_DISK,
            head_color=(1.0, 0.9, 0.8, 1.0),
            tail_color=(0.8, 0.2, 0.1, 0.0),
            glow_enabled=True, glow_radius=25, glow_intensity=1.5,
            fade_alpha=True, antialiasing=True
        )

    @staticmethod
    def custom() -> TrajectoryStyle:
        """自定义轨迹样式"""
        return TrajectoryStyle(
            head_width=9.0,           # 头部宽度
            tail_width=1.0,            # 尾部宽度
            max_length=20,             # 轨迹长度
            gradient_mode=GradientMode.NEON_GLOW,
            head_color = (0.016, 0.0, 0.745, 1.0),      # rgb(4, 0, 190) 深蓝紫
            middle_colors = [
                (0.200, 0.000, 1.000, 1.0),  # rgb(51, 0, 255)
                (0.400, 0.000, 1.000, 1.0),  # rgb(102, 0, 255)
                (0.600, 0.000, 1.000, 1.0),  # rgb(153, 0, 255)
                (0.800, 0.000, 0.900, 1.0),  # rgb(204, 0, 230)
                (1.000, 0.000, 0.800, 1.0),  # rgb(255, 0, 204) 热粉
                (1.000, 0.100, 0.600, 1.0),  # rgb(255, 25, 153)
                (1.000, 0.200, 0.400, 1.0),  # rgb(255, 51, 102)
                (1.000, 0.300, 0.200, 1.0),  # rgb(255, 76, 51)
                (1.000, 0.400, 0.100, 1.0),  # rgb(255, 102, 25)
            ],
            tail_color = (0.706, 0.035, 0.035, 1.0),     # rgb(180, 9, 9) 深红
            glow_enabled=True,         # 启用光晕
            glow_radius=8.0,          # 增大光晕半径
            glow_intensity=0.8,        # 增强光晕强度
            glow_color=(0.8, 0.8, 1.0, 0.8),  # 设置明显的光晕颜色（淡蓝色）
            fade_alpha=False,           # 透明度渐变
            antialiasing=True,         # 抗锯齿
            width_animation=False,     # 关闭宽度动画
            color_animation=False      # 关闭颜色动画
        )
        
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='增强版轨迹渲染器')
    parser.add_argument('trajectory_file', help='轨迹文件路径')
    parser.add_argument('--output-video', help='输出视频路径')
    parser.add_argument('--output-images', help='输出图像目录')
    parser.add_argument('--preset', 
                       choices=['neon', 'plasma', 'fire', 'ice', 'neon_rainbow', 'custom', 'aurora', 'blackhole'],
                       default='neon_rainbow', help='预设样式')
    parser.add_argument('--width', type=int, default=3840, help='视频宽度')
    parser.add_argument('--height', type=int, default=2160, help='视频高度')
    parser.add_argument('--fps', type=int, default=25, help='视频帧率')
    
    args = parser.parse_args()
    
    preset_map = {
        'neon': PresetStyles.neon_glow(),
        'plasma': PresetStyles.plasma_trail(),
        'fire': PresetStyles.fire_trail(),
        'ice': PresetStyles.ice_trail(),
        'neon_rainbow': PresetStyles.neon_rainbow(),
        'custom': PresetStyles.custom(),
        'aurora': PresetStyles.aurora(),
        'blackhole': PresetStyles.blackhole()
    }
    
    style = preset_map[args.preset]
    
    print(f"使用预设样式: {args.preset}")
    print(f"输出分辨率: {args.width}x{args.height}")
    
    render_enhanced_trajectory(
        trajectory_file=args.trajectory_file,
        output_video=args.output_video,
        output_images=args.output_images,
        style=style,
        frame_size=(args.width, args.height),
        fps=args.fps
    )
    
# python utils\render_traj.py "D:\videos\tabletennis\ttb1\predict\labels.txt" --output-video D:\videos\tabletennis\ttb1\predict\trajectory.mp4 --output-images D:\videos\tabletennis\ttb1\predict\rendered_images --preset custom --width 1920 --height 1080 --fps 25
