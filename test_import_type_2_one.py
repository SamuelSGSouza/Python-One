def pastel():
    return "Pastel de zanahoria"

class Bolinho:
    def __init__(self, sabor: str):
        self.sabor = sabor

    def __str__(self):
        return f"Bolinho de {self.sabor}"

    def __repr__(self):
        return f"Bolinho de {self.sabor}"


print(p.pastel)
