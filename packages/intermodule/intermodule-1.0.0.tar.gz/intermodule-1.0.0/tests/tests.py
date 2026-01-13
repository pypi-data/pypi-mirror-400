import intermodule
import test2


intermodule.SharedGlobal.set_global("x", 10)
intermodule.SharedGlobal.set_global("x", 20)


if intermodule.patch_and_reload_module():
    intermodule.SharedGlobal.set_global("y", 50)
    x += y
    print(x)
    test2.func()
    print(test2.x)
    print(x)
