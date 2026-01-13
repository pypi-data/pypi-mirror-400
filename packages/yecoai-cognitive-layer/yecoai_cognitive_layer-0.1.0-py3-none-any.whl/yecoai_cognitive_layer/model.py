import math
import json
import os

class CognitiveModel:
    def __init__(self, weights=None):
        self.classes_ = ["Normal", "Loop", "Amnesia"]
        self.coefs_ = None
        self.intercepts_ = None
        self.is_fitted = False
        if weights:
            self.coefs_ = weights['coefs']
            self.intercepts_ = weights['intercepts']
            self.classes_ = weights['classes']
            self.is_fitted = True

    def _dot(self, a, b):
        result = [0.0] * len(b[0])
        for i in range(len(a)):
            for j in range(len(b[0])):
                result[j] += a[i] * b[i][j]
        return result

    def _add(self, a, b):
        return [x + y for x, y in zip(a, b)]

    def _relu(self, a):
        return [max(0, x) for x in a]

    def predict(self, feature_vector, features_dict=None):
        if features_dict is not None:
            if features_dict.get("semantic_coherence", 0) > 0.45 and features_dict.get("normal_pattern_flag", 0) > 0.5:
                return "Normal", {"Normal": 0.98, "Loop": 0.01, "Amnesia": 0.01}
            
            if features_dict.get("repetition_score", 0) > 0.8 or features_dict.get("max_ngram_repeat", 0) > 0.7:
                return "Loop", {"Normal": 0.01, "Loop": 0.98, "Amnesia": 0.01}

            if features_dict.get("adversarial_score", 0) > 0.5 and features_dict.get("repetition_score", 0) < 0.6:
                return "Amnesia", {"Normal": 0.01, "Loop": 0.01, "Amnesia": 0.98}
            
            if features_dict.get("struct_loop_flag", 0) > 0.5 and features_dict.get("semantic_coherence", 0) < 0.3:
                return "Loop", {"Normal": 0.02, "Loop": 0.96, "Amnesia": 0.02}
            
            if features_dict.get("digit_density", 0) > 0.7 and features_dict.get("length", 0) > 1.2:
                return "Loop", {"Normal": 0.05, "Loop": 0.90, "Amnesia": 0.05}

            if features_dict.get("salad_diff", 0) > 0.35 and features_dict.get("semantic_coherence", 0) < 0.45:
                return "Amnesia", {"Normal": 0.05, "Loop": 0.05, "Amnesia": 0.90}
            
            if features_dict.get("adversarial_score", 0) > 0.5 and features_dict.get("semantic_coherence", 0) < 0.25:
                return "Amnesia", {"Normal": 0.01, "Loop": 0.01, "Amnesia": 0.98}
            
            if features_dict.get("word_salad_score", 0) > 0.55 and features_dict.get("semantic_coherence", 0) < 0.2:
                return "Amnesia", {"Normal": 0.05, "Loop": 0.05, "Amnesia": 0.90}

        if not self.is_fitted:
            return "Normal", {"Normal": 1.0, "Loop": 0.0, "Amnesia": 0.0}

        layer_input = feature_vector
        for i in range(len(self.coefs_)):
            z = self._add(self._dot(layer_input, self.coefs_[i]), self.intercepts_[i])
            if i < len(self.coefs_) - 1:
                layer_input = self._relu(z)
            else:
                scores = z
        
        max_score = max(scores)
        exp_scores = [math.exp(s - max_score) for s in scores]
        sum_exp = sum(exp_scores)
        probs = [s / sum_exp for s in exp_scores]
        
        max_prob_idx = probs.index(max(probs))
        prediction = self.classes_[max_prob_idx]
        scores_dict = {cls: float(prob) for cls, prob in zip(self.classes_, probs)}
        
        return prediction, scores_dict

    @classmethod
    def load_from_json(cls, path):
        if os.path.exists(path):
            with open(path, 'r') as f:
                weights = json.load(f)
            return cls(weights)
        return cls()
