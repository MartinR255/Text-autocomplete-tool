import operator

class MarkovChain:

    def __init__(self, data) -> None:
        self._model = self._build_model(data)
    

    def _build_model(self, data):
        model = {}

        for sentence in data:
            for word_index in range(len(sentence) - 1):
                current_state = sentence[word_index]
                next_state = sentence[word_index + 1]

                if current_state not in model:
                    model[current_state] = { next_state : 1 }
                elif next_state not in model[current_state]:
                    model[current_state][next_state] = 1
                else:
                    model[current_state][next_state] += 1

        return self._compute_transitions_probabilities(model)
    

    def _compute_transitions_probabilities(self, model):
        for current_state, transition_states in model.items():

            # total transition form state
            total_transitions = sum(transition_states.values()) 
            for destination_state, transition_count  in transition_states.items():
                model[current_state][destination_state] = transition_count / total_transitions

        return model
    

    def get_top_three_possible_states(self, state) -> list:
        state_lower = state.lower()
        if state_lower in self._model:
            return sorted(self._model[state_lower], key=operator.itemgetter(1), reverse=True)[:3]
        return []


    