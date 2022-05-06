import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    """
    people has index of each person, their parents and if they have the trait.
    one-gene is a set of all people for whom we want to compute the probability 
        that they have one copy of the gene.
    two_genes is a set of all people for whom we want to compute the probability 
        that they have two copies of the gene
    have_trait is a set of all people for whom we want to compute the probability 
        that they have the trait.
    """
    # Initilize probablility variable
    probability = float(1)

    # Loop through people
    for person in people:
        # Who are their parents, if any
        mother = people[person]['mother']
        father = people[person]['father']

        # Deteremine num genes, if any
        if person in one_gene:
            gene = 1
        elif person in two_genes:
            gene = 2
        else:
            gene = 0

        # Do they have the trait? T/F
        trait = person in have_trait

        # No parents, unconditional probability
        if mother is None and father is None:
            probability *= PROBS['gene'][gene]
        # Otherwise, calculate conditional probability based on parents
        else:
            # Initialise probabilities that they pass gene
            # mother_pass = 0
            # father_pass = 0
            parent_pass = {mother: 0, father: 0}

            for parent in parent_pass:
                # Prob they pass with two genes
                if parent in two_genes:
                    parent_pass[parent] = 1 - PROBS['mutation']
                # Prob they pass with one genes. mutations cancel
                elif parent in one_gene:
                    parent_pass[parent] = 0.5
                # Prob they pass with no gene
                else:
                    parent_pass[parent] = PROBS['mutation']

            # Calc probability that person got their gene
            # If both genes, each parent passed a gene
            if person in two_genes:
                probability *= parent_pass[mother] * parent_pass[father]
            # If one gene, only one parent passed the gene
            elif person in one_gene:
                probability *= (parent_pass[mother] * (1 - parent_pass[father]) +
                                parent_pass[father] * (1 - parent_pass[mother]))
            # No gene, prob that parents didn't pass gene
            else:
                probability *= (1 - parent_pass[father]) * (1 - parent_pass[mother])

        # Multiply by probability has trait (or not) based on genes
        probability *= PROBS["trait"][gene][trait]
    return probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    # Loop through people
    for person in probabilities:
        # Check persons gene count
        if person in two_genes:
            gene = 2
        elif person in one_gene:
            gene = 1
        else:
            gene = 0

        # Check if they have the trait. T/F
        trait = person in have_trait

        # Update probabilities with p based on gene and trait
        probabilities[person]['gene'][gene] += p
        probabilities[person]['trait'][trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    # Loop through people
    for person in probabilities:
        # Sum all probabilities for the person
        for column in probabilities[person]:
            total = sum(dict(probabilities[person][column]).values())
            # Divide each probability by the total, to get it normalised to 1
            for value in probabilities[person][column]:
                probabilities[person][column][value] /= total

if __name__ == "__main__":
    main()
