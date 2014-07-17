# Pyschema

Simple, composable, and extensible schema validation and coercion tool. Based on 
[schema](https://github.com/halst/schema) but with more extensible code, added syntax
features and active development.

## Installation

Not on pypi yet, so you'll have to clone the repo. Sorry!

## Use

### Basic Validation

Create a `Schema` object by passing a map, type, callable, or list to `Schema`. Then
call `coerce` on that object to get a True or False validation.

```.py

s = Schema({
    'name': str,
    'age': int,
})
assert s.validate({'name': 'Chen', 'age': 26})

s = Schema([int])
assert s.validate([1, 2, 3, 4])
assert not s.validate([1, 'abc', 3, 4])

s = Schema(str)
assert s.validate('abc')
```

### Schema descriptors

There's also support for custom Schema descriptors for optional values, regexes,
and custom validation functions. You can also compose them. 

```.py
def cardchecksum(n):
    # validates credit card number, returns True or False
    ...

s = Schema({
    'creditcard': Check(cardchecksum),
    'zipcode': Optional(int, default=10101)
    'email': Optional(Email()) 
})
assert s.validate({ 'creditcard': 12345678911111111 })
assert not s.validate({ 'creditcard': 12345678911111111, 
                        'email': 'notanemail' })
assert s.validate({ 'creditcard': 12345678911111111, 
                    'email': 'validemail@abc.com' })
```

### Logical Combinators

You can mix and match Schemas with `And` and `Or`. The results of the logical
operators `&` and `|` are syntatical sugar that produce `And` and `Or`, respectively.

Note: Not yet implemented :). 

### Coercion

Some schema descriptors can return coerced versions of your values. 

You can also create a copy of your data with the values coerced by callables using
the `Coerce` descriptor with the `coerce` function.  

```python
s = Schema({
    'age': Coerce(int)
})
print s.coerce({'age': '26'})

>>> { 'age': 26 }
```
