import intermodule


def func():
    global x
    intermodule.SharedGlobal.get_global("x")
    x += 30

if intermodule.patch_and_reload_module():
    pass
