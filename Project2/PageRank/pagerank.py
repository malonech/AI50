import os
import random
import re
import sys
from collections import Counter

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.

    Corpus is a python dictionary mapping a page name to all linked pages
    page is a string representing which page the surfer is currently on
    Damping Factor is a floating point number representing the damping
        factor to be used in generating probabilities.
    """

    """
    METHOD:
    All pages linked on current page are equally likely to be picked in 
    damping_factor range of values (0.85). So their likelihood is 
    damping_factor divided by number of linked pages.
    
    All pages are equally likely to be picked in (1 - damping_factor),
    so divide that by sum of all possible pages to get the chance of 
    each page. sum corresponding probabilities.
    
    """
    # Initialize return dictionary
    probabilities = dict()
    # First check if no links
    if not corpus[page]:
        prob_all = 1 / len(corpus)
        for page in corpus:
            probabilities[page] = prob_all
        return probabilities

    # Otherwise
    # determine number of linked sites and total links
    n_linked = len(corpus[page])
    n_total = len(corpus)

    # Determine chance of linked and random site chosen
    prob_linked = damping_factor / n_linked
    prob_random = (1 - damping_factor) / n_total

    # Total prob for linked
    prob_linked_total = prob_linked + prob_random

    #determine total probability for linked site
    for link in corpus:
        if link in corpus[page]:
            probabilities[link] = prob_linked_total
        else:
            probabilities[link] = prob_random
    return probabilities


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # First sample and its PD
    sample_page = random.choice(list(corpus.keys()))
    # first_distribution = transition_model(corpus, first_sample, damping_factor)

    #Initialize data list for pages chosen while sampling
    data = []
    data.append(sample_page)
    #Loop through samples and add to data
    for _ in range(n):
        sample_pd = transition_model(corpus, sample_page, damping_factor)
        sample_page = random.choices(list(sample_pd.keys()), weights=sample_pd.values())[0]
        data.append(sample_page)
    count = Counter(data)

    #Convert count into sample probabilities
    sample_probabilities = dict()
    for site in count:
        sample_probabilities[site] = count[site] / n

    return sample_probabilities



def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Number of pages in the corpus
    N = len(corpus)

    # Initialize Probability dictionary and last iteration
    probabilities = dict()
    last_probabilities = dict()

    #Set initial probabilities to be 1/N
    for site in corpus:
        probabilities[site] = 1 / N
        last_probabilities[site] = 0

    #Create list of site with no links
    zero_link_sites = list()
    for site in corpus:
        if not corpus[site]:
            zero_link_sites.append(site)

    #Iterative loop
    while True:

        for site in probabilities:
            sum= 0
            linked_from_list = list()

            #Get list of sites linking to current site
            for linked_from in probabilities:
                if site == linked_from:
                    continue
                elif site in corpus[linked_from]:
                    linked_from_list.append(linked_from)
                if linked_from in zero_link_sites:
                    linked_from_list.append(linked_from)
            for link in linked_from_list:
                sum += probabilities[link] / len(corpus[link])
            # Copy previous site prob and then update original
            last_probabilities[site] = probabilities[site]
            probabilities[site] = (1 - damping_factor) / N + damping_factor * sum

        #Check if iteration complete
        i = 0
        for site in probabilities:
            if abs(probabilities[site] - last_probabilities[site]) < 0.001:
                i += 1
        if i == len(probabilities):
            return probabilities




if __name__ == "__main__":
    main()

