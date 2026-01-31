import worble

worble.load('/usr/share/dict/american-english')

m,c,e,p = worble.eval_guess2('HORSE', 'EARTH')
assert p == '🟨⬛🟩⬛🟨'

m,c,e,p = worble.eval_guess2('MOSSY', 'SORRY')
assert p == '🟨🟩⬛⬛🟩'

m,c,e,p = worble.eval_guess2('SORRY', 'MOSSY')
assert p == '⬛🟩🟨⬛🟩'

m,c,e,p = worble.eval_guess2('NANNY', 'NAPPY')
assert p == '🟩🟩⬛⬛🟩'

res, p, state = worble.play_round('LETUP', 'ORATE')
assert p.startswith('1 ⬛⬛⬛🟨🟨')
res, p, state = worble.play_round('LETUP', 'FEINT', state)
assert p.startswith('2 ⬛🟩⬛⬛🟨')
res, p, state = worble.play_round('LETUP', 'TELLY', state)
assert p.startswith('3 🟨🟩🟨⬛⬛')
assert 'LETUP' in state['options']



