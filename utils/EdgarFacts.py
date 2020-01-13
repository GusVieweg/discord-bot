class EdgarFacts():
    def __init__(self):
        self.facts = [
            "Edgar Allan Poe is widely considered America's first well-known professional writer.",
            "Edgar Allan Poe published his first book, _Tamerlane_, when he was just eighteen!",
            "When his adopted father died, Edgar Allan Poe was left out of the will.",
            "Edgar Allan Poe's death is a mystery. In 1849, he went missing for five days and was found decrepid and delirious in Baltimore. He died in the hospital at 40. No autopsy was performed. The cause of death was listed as 'congestion of the brain.'",
            "Edgar Degas is considered as one of the founders of the art movement impressionism.",
            "Edgar Degas's most famous painting is _L'Absinthe (The Absinthe Drinker)_.",
            "Edgar Degas died in Paris in September 27, 1917, having never married.",
            "Edgar Degas infamously referred to dancers he drew as his little monkey girls.",
            'In 1996, Johnny and Edgar Winter sued DC Comics for defamation after an issue of _Jonah Hex: Riders of the Worm and Such_ featured two worm-like villains named Johnny and Edgar Autumn. The Supreme Court of California ultimately found that "although the fictional characters Johnny and Edgar Autumn are less-than-subtle evocations of Johnny and Edgar Winter, the books do not depict plaintiffs literally," and that, "the characters and their portrayals do not greatly threaten plaintiffs’ right of publicity." It was a landmark case that, essentially, gave comics free reign to parody and lampoon figures in the public eye.',
            "Edgar Winter is an albino human.",
            "Edgar Winter is the seventh most famous person from Beaumont, Texas according to famousbirthdays.com.",
            "Edgar Winter isn't dead yet.",
            "J. Edgar Hoover sang in his school choir.",
            "J. Edgar Hoover is the only civil servant to have lain in state.",
            "Regarding rumours of J. Edgar Hoover's (homo)sexuality, historians John Stuart Cox and Athan G. Theoharis concluded that he was most likely asexual.",
            "Under J. Edgar Hoover's FBI, agents were directed to seize all pornographic materals uncovered in their investigations and forward them _to Hoover personally_. He kept a large collection, possibly the world's largest, of films, photographs, and written materials, with particular emphasis on nude photos of celebrities. Hoover reportedly used these for his own titillation, as well as holding them for blackmail purposes."
        ]
    
    def get_edgar_fact(self):
        import random
        return random.choice(self.facts)
