# `clientity` -- changelog

## [0.1.6] -- Jan. 6th, 2026

### Added
+ **Execution utilities**: `http.execute` and `http.respond` extracted from Client/Namespace
+ **`groupings()` iterator**: On `Grouping` base class for iterating nested Resource/Namespace
+ **Integration test suite**: Full flow tests for Client → Resource → Namespace → Endpoint

### Changed
* **Operator mappings**: `%` for query model, `&` for prehook, `|` for posthook (precedence fix)
* **Phantom types for DX**: Operators return `Bound[Endpoint]` to type checkers via `TYPE_CHECKING` block
* **`embody()` fallback**: Now calls `dictate()` for unknown object types

### Fixed
* `Resource.__nest__` / `Namespace.__nest__` double-prepend bug (strips child location prefix)
* `Client.__sourced` nested grouping re-nesting (bypass `__setattr__` with `object.__setattr__`)
* `Grouping.__setattr__` changed `if` to `elif` for Grouping check
* Various type hints: `Stringable` for URL params, `respond` overloads, `AsyncInterface` return types

---

## Current Agenda

### Immediate
1. Revisit DX typing for nested resource/namespace attribute access (`client.users.list` shows `Any`)

### Pinned for Later
1. IDE typing / signatures (`Unpack[TypedDict]` for kwargs autocomplete)
2. Iterable response models
3. WebSocket clients
4. CLI generation

## [0.1.5] -- Jan. 4th, 2026

### Added
+ **Grouping system**: Base `Grouping` class for organizing endpoints
  - `Resource`: Dependent grouping with relative `location`, prepends path to nested endpoints
  - `Namespace`: Independent grouping with absolute `base`, optional own `interface`/`adapter`
  - Nested resource support with `__nest__` and `Located` protocol
  - `endpoints()` iterator utility on base `Grouping`

+ **Adapters**: Library-specific request building and sending
  - `Adapter` ABC with `build()` and `send()` methods
  - `RequestsAdapter` for `requests` library
  - `HttpxAdapter` for `httpx` library  
  - `AiohttpAdapter` for `aiohttp` library (fire-and-forget or session reuse modes)
  - `adapt()` factory function with `Compatible()` detection

+ **Utilities**:
  - `synced`: Inverse of `asynced` - wraps async callables to sync with `eval` option
  - `dictate`: Extract dict from model instances (pydantic, dataclass, etc.)
  - `sift.instructions()`: Convenience method for sifting with `Instructions`
  - `domain()`: Extract domain name from URL
  - `bound()`: Moved to utils/typers.py

+ **Type hints**:
  - `Located` protocol for objects with `location` attribute
  - `Requested` hint for embody input
  - `Responded` hint for execution return type
  - `WrappedEndpoint` = `Union[Endpoint, Bound[Endpoint]]`

### Changed
* `Location.__new__`: Now idempotent - returns existing Location unchanged
* `Location.name`: Property returning PascalCase name from path segments (excluding params)
* `Endpoint.mutate()`: Public method exposing `__copy` for modification
* `Client.__init__`: Now accepts `Interfacing` (interface or callable returning interface)
* `embody()`: Parameter type changed from `Requesting` to `Optional[Requested]`

### Fixed
* `synced`/`asynced` overload signatures for proper type inference
* Name mangling issues with abstract methods (`__wrap__` -> `__wrap__`)

---

## Current Agenda

### Immediate
1. Update `Client` to handle `Resource` and `Namespace` assignment in `__setattr__`
2. Extract shared execution logic from `Client.__x` and `Namespace.__x` into utility
3. Test full flow: Client -> Resource -> Endpoint -> execution

### Pending
- IDE typing / signatures (`Unpack[TypedDict]` for kwargs autocomplete)
- `domain()` utility implementation (currently raises)

### Pinned for Later
1. **Iterable response models**: Handle `list[Item]` responses, sequence parsing, `__responds__` for collections
2. **WebSocket clients**: Different protocol handling, maybe `ws_endpoint` or separate client type
3. **CLI generation**: `clientity generate --source /path/to/spec --destination /path/to/client.py` from OpenAPI/FastAPI/Flask specs

---

## [0.1.0] -- Dec. 29, 2025
* Initial project scaffolding and core primitives

### Added
+ **Project Structure**: Established base package layout with `core/`, `exc/`, and logging infrastructure
+ **Logging**: Configurable logging via `CLIENTITYLOGS` environment variable with `devnull` fallback
+ **Exceptions**: Base `ClientityError` exception class

+ **Protocols**:
  - `SyncInterface` / `AsyncInterface`: Runtime-checkable protocols for HTTP engines (requests, httpx, aiohttp, etc.)
  - `Requestable`: Protocol for request models with `__request__()` method and optional `RequestKey` class var
  - `Responsive`: Protocol for response models with `__respond__()` classmethod

+ **Primitives**:
  - `Location`: Path fragment class with parameter extraction (`{id}`), `/` operator for joining, and `resolve()` for substitution
  - `URL`: Full URL class combining base + location, with `resolve()` for final string output
  - `MethodType`: Literal type for HTTP methods with constants (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS`)
  - `Hooks`: Container for pre/post request hooks with async conversion via `before`/`after` properties
  - `Instructions`: Core instruction set containing method, location, hooks, and models (querying, requesting, responding) with `merge()` and `prepend()` methods

+ **Endpoint**:
  - `Endpoint`: Builder class for constructing `Instructions` via method chaining
  - `endpoint` factory with method-specific properties (`.get`, `.post`, `.put`, etc.)
  - Operator overloads: `@` (location), `|` (hooks), `<<` (request models), `>>` (response model)

+ **Utilities**:
  - `asynced`: Utility for wrapping sync callables as async
  - `embody`: Utility for encoding request objects to `(key, data)` tuples

### Architecture
+ **Reverse-cascade design**: Endpoints return instruction sets that bubble up to client for execution
+ **Engine agnostic**: Interface protocols accept any HTTP library that quacks correctly
+ **Sift pattern** (pending): kwargs distributed to path/query/body based on model field introspection

## [0.0.0] -- Dec. 28, 2025
* Project Initialized
