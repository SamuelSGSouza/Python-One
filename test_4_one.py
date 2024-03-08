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
   
m = modulo_folder.modulo


class modulo_folder(modulo_folder):
   class modulo_2:
      def pizza():
          import modulo_folder.modulo as m
          return "I am a pizza from modulo_2"
   
m2 = modulo_folder.modulo_2



def pastel3():
    return "Pastel de zanahoria"
m2.pizza()

print(m.Bolinho)
