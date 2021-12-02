modes = (
    'Image Paint',
    'Vertex Paint',
    'Weight Paint'
)

key_type = 'SPACE'
key_value = 'PRESS'
op = 'view3d.color_picker'


def get_keyitem(context):
    mode = context.mode
    km = modes[0] if mode=='PAINT_TEXTURE' else modes[2] if mode=='PAINT_WEIGHT' else modes[1]
    return context.window_manager.keyconfigs.user.keymaps[km].keymap_items.get(op, None)

def get_keyitem_mode(context, mode):
    return context.window_manager.keyconfigs.user.keymaps[mode].keymap_items.get(op, None)

def register():
    from bpy import context as C
    cfg = C.window_manager.keyconfigs.addon
    for mode in modes:
        if not cfg.keymaps.__contains__(mode):
            cfg.keymaps.new(mode, space_type='EMPTY', region_type='WINDOW')
        kmi = cfg.keymaps[mode].keymap_items
        kmi.new(op, key_type, key_value)

def unregister():
    from bpy import context as C
    cfg = C.window_manager.keyconfigs.addon
    for mode in modes:
        if cfg.keymaps.__contains__(mode):
            for kmi in cfg.keymaps[mode].keymap_items:
                if kmi.idname == op:
                    if kmi.value == key_value and kmi.type == key_type:
                        cfg.keymaps[mode].keymap_items.remove(kmi)
                        break
