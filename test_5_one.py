class modulo_folder:
   class modulo:
      def pastel():
          return "Pastel de zanahoria"
      
      class Bolinho:
          def __init__(self, sabor: str):
              self.sabor = sabor
      
          def __str__(self):
              return f"Bolinho de {self.sabor}"
      
          def __repr__(self):
              return f"Bolinho de {self.sabor}"
          
          def sub_bolinho(self):
              return "Sub bolinho"
   

bolinho = modulo_folder.modulo.Bolinho


class modulo_folder(modulo_folder):
   class modulo:
      def pastel():
          return "Pastel de zanahoria"
      
      class Bolinho:
          def __init__(self, sabor: str):
              self.sabor = sabor
      
          def __str__(self):
              return f"Bolinho de {self.sabor}"
      
          def __repr__(self):
              return f"Bolinho de {self.sabor}"
          
          def sub_bolinho(self):
              return "Sub bolinho"
   

pastel = modulo_folder.modulo.pastel


class modulo_folder(modulo_folder):
   class modulo:
      def pastel():
          return "Pastel de zanahoria"
      
      class Bolinho:
          def __init__(self, sabor: str):
              self.sabor = sabor
      
          def __str__(self):
              return f"Bolinho de {self.sabor}"
      
          def __repr__(self):
              return f"Bolinho de {self.sabor}"
          
          def sub_bolinho(self):
              return "Sub bolinho"
   

modulo = modulo_folder.modulo


