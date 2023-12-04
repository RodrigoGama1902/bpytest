

def register_addon():

    from ..panels import register_panels
    register_panels()
    
    from ..operator import register_operators
    register_operators()
    
    from ..addon_properties import register_properties
    register_properties()

def unregister_addon():

    from ..operator import unregister_operators
    unregister_operators()
    
    from ..panels import unregister_panels
    unregister_panels()
        
    from ..addon_properties import unregister_properties
    unregister_properties()


