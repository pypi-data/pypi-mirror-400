import k3pattern

k3pattern.common_prefix("abc", "abd")  # 'ab'
k3pattern.common_prefix((1, 2, "abc"), (1, 2, "abd"))  # (1, 2, 'ab')
k3pattern.common_prefix((1, 2, "abc"), (1, 2, "xyz"))  # (1, 2); empty prefix of 'abc' and 'xyz' is removed
k3pattern.common_prefix((1, 2, (5, 6)), (1, 2, (5, 7)))  # (1, 2, (5,) )
k3pattern.common_prefix("abc", "abd", "abe")  # 'ab'; common prefix of more than two
