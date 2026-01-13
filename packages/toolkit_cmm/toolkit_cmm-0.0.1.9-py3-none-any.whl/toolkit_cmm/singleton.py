def Singleton(class_):
    """
    Singleton simple impelement

    Usage::

      @Singleton
      class CustomClass:
        ...
    """
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance
