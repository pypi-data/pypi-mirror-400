# Changelog

## [1.0.3] - 2026-01-05

### Added

- `expect(message)` pour `MayBe` et `Result`: comme `unwrap()` mais avec message d'erreur personnalisé
- `to_option()` pour `MayBe` et `Result`: retourne la valeur ou `None`
- `match(just=..., nothing=...)` pour `MayBe`: pattern matching ergonomique
- `match(ok=..., err=...)` pour `Result`: pattern matching ergonomique (err reçoit msg, code, details)
- `Result.from_dict()`: construit un `Result` depuis un dict (réciproque de `to_dict()`)

### Changed

- L'opérateur `>>` lève désormais un `TypeError` si la fonction ne retourne pas un `MayBe`/`Result`

## [1.0.2] - 2025-12-31

### Added

- Support du typage générique pour `MayBe` et `Result` via `__class_getitem__`
  - Permet d'écrire `MayBe[User]` ou `Result[dict[str, Any], ErrorCodes]`
  - Compatible avec les outils de typage statique (mypy, pyright)

### Changed

- Exemple renommé: `examples/abc.py` → `examples/objects.py`

## [1.0.1] - 2025-12-22

### Changed

- README.md: affichage conforme sur pypi.org

## [1.0.0] - 2025-12-22

### Added

- `MayBe` monad: `just()`, `nothing()`, `map()`, `flat_map()`, opérateurs `>>` et `|`
- `Result` monad: `ok()`, `err()`, `map()`, `map_err()`, `flat_map()`, `and_then()`, `to_dict()`
- Erreurs structurées avec `code` et `details` optionnels
- Type stubs pour autocomplétion (`.pyi`)
