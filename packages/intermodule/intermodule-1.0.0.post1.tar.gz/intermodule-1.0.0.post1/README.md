# intermodule
This library makes it possible to share global variables across modules.

# Installation
```pip install intermodule```

# Api Reference
_class_ intermodule.**SharedGlobal**

Instances of this class manage a global variable and keep it synchronized across modules.
You should never instantiate this class directly. Instead, use ```set_global``` and ```get_global``` functions.
This class inherits a variant of [ObjectProxy](https://wrapt.readthedocs.io/en/master/wrappers.html#object-proxy) from wrapt.
Along with all augmented assignment operators, this class also overloads the normal assignment operator (=) thanks to [assign-overload](https://github.com/pyhacks/assign-overload).
Underlying global variable can be any object and the resulting instance of this class will act like that object in every way.
If you use this class, you need to call intermodule.**patch_and_reload_module**(). 
You can also access this function from assign_overload module.
You can find documentation about this function in [assign-overload](https://github.com/pyhacks/assign-overload).

SharedGlobal.**set_global**(name, value)

Creates a new ```SharedGlobal``` instance with the given _name_ and _value_ but doesn't return it.
Instead, assigns it to the calling module. 
Lastly, assigns it to every module which has a global variable whose name is _name_ and whose value is a ```SharedGlobal``` instance.

SharedGlobal.**get_global**(name)

Search through every module for a already defined global variable named _name_. 
If found, check if it is a ```SharedGlobal``` instance.
If it is, assign its value to the calling module. The value won't be returned.
If no module defines a variable named _name_ or if its value is not a ```SharedGlobal``` instance, raise an error.

# Example
```python
# module1.py
import intermodule

intermodule.SharedGlobal.set_global("x", 10)

def main():
    global x
    import module2
    module2.func1()
    print(x) # prints 20
    x = 30
    module2.func2()

if intermodule.patch_and_reload_module():
    main()
```

```python
# module2.py
import intermodule

intermodule.SharedGlobal.get_global("x")

def func1():
    global x
    x = 20

def func2():
    print(x) # prints 30

if intermodule.patch_and_reload_module():
    pass
```
