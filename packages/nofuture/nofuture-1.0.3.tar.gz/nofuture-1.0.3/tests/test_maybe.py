import unittest
from nofut import MayBe


class TestMayBe(unittest.TestCase):

    def test_constructor_new(self):
        # MayBe(None) == Nothing
        m = MayBe(None)
        self.assertFalse(m.is_just())
        self.assertTrue(m.is_nothing())
        with self.assertRaises(ValueError):
            m.unwrap()

        # MayBe(x) avec x non-None == Just(x)
        j = MayBe(0)
        self.assertTrue(j.is_just())
        self.assertFalse(j.is_nothing())
        self.assertEqual(j.unwrap(), 0)

    def test_static_constructors(self):
        j = MayBe.just("val")
        self.assertTrue(j.is_just())
        self.assertEqual(j.unwrap(), "val")

        n = MayBe.nothing()
        self.assertTrue(n.is_nothing())
        with self.assertRaises(ValueError):
            n.unwrap()

    def test_or_else_method(self):
        j = MayBe.just("hello")
        self.assertEqual(j.or_else("fallback"), "hello")

        n = MayBe.nothing()
        self.assertEqual(n.or_else("fallback"), "fallback")

    def test_map_method(self):
        # map sur Just
        j = MayBe.just(5)
        j2 = j.map(lambda x: x + 3)
        self.assertTrue(isinstance(j2, MayBe))
        self.assertTrue(j2.is_just())
        self.assertEqual(j2.unwrap(), 8)

        # map sur Nothing
        n = MayBe.nothing()
        n2 = n.map(lambda x: x * 2)
        self.assertTrue(isinstance(n2, MayBe))
        self.assertTrue(n2.is_nothing())

    def test_map_propagates_exceptions(self):
        j = MayBe.just(1)
        with self.assertRaises(ZeroDivisionError):
            j.map(lambda x: x / 0)

    def test_rshift_operator_flat_map(self):
        j = MayBe.just(10)
        # flat_map normal
        r = j >> (lambda x: MayBe.just(x * 2))
        self.assertTrue(isinstance(r, MayBe))
        self.assertEqual(r.unwrap(), 20)

        # chaînage
        r2 = j >> (lambda x: MayBe.just(x + 1)) >> (lambda x: MayBe.just(x * 3))
        self.assertEqual(r2.unwrap(), (10 + 1) * 3)

        # >> sur Nothing reste Nothing
        n = MayBe.nothing()
        n2 = n >> (lambda x: MayBe.just(x + 1))
        self.assertTrue(n2.is_nothing())

    def test_rshift_invalid_return_type(self):
        j = MayBe.just(10)
        with self.assertRaises(TypeError):
            j >> (lambda x: x * 2)

    def test_or_operator(self):
        j = MayBe.just(7)
        # sur Just, renvoie la valeur interne
        self.assertEqual(j | 100, 7)

        n = MayBe.nothing()
        # sur Nothing, renvoie default
        self.assertEqual(n | 100, 100)

        # default peut être un type complexe
        default_obj = {"a": 1}
        self.assertIs(n | default_obj, default_obj)

    def test_bool_truthiness(self):
        j = MayBe.just("x")
        n = MayBe.nothing()
        self.assertTrue(bool(j))
        self.assertFalse(bool(n))

    def test_repr(self):
        self.assertEqual(repr(MayBe.just("abc")), "Just(abc)")
        self.assertEqual(repr(MayBe.nothing()), "Nothing")

    def test_store_explicit_none(self):
        # Just(None) doit conserver None
        j = MayBe.just(None)
        self.assertTrue(j.is_just())
        self.assertFalse(j.is_nothing())
        self.assertIsNone(j.unwrap())
        self.assertEqual(repr(j), "Just(None)")
        # or_else ne remplace pas un None stocké
        self.assertIsNone(j.or_else("fallback"))

    def test_map_on_complex_object(self):
        # map doit fonctionner sur tout PyObject
        j = MayBe.just([1, 2, 3])
        j2 = j.map(lambda lst: lst + [4])
        self.assertTrue(j2.is_just())
        self.assertEqual(j2.unwrap(), [1, 2, 3, 4])

    def test_flat_map_on_just(self):
        j = MayBe.just(10)
        r = j.flat_map(lambda x: MayBe.just(x * 2))
        self.assertTrue(r.is_just())
        self.assertEqual(r.unwrap(), 20)

    def test_flat_map_on_nothing(self):
        n = MayBe.nothing()
        r = n.flat_map(lambda x: MayBe.just(x * 2))
        self.assertTrue(r.is_nothing())

    def test_flat_map_returns_nothing(self):
        j = MayBe.just(5)
        r = j.flat_map(lambda x: MayBe.nothing())
        self.assertTrue(r.is_nothing())

    def test_flat_map_invalid_return_type(self):
        j = MayBe.just(3)
        with self.assertRaises(TypeError):
            j.flat_map(lambda x: x * 2)

    def test_flat_map_propagates_exceptions(self):
        j = MayBe.just(1)
        with self.assertRaises(ZeroDivisionError):
            j.flat_map(lambda x: MayBe.just(x / 0))

    def test_class_getitem_generic_syntax(self):
        # MayBe[T] doit retourner la classe MayBe
        aliased = MayBe[int]
        self.assertIs(aliased, MayBe)

        # Fonctionne avec des types complexes
        aliased2 = MayBe[dict]
        self.assertIs(aliased2, MayBe)

        # Les instances fonctionnent normalement après
        j = aliased.just(42)
        self.assertTrue(j.is_just())
        self.assertEqual(j.unwrap(), 42)

    # Tests pour expect()
    def test_expect_just(self):
        j = MayBe.just(42)
        self.assertEqual(j.expect("should not fail"), 42)

    def test_expect_nothing(self):
        n = MayBe.nothing()
        with self.assertRaises(ValueError) as ctx:
            n.expect("custom error message")
        self.assertIn("custom error message", str(ctx.exception))

    # Tests pour to_option()
    def test_to_option_just(self):
        j = MayBe.just("value")
        self.assertEqual(j.to_option(), "value")

    def test_to_option_nothing(self):
        n = MayBe.nothing()
        self.assertIsNone(n.to_option())

    def test_to_option_just_none(self):
        # Just(None) retourne None mais c'est différent de Nothing
        j = MayBe.just(None)
        self.assertIsNone(j.to_option())

    # Tests pour match()
    def test_match_just(self):
        j = MayBe.just(10)
        result = j.match(just=lambda x: x * 2, nothing=lambda: -1)
        self.assertEqual(result, 20)

    def test_match_nothing(self):
        n = MayBe.nothing()
        result = n.match(just=lambda x: x * 2, nothing=lambda: -1)
        self.assertEqual(result, -1)

    def test_match_just_only(self):
        j = MayBe.just(5)
        result = j.match(just=lambda x: x + 1)
        self.assertEqual(result, 6)

    def test_match_nothing_only(self):
        n = MayBe.nothing()
        result = n.match(nothing=lambda: "empty")
        self.assertEqual(result, "empty")

    def test_match_no_callbacks(self):
        j = MayBe.just(5)
        n = MayBe.nothing()
        self.assertIsNone(j.match())
        self.assertIsNone(n.match())

    def test_match_partial_on_just(self):
        j = MayBe.just(5)
        # only nothing callback, but value is Just
        result = j.match(nothing=lambda: "fallback")
        self.assertIsNone(result)

    def test_match_partial_on_nothing(self):
        n = MayBe.nothing()
        # only just callback, but value is Nothing
        result = n.match(just=lambda x: x * 2)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
