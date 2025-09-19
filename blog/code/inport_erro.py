import bpy
import os
from bpy_extras.io_utils import ImportHelper

# ====================================================================
# 1. アドオン情報
# ====================================================================
bl_info = {
    "name": "Local FBX Importer",
    "author": "Your Name", # あなたの名前に変更してください
    "version": (1, 0),
    "blender": (4, 3, 0), # Blender 4.3 をターゲット
    "location": "Object Mode > Add Menu (Shift+A)",
    "description": "Imports FBX models from a specified local directory.",
    "warning": "",
    "doc_url": "",
    "category": "Import-Export",
}

# ====================================================================
# 2. 設定
# ====================================================================
# ★★★ ここをあなたのFBXファイルがあるフォルダのパスに変更してください ★★★
# 例: Windowsの場合 "C:\\Users\\YourUser\\Models\\FBX"
# 例: macOS/Linuxの場合 "/Users/YourUser/Models/FBX"
FBX_DIR = "C:\\path\\to\\your\\fbx\\folder" 

# ====================================================================
# 3. オペレータ定義
# ====================================================================
class OBJECT_OT_local_fbx_importer(bpy.types.Operator, ImportHelper):
    """ローカルフォルダからFBXモデルを読み込みます"""
    bl_idname = "object.local_fbx_importer"
    bl_label = "ローカルからモデル読み込み"
    bl_options = {'REGISTER', 'UNDO'}

    # ファイルブラウザ用のプロパティ
    filename_ext = ".fbx"
    filter_glob: bpy.props.StringProperty(
        default="*.fbx",
        options={'HIDDEN'},
        maxlen=255,
    )

    def execute(self, context):
        if not os.path.isdir(FBX_DIR):
            self.report({'ERROR'}, f"指定されたFBXフォルダが見つかりません: {FBX_DIR}")
            return {'CANCELLED'}
        
        # ファイルブラウザの初期パスを設定
        self.filepath = os.path.join(FBX_DIR, self.filepath)

        # ファイルが存在することを確認
        if not os.path.exists(self.filepath):
            self.report({'ERROR'}, f"選択されたFBXファイルが見つかりません: {self.filepath}")
            return {'CANCELLED'}

        try:
            # FBXファイルをインポート
            bpy.ops.import_scene.fbx(filepath=self.filepath)
            self.report({'INFO'}, f"FBXファイルを読み込みました: {os.path.basename(self.filepath)}")
        except Exception as e:
            self.report({'ERROR'}, f"FBXファイルの読み込み中にエラーが発生しました: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        # ファイルブラウザを開く際の初期ディレクトリを設定
        # FBX_DIR が有効なパスでない場合はキャンセル
        if not os.path.isdir(FBX_DIR):
            self.report({'ERROR'}, f"指定されたFBXフォルダが見つかりません: {FBX_DIR}")
            return {'CANCELLED'}

        context.window_manager.fileselect_add(self)
        context.window_manager.fileselect_last_path = FBX_DIR # Blender 4.x の推奨される設定方法
        return {'RUNNING_MODAL'}

# ====================================================================
# 4. メニューへの追加
# ====================================================================
def add_local_fbx_importer_menu(self, context):
    """Shift+Aメニューに項目を追加します"""
    if context.mode == 'OBJECT':
        self.layout.operator(OBJECT_OT_local_fbx_importer.bl_idname, text="ローカルからモデル読み込み", icon='MESH_CUBE')

# ====================================================================
# 5. アドオン登録・登録解除
# ====================================================================
def register():
    bpy.utils.register_class(OBJECT_OT_local_fbx_importer)
    bpy.types.VIEW3D_MT_add.append(add_local_fbx_importer_menu)
    print("Local FBX Importer registered.")

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_local_fbx_importer)
    bpy.types.VIEW3D_MT_add.remove(add_local_fbx_importer_menu)
    print("Local FBX Importer unregistered.")

if __name__ == "__main__":
    register()
