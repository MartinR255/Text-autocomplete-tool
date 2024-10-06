import operator

class MarkovChain:

    def __init__(self, data, n):
        self._chain = {}
        self._prefix_chain = {}
        self._build_chain_of_nth_order(data, n)


    '''
    Desc: Inserts a state transition into the chain
    Params:
        chain: dict - The chain to insert into
        current_state: tuple - The current state
        next_state: str - The next state
    Returns: None
    '''
    def _insert_into_chain(self, chain, current_state, next_state):
            if current_state not in chain:
                chain[current_state] = { next_state : 1 }
            elif next_state not in chain[current_state]:
                chain[current_state][next_state] = 1
            else:
                chain[current_state][next_state] += 1        


    '''
    Desc: Builds the prefix chain for word completion
    Params:
        words: list - The list of words to build the prefix chain from
        n: int - The order of the Markov chain
    Returns: None
    '''
    def _build_prefix_chain(self, words, n):
        last_word = words[-1]
        for i in range(1,len(last_word)):
        
            q = words[:n-1]
            q.append(last_word[:i])
            prefix_state = tuple(q)
            next_state = last_word[i:]

            self._insert_into_chain(self._prefix_chain, prefix_state, next_state)


    '''
    Desc: Builds the nth order Markov chain
    Params:
        data: list - The input data to build the chain from
        n: int - The order of the Markov chain
    Returns: None
    '''
    def _build_chain_of_nth_order(self, data, n):
        for sentence in data:
            if len(sentence) == 0 or len(sentence) < n: continue

            for i in range(len(sentence) - n):
                current_state = sentence[i:i+n]
                next_state = sentence[i+n]
                self._insert_into_chain(self._chain, tuple(current_state), next_state)

                current_state = sentence[i:i+n]
                self._build_prefix_chain(current_state, n)

        self._chain = self._compute_transitions_probabilities(self._chain)
        self._prefix_chain = self._compute_transitions_probabilities(self._prefix_chain)


    '''
    Desc: Computes transition probabilities for the Markov chain
    Params:
        chain: dict - The chain to compute probabilities for
    Returns: dict - The Markov chain with computed probabilities
    '''
    def _compute_transitions_probabilities(self, chain):
        for current_state, transition_states in chain.items():
            total_transitions = sum(transition_states.values()) 
            for destination_state, transition_count  in transition_states.items():
                chain[current_state][destination_state] = transition_count / total_transitions

        return chain
    

    '''
    Desc: Gets the top three possible states from the chain
    Params:
        state: tuple - The current state
        chain: dict - The Markov chain to get states from
    Returns: list - Top three possible states with their probabilities
    '''
    def _get_top_three_possible_states(self, state, chain):
        state_lower = tuple(s.lower() for s in state)
        if state_lower in chain:
            return sorted(chain[state_lower].items(), key=operator.itemgetter(1), reverse=True)[:3]
        return []
    

    '''
    Desc: Gets the top three possible next words
    Params:
        state: tuple - The current state
    Returns: list - Top three possible next words with their probabilities
    '''
    def get_words(self, state):
        return self._get_top_three_possible_states(state, self._chain)


    '''
    Desc: Gets the top three possible word completions with given prefix
    Params:
        state: tuple - The current state 
    Returns: list - Top three possible word completions with their probabilities
    '''
    def get_words_with_prefix(self, state):
        return self._get_top_three_possible_states(state, self._prefix_chain)


