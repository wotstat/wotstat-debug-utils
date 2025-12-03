from .Line import Line

class SeparatorLine(Line):
  def __init__(self, properties=1, commands=0):
    # type: (str, int, int) -> None
    super(SeparatorLine, self).__init__(type='separator', properties=properties, commands=commands)
  
  def _initialize(self):
    # type: () -> None
    super(SeparatorLine, self)._initialize()
    