from glob import iglob
import os

import moderngl_window as mglw
import moderngl as mgl
from moderngl_window import scene
import glm

from ..blueprint import Blueprint


class CameraWindow(mglw.WindowConfig):
    """Base class with built in 3D camera support"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = scene.KeyboardCamera(
            self.wnd.keys, aspect_ratio=self.wnd.aspect_ratio)
        self.camera_enabled = True

    def on_key_event(self, key, action, modifiers):
        keys = self.wnd.keys

        if self.camera_enabled:
            self.camera.key_input(key, action, modifiers)

        if action == keys.ACTION_PRESS:
            if key == keys.C:
                self.camera_enabled = not self.camera_enabled
                self.wnd.mouse_exclusivity = self.camera_enabled
                self.wnd.cursor = not self.camera_enabled
            if key == keys.SPACE:
                self.timer.toggle_pause()

    def on_mouse_position_event(self, x: int, y: int, dx, dy):
        if self.camera_enabled:
            self.camera.rot_state(-dx, -dy)

    def on_resize(self, width: int, height: int):
        self.camera.projection.update(aspect_ratio=self.wnd.aspect_ratio)

    def on_mouse_scroll_event(self, x_offset: float, y_offset: float) -> None:
        velocity = self.camera.velocity + y_offset
        self.camera.velocity = max(velocity, 1.0)


def preview(bp: Blueprint):
    class BlueprintPreviewer(CameraWindow):
        window_size = 1080, 720
        clear_color = 0.3, 0.3, 0

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.wnd.mouse_exclusivity = True

            self.parts: list[scene.Scene] = []
            for i, p in enumerate(iglob("**/*.obj", recursive=True)):
                try:
                    self.parts.append(s := self.load_scene(os.path.abspath(p)))
                    s.matrix *= glm.translate(glm.vec3((i % 8)*5, (i//8)*4, 0))
                except FileNotFoundError:
                    pass
            self.camera = scene.KeyboardCamera(
                self.wnd.keys,
                fov=75.0,
                aspect_ratio=self.wnd.aspect_ratio,
                near=0.1,
                far=1000.0,
            )
            self.camera.velocity = 10.0
            self.camera.mouse_sensitivity = 0.25
            # self.camera.position = (
            #     self.parts.get_center()
            #     + glm.vec3(0.0, 0.0, self.parts.diagonal_size / 0.5)
            # )

        def on_render(self, time, frame_time):
            self.ctx.enable_only(mgl.DEPTH_TEST | mgl.CULL_FACE)
            for part in self.parts:
                part.draw(
                    projection_matrix=self.camera.projection.matrix,
                    camera_matrix=self.camera.matrix,
                    time=time
                )

    BlueprintPreviewer.run()
