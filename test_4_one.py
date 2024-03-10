class modulo_folder:
   class submodulo_folder:
      class modulo_4:
         def pipoca():
             print('pipoca')
      
   


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
   
m = modulo_folder.modulo


class modulo_folder(modulo_folder):
   class modulo_2:
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
         
      m1 = modulo_folder.modulo
      

      
      def pizza():
          class modulo_folder:
             class modulo_3:
                def tapioca():
                    print("Tapioca de coco")
             
          m3 = modulo_folder.modulo_3
          

          return "I am a pizza from modulo_2"
      
      print(m1.Bolinho)
   
m2 = modulo_folder.modulo_2




def pastel3():
    return "Pastel de zanahoria"
m2.pizza()

print(m.Bolinho)
