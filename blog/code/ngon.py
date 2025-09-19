bl_info = {
    "name": "Nゴン表示",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > ツール",
    "description": "編集モードでNゴンを赤色で表示します",
    "warning": "",
    "category": "3D View"
}

import bpy
from bpy.props import BoolProperty
from bpy_extras import view3d_utils
import gpu
from gpu_extras.batch import batch_for_shader

# シェーダーの定義
vertex_shader = '''
    uniform mat4 ModelViewProjectionMatrix;
    in vec3 position;
    void main() {
        gl_Position = ModelViewProjectionMatrix * vec4(position, 1.0);
    }
'''

fragment_shader = '''
    uniform vec4 color;
    out vec4 FragColor;
    void main() {
        FragColor = color;
    }
'''

shader = gpu.types.GPUShader(vertex_shader, fragment_shader)

_draw_handler = None  # グローバル変数でハンドラを管理

def draw_ngons_callback():
    context = bpy.context
    if not context.object or context.object.mode != 'EDIT' or not context.scene.ngon_color_properties.enable_ngon_color:
        return

    obj = context.object
    mesh = obj.data

    if not mesh.is_editmode:
        return

    gpu.state.depth_test_set('LESS_EQUAL')
    gpu.state.blend_set('ALPHA')

    batch_verts = []

    for poly in mesh.polygons:
        if len(poly.vertices) >= 5:
            for i in range(1, len(poly.vertices) - 1):
                batch_verts.append(obj.matrix_world @ mesh.vertices[poly.vertices[0]].co)
                batch_verts.append(obj.matrix_world @ mesh.vertices[poly.vertices[i]].co)
                batch_verts.append(obj.matrix_world @ mesh.vertices[poly.vertices[i+1]].co)

    if batch_verts:
        batch = batch_for_shader(shader, 'TRIS', {"position": batch_verts})
        shader.bind()
        shader.uniform_float("color", (1.0, 0.0, 0.0, 0.5))
        region_data = context.region_data
        if region_data:
            shader.uniform_float("ModelViewProjectionMatrix", region_data.perspective_matrix)
        batch.draw(shader)

    gpu.state.depth_test_set('NONE')
    gpu.state.blend_set('NONE')

class NgonColorProperties(bpy.types.PropertyGroup):
    enable_ngon_color: BoolProperty(
        name="Nゴンをカラー",
        description="編集モードで五角形以上の面を赤色で表示します",
        default=False,
        update=lambda self, context: update_ngon_color_display(self, context)
    )

def update_ngon_color_display(self, context):
    global _draw_handler
    # 既存のハンドラを解除
    if _draw_handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_draw_handler, 'WINDOW')
        _draw_handler = None

    # 有効化時のみ新規登録
    if context.scene.ngon_color_properties.enable_ngon_color:
        _draw_handler = bpy.types.SpaceView3D.draw_handler_add(
            draw_ngons_callback, (), 'WINDOW', 'POST_VIEW'
        )

    # ビューポートを再描画
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()

def mesh_update_handler(scene):
    """メッシュの更新をモニタリングするハンドラ"""
    if scene.ngon_color_properties.enable_ngon_color:
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

class VIEW3D_PT_NgonColorPanel(bpy.types.Panel):
    bl_label = "Nゴン設定"
    bl_idname = "VIEW3D_PT_ngon_color_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Nゴン消すやつ" # サイドメニューのカテゴリ

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.ngon_color_properties

        row = layout.row()
        row.prop(props, "enable_ngon_color")

classes = (
    NgonColorProperties,
    VIEW3D_PT_NgonColorPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.ngon_color_properties = bpy.props.PointerProperty(type=NgonColorProperties)
    
    # メッシュ更新ハンドラを登録
    bpy.app.handlers.depsgraph_update_post.append(mesh_update_handler)
    
    # bpy.context.sceneの直接参照を避ける
    def setup_handler():
        if hasattr(bpy.context, "scene"):
            if bpy.context.scene.ngon_color_properties.enable_ngon_color:
                global _draw_handler
                _draw_handler = bpy.types.SpaceView3D.draw_handler_add(
                    draw_ngons_callback, (), 'WINDOW', 'POST_VIEW'
                )

    # タイマーを使用して遅延実行
    bpy.app.timers.register(setup_handler, first_interval=0.1)

def unregister():
    global _draw_handler
    if _draw_handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_draw_handler, 'WINDOW')
        _draw_handler = None
    
    # メッシュ更新ハンドラを解除
    bpy.app.handlers.depsgraph_update_post.remove(mesh_update_handler)
    
    del bpy.types.Scene.ngon_color_properties
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()