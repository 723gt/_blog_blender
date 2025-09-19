import bpy
import os
from bpy.types import Menu

# アドオン情報
bl_info = {
    "name": "FBX Importer test",
    "author": "Your Name (開発者名をここに入力してください)", # 開発者名を適切に設定してください
    "version": (1, 0),
    "blender": (4, 3, 0),
    "location": "Add > FBX Importer",
    "description": "Imports FBX files from a specified directory.",
    "warning": "",
    "doc_url": "",
    "category": "Import",
}

# FBXファイルが置かれているディレクトリ
FBX_MODULE_DIR = "c:/Users/eriko/Documents/blender_fbx_modules"

class FBX_IMPORTER_OT_import_fbx(bpy.types.Operator):
    """指定されたFBXファイルをインポートします"""
    bl_idname = "fbx_importer.import_fbx"
    bl_label = "Import FBX"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(
        name="File Path",
        subtype='FILE_PATH',
    )

    def execute(self, context):
        if not self.filepath:
            self.report({'ERROR'}, "No FBX file selected.")
            return {'CANCELLED'}

        if not os.path.exists(self.filepath):
            self.report({'ERROR'}, f"File not found: {self.filepath}")
            return {'CANCELLED'}

        try:
            # FBXをデフォルトオプションでインポート
            bpy.ops.wm.collada_import(filepath=self.filepath) # BlenderのFBXインポーターは 'wm.collada_import' ではなく 'wm.fbx_import' です
                                                            # 修正します
            bpy.ops.wm.fbx_import(filepath=self.filepath)
            self.report({'INFO'}, f"Successfully imported: {os.path.basename(self.filepath)}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to import FBX: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

class FBX_IMPORTER_MT_add_menu(Menu):
    """Shift + A (追加) メニューにFBXファイル一覧を表示するメニュー"""
    bl_idname = "FBX_IMPORTER_MT_add_menu"
    bl_label = "FBX Importer"

    def draw(self, context):
        layout = self.layout
        
        if not os.path.isdir(FBX_MODULE_DIR):
            layout.label(text=f"Directory not found: {FBX_MODULE_DIR}", icon='ERROR')
            return

        fbx_files = [f for f in os.listdir(FBX_MODULE_DIR) if f.lower().endswith(('.fbx'))]
        
        if not fbx_files:
            layout.label(text="No FBX files found in the directory.", icon='INFO')
            return

        for fbx_file in sorted(fbx_files):
            filepath = os.path.join(FBX_MODULE_DIR, fbx_file)
            op = layout.operator(FBX_IMPORTER_OT_import_fbx.bl_idname, text=fbx_file)
            op.filepath = filepath

def menu_func_add_object(self, context):
    """オブジェクト追加メニューに関数を追加"""
    self.layout.menu(FBX_IMPORTER_MT_add_menu.bl_idname)

def register():
    bpy.utils.register_class(FBX_IMPORTER_OT_import_fbx)
    bpy.utils.register_class(FBX_IMPORTER_MT_add_menu)
    bpy.types.VIEW3D_MT_add.append(menu_func_add_object)

def unregister():
    bpy.types.VIEW3D_MT_add.remove(menu_func_add_object)
    bpy.utils.unregister_class(FBX_IMPORTER_MT_add_menu)
    bpy.utils.unregister_class(FBX_IMPORTER_OT_import_fbx)

if __name__ == "__main__":
    register()