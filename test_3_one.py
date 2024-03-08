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
   
import sys



def pastel3():
    import modulo_folder.modulo
    return "Pastel de zanahoria"

print(modulo_folder.modulo.Bolinho)
