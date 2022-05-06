from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    #If knight, then not a knave
    Biconditional(AKnight, Not(AKnave)),
    # If knave, then not a knight
    Biconditional(AKnave, Not(AKnight)),
    # Knowledge: If Knight, then Knight&Knave True
    Implication(AKnight, And(AKnight, AKnave))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    # One or the other for A
    Biconditional(AKnight, Not(AKnave)),
    # One or the other for B
    Biconditional(BKnight, Not(BKnave)),
    # Knowledge. If A Knight, then both AKnave and BKnave
    Implication(AKnight, And(AKnave, BKnave)),
    Implication(AKnave, Or(AKnight, BKnight))

)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # One or the other for A
    Biconditional(AKnight, Not(AKnave)),
    # One or the other for B
    Biconditional(BKnight, Not(BKnave)),
    # If AKnight, then both same kind, and vice versa
    Biconditional(AKnight, Or(And(AKnight, BKnight), And(AKnave, BKnave))),
    # If BKnight, then both opposite kind, and nice versa
    Biconditional(BKnight, Or(And(AKnight, BKnave), And(AKnave, BKnight)))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    #One or the other for all three (A, B, C)
    Biconditional(AKnight,Not(AKnave)),
    Biconditional(BKnight,Not(BKnave)),
    Biconditional(CKnight,Not(CKnave)),

    # A says either "I am a knight." or "I am a knave.", but you don't know which.
    Implication(AKnight, Or(AKnight, AKnave)),
    Implication(AKnave, Not(Or(AKnight, AKnave))),

    # B says "A said 'I am a knave'."
    #If A is Knave, the sentence is a lie, if Knight, then true. B must be Lying
    Implication(BKnight, Implication(AKnight, BKnave)),
    Implication(BKnight, Implication(AKnave, Not(BKnave))),


    # B says "C is a knave."
    Implication(BKnight, CKnave),
    Implication(BKnave, CKnight),

    # C says "A is a knight."
    Implication(CKnight, AKnight),
    Implication(CKnave, Not(AKnight)),
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
