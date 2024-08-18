import operator

class MarkovChain:

    def __init__(self, data):
        self._model = {}
        self._prefix_model = {}

        self._build_model(data)


    def _insert_into_model(self, model, current_state, next_state):
            if current_state not in model:
                model[current_state] = { next_state : 1 }
            elif next_state not in model[current_state]:
                model[current_state][next_state] = 1
            else:
                model[current_state][next_state] += 1        


    def _build_prefix_model(self, word):
        for i in range(len(word)):
            prefix_state = word[:i]
            next_state = word[i:]

            self._insert_into_model(self._prefix_model, prefix_state, next_state)


    def _build_model(self, data):
        for sentence in data:
            if len(sentence) == 0: continue

            self._build_prefix_model(sentence[0])

            for word_index in range(len(sentence) - 1):
                current_state = sentence[word_index]
                next_state = sentence[word_index + 1]
                self._insert_into_model(self._model, current_state, next_state)

                self._build_prefix_model(next_state)
                
        self._model = self._compute_transitions_probabilities(self._model)
        self._prefix_model = self._compute_transitions_probabilities(self._prefix_model)
         
    
    def _compute_transitions_probabilities(self, model):
        for current_state, transition_states in model.items():
            # total transition form state
            total_transitions = sum(transition_states.values()) 
            for destination_state, transition_count  in transition_states.items():
                model[current_state][destination_state] = transition_count / total_transitions

        return model
    

    def _get_top_three_possible_states(self, state, model):
        state_lower = state.lower()
        if state_lower in model:
            return sorted(model[state_lower].items(), key=operator.itemgetter(1), reverse=True)[:3]
        return []
    

    def get_word(self, state):
        return self._get_top_three_possible_states(state, self._model)


    def get_word_with_prefix(self, state):
        return self._get_top_three_possible_states(state, self._prefix_model)

    