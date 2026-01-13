import sys
import wrapt


class SharedGlobal(wrapt.AutoObjectProxy):
    class_id = "intermodule.SharedGlobal"
    
    def __object_proxy__(self, wrapped):
        obj = SharedGlobal(wrapped)
        obj._self_name = self._self_name        
        return obj

    def set_to_modules(self, value):
        for module in sys.modules.values():
            if hasattr(module, self._self_name):
                var = getattr(module, self._self_name)
                if hasattr(var, "class_id") and var.class_id == "intermodule.SharedGlobal":
                    setattr(module, self._self_name, value)        
        
    @classmethod
    def set_global(cls, name, value):
        if hasattr(value, "class_id") and value.class_id == "intermodule.SharedGlobal":
            value = value.__wrapped__
        obj = cls(value)
        obj._self_name = name
        module_name = sys._getframe(1).f_globals["__name__"]
        module = sys.modules[module_name]
        setattr(module, obj._self_name, obj)
        obj.set_to_modules(obj)        

    @classmethod
    def get_global(cls, name):
        for module in sys.modules.values():
            if hasattr(module, name):
                var = getattr(module, name)
                if hasattr(var, "class_id") and var.class_id == "intermodule.SharedGlobal" and var._self_name == name:
                    module_name = sys._getframe(1).f_globals["__name__"]
                    module = sys.modules[module_name]
                    setattr(module, var._self_name, var)
                    break
        else:
            raise NameError(f"name '{name}' is not defined")        
        
    def _assign_(self, value, *annotation):
        if hasattr(value, "class_id") and value.class_id == "intermodule.SharedGlobal":
            value = value.__wrapped__
        if hasattr(self.__wrapped__, "_assign_"):
            self.__wrapped__ = self.__wrapped__._assign_(value)
        else:
            self.__wrapped__ = value        
        self.set_to_modules(self)
        return self

    def __iadd__(self, other):
        if hasattr(other, "class_id") and other.class_id == "intermodule.SharedGlobal":
            other = other.__wrapped__        
        value = super().__iadd__(other)
        self.set_to_modules(value)
        return value

    def __isub__(self, other):
        if hasattr(other, "class_id") and other.class_id == "intermodule.SharedGlobal":
            other = other.__wrapped__        
        value = super().__isub__(other)
        self.set_to_modules(value)
        return value

    def __imul__(self, other):
        if hasattr(other, "class_id") and other.class_id == "intermodule.SharedGlobal":
            other = other.__wrapped__                
        value = super().__imul__(other)
        self.set_to_modules(value)
        return value

    def __itruediv__(self, other):
        if hasattr(other, "class_id") and other.class_id == "intermodule.SharedGlobal":
            other = other.__wrapped__                
        value = super().__itruediv__(other)
        self.set_to_modules(value)
        return value

    def __ifloordiv__(self, other):
        if hasattr(other, "class_id") and other.class_id == "intermodule.SharedGlobal":
            other = other.__wrapped__                
        value = super().__ifloordiv__(other)
        self.set_to_modules(value)
        return value

    def __imod__(self, other):
        if hasattr(other, "class_id") and other.class_id == "intermodule.SharedGlobal":
            other = other.__wrapped__                
        value = super().__imod__(other)
        self.set_to_modules(value)
        return value

    def __ipow__(self, other):
        if hasattr(other, "class_id") and other.class_id == "intermodule.SharedGlobal":
            other = other.__wrapped__                
        value = super().__ipow__(other)
        self.set_to_modules(value)
        return value

    def __ilshift__(self, other):
        if hasattr(other, "class_id") and other.class_id == "intermodule.SharedGlobal":
            other = other.__wrapped__                
        value = super().__ilshift__(other)
        self.set_to_modules(value)
        return value

    def __irshift__(self, other):
        if hasattr(other, "class_id") and other.class_id == "intermodule.SharedGlobal":
            other = other.__wrapped__                
        value = super().__irshift__(other)
        self.set_to_modules(value)
        return value

    def __iand__(self, other):
        if hasattr(other, "class_id") and other.class_id == "intermodule.SharedGlobal":
            other = other.__wrapped__                
        value = super().__iand__(other)
        self.set_to_modules(value)
        return value

    def __ixor__(self, other):
        if hasattr(other, "class_id") and other.class_id == "intermodule.SharedGlobal":
            other = other.__wrapped__                
        value = super().__ixor__(other)
        self.set_to_modules(value)
        return value

    def __ior__(self, other):
        if hasattr(other, "class_id") and other.class_id == "intermodule.SharedGlobal":
            other = other.__wrapped__                
        value = super().__ior__(other)
        self.set_to_modules(value)
        return value

    def __imatmul__(self, other):
        if hasattr(other, "class_id") and other.class_id == "intermodule.SharedGlobal":
            other = other.__wrapped__                
        value = super().__imatmul__(other)
        self.set_to_modules(value)
        return value
