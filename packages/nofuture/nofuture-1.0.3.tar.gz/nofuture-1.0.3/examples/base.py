# Example 1/3: MayBe basics
from nofut import MayBe

# Level 1: construction and inspection
just_value = MayBe.just(3)
nothing_value = MayBe.nothing()

assert just_value.is_just()
assert nothing_value.is_nothing()

# Level 2: extraction and defaults
assert just_value.unwrap() == 3
assert nothing_value.or_else(99) == 99

# Level 3: transform and chain
assert just_value.map(lambda x: x + 1).unwrap() == 4
assert (just_value >> (lambda x: MayBe.just(x * 2))).unwrap() == 6

# Level 4: operators and truthiness
assert (nothing_value | 123) == 123
assert bool(just_value)
assert repr(just_value) == "Just(3)"

# Level 5: expect and to_option
assert just_value.expect("should have value") == 3
assert just_value.to_option() == 3
assert nothing_value.to_option() is None

# Level 6: pattern matching
result = just_value.match(just=lambda x: f"got {x}", nothing=lambda: "empty")
assert result == "got 3"

result2 = nothing_value.match(just=lambda x: f"got {x}", nothing=lambda: "empty")
assert result2 == "empty"

# partial match (callback optionnel)
assert just_value.match(just=lambda x: x * 10) == 30
assert nothing_value.match(nothing=lambda: "default") == "default"

print("MayBe basics OK")
