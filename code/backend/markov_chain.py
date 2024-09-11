import operator

class MarkovChain:

    def __init__(self, data, n):
        self._model = {}
        self._prefix_model = {}
        self._build_model_of_nth_order(data, n)


    def _insert_into_model(self, model, current_state, next_state):
            if current_state not in model:
                model[current_state] = { next_state : 1 }
            elif next_state not in model[current_state]:
                model[current_state][next_state] = 1
            else:
                model[current_state][next_state] += 1        


    def _build_prefix_model(self, words, n):

        last_word = words[-1]
        for i in range(1,len(last_word)):
        
            q = words[:n-1]
            q.append(last_word[:i])
            prefix_state = tuple(q)
            next_state = last_word[i:]

            self._insert_into_model(self._prefix_model, prefix_state, next_state)


    def _build_model_of_nth_order(self, data, n):
        for sentence in data:
            if len(sentence) == 0 or len(sentence) < n: continue

            for i in range(len(sentence) - n):
                current_state = sentence[i:i+n]
                next_state = sentence[i+n]
                self._insert_into_model(self._model, tuple(current_state), next_state)

                current_state = sentence[i:i+n]
                self._build_prefix_model(current_state, n)

        self._model = self._compute_transitions_probabilities(self._model)
        self._prefix_model = self._compute_transitions_probabilities(self._prefix_model)


    def _compute_transitions_probabilities(self, model):
        for current_state, transition_states in model.items():
            total_transitions = sum(transition_states.values()) 
            for destination_state, transition_count  in transition_states.items():
                model[current_state][destination_state] = transition_count / total_transitions

        return model
    

    def _get_top_three_possible_states(self, state, model):
        state_lower = tuple(s.lower() for s in state)
        if state_lower in model:
            return sorted(model[state_lower].items(), key=operator.itemgetter(1), reverse=True)[:3]
        return []
    

    def get_words(self, state):
        return self._get_top_three_possible_states(state, self._model)


    def get_words_with_prefix(self, state):
        return self._get_top_three_possible_states(state, self._prefix_model)


