# Example 2/3: MayBe with objects
from dataclasses import dataclass
from nofut import MayBe


# Focus: mapping objects through MayBe
@dataclass
class Dog:
    name: str

    def speak(self) -> str:
        return f"{self.name} says woof!"


@dataclass
class Cat:
    name: str

    def speak(self) -> str:
        return f"{self.name} says meow!"


def find_animal(name: str) -> MayBe:
    if name.startswith("D"):
        return MayBe.just(Dog(name))
    return MayBe.nothing()


maybe_dog = find_animal("Larsen")
maybe_cat = find_animal("Whiskers")

greeting1 = maybe_dog.map(lambda a: a.speak())
greeting2 = maybe_cat.map(lambda a: a.speak())

assert repr(greeting1) == "Just(Larsen says woof!)"
assert repr(greeting2) == "Nothing"

# Fallback value with or_else
default_cat = Cat("FallbackCat")
final_greeting = greeting2.or_else(default_cat.speak())
assert final_greeting == "FallbackCat says meow!"


# Chaining with >> and a MayBe-returning function


def to_upper(msg: str) -> MayBe:
    return MayBe.just(msg.upper())


chained = greeting1 >> (lambda msg: to_upper(msg))
assert repr(chained) == "Just(LARSEN SAYS WOOF!)"


# Pattern matching with objects
def describe_animal(maybe_animal: MayBe) -> str:
    return maybe_animal.match(just=lambda a: f"Found: {a.speak()}", nothing=lambda: "No animal found")


assert describe_animal(maybe_dog) == "Found: Larsen says woof!"
assert describe_animal(maybe_cat) == "No animal found"

# to_option for integration with existing code
animal_or_none = maybe_dog.to_option()
assert animal_or_none is not None
assert animal_or_none.name == "Larsen"

print("MayBe objects OK")
