
class Animal():
    """
    Abstract class for kingdom animalia
    """

    def __init__(self, name):
        self.name = name

    def getBiologicalName(self):

        return self.name.swapcase()


class Person(Animal):
    """Person class

    describes the biological and visible attribures of a person

    Extends:
        Animal
    """

    def __init__(self, name, gender, weight, height):
        super().__init__(name)
        self.gender = gender
        self.weight = weight
        self.height = height

    def calculateBMI(self):

        return eval('self.weight/(self.height**2)')


if __name__ == "__main__":
    p = Person("Joseph", "Male", 78.2, 1.8)
    print("BMI:", p.calculateBMI())
    print("Biological Name:", p.getBiologicalName())
