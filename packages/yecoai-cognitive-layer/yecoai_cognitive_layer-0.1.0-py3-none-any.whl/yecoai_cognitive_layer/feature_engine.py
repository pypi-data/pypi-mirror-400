import re
import math
from collections import Counter

class FeatureEngine:
    def __init__(self):
        self.stop_words = set([
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "it", "this", "that", "you", "i", "me", "my",
            "et", "in", "est", "non", "ad", "ut", "cum", "quod", "qui", "que", "sed", "si", "per", "ex", "de", "esse", "sunt",
            "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "也", "他", "一个", "说", "去", "谢谢", "我们", "你们", "他们",
            "di", "e", "il", "la", "che", "un", "una", "per", "con", "su", "mi", "ti", "si", "è", "ma", "ed", "se", "perché", "come", "molto", "sono", "ho", "ha", "abbiamo", "hanno"
        ])
        
        self.reset_keywords = set([
            "reset", "forget", "clear", "wipe", "purge", "override", "nullify", "reboot",
            "dimentica", "resetta", "cancella", "vuoto", "ignora", "pulisci",
            "重置", "忘记", "清除", "清空", "重启"
        ])

        self.loop_keywords = set([
            "loop", "ripeti", "repeat", "redundancy", "stuck", "bloccato", "endless",
            "循环", "重复", "卡住", "再次", "ancora", "infinito"
        ])
        
        self.normal_patterns = set([
            "hello", "hi", "thanks", "thank", "please", "could", "would", "how", "what", "can", "help", "need", "write", "explain", "describe",
            "salve", "ave", "gratias", "quomodo", "quis", "quid", "ubi", "quando", "ciao", "grazie", "per favore", "potresti", "spiega", "descrivi",
            "opera", "poesia", "storia", "scienza", "libro", "film", "musica", "viaggio", "cibo", "lavoro", "pomeriggio", "sera", "notte", "giorno",
            "你好", "谢谢", "请", "怎么", "什么", "哪里", "帮助", "解释", "描述", "分析", "研究", "讨论", "建议"
        ])

    def _tokenize(self, text):
        return re.findall(r'\b\w+\b|[\u4e00-\u9fff]', text.lower())

    def _calculate_entropy(self, items):
        if not items:
            return 0.0
        counts = Counter(items)
        total = len(items)
        probs = [count / total for count in counts.values()]
        return -sum(p * math.log2(p) for p in probs)

    def extract_features(self, text):
        if not text:
            return [0.0] * 22, {
                "length": 0, "unique_ratio": 0.0, "entropy": 0.0, "repetition_score": 0.0, "max_ngram_repeat": 0.0,
                "stop_word_ratio": 0.0, "alpha_ratio": 0.0, "avg_token_len": 0.0, "reset_flag": 0.0, "loop_keyword_flag": 0.0, 
                "punc_density": 0.0, "vowel_ratio": 0.0, "normal_pattern_flag": 0.0, "char_repetition": 0.0, "word_salad_score": 0.0, "token_diversity": 0.0,
                "entropy_2gram": 0.0, "adversarial_score": 0.0, "struct_loop_flag": 0.0, "semantic_coherence": 0.0,
                "salad_diff": 0.0, "digit_density": 0.0
            }

        tokens = self._tokenize(text)
        num_tokens = len(tokens)
        if num_tokens == 0:
             return [0.0] * 22, {
                "length": 0, "unique_ratio": 0.0, "entropy": 0.0, "repetition_score": 0.0, "max_ngram_repeat": 0.0,
                "stop_word_ratio": 0.0, "alpha_ratio": 0.0, "avg_token_len": 0.0, "reset_flag": 0.0, "loop_keyword_flag": 0.0,
                "punc_density": 0.0, "vowel_ratio": 0.0, "normal_pattern_flag": 0.0, "char_repetition": 0.0, "word_salad_score": 0.0, "token_diversity": 0.0,
                "entropy_2gram": 0.0, "adversarial_score": 0.0, "struct_loop_flag": 0.0, "semantic_coherence": 0.0,
                "salad_diff": 0.0, "digit_density": 0.0
            }

        length = math.log1p(num_tokens)
        unique_tokens = set(tokens)
        unique_ratio = len(unique_tokens) / num_tokens
        entropy = self._calculate_entropy(tokens)

        repetition_score = 0.0
        if num_tokens >= 3:
            ngrams = list(zip(tokens, tokens[1:], tokens[2:]))
            ngram_counts = Counter(ngrams)
            repeated_ngrams = sum(count for count in ngram_counts.values() if count > 1)
            repetition_score = repeated_ngrams / len(ngrams)
        
        max_ngram_repeat = 0.0
        if num_tokens >= 5:
             ngrams_4 = list(zip(tokens, tokens[1:], tokens[2:], tokens[3:]))
             if len(ngrams_4) > 1:
                 max_ngram_repeat = Counter(ngrams_4).most_common(1)[0][1] / len(ngrams_4)

        stop_count = sum(1 for t in tokens if t in self.stop_words)
        stop_word_ratio = stop_count / num_tokens
        alpha_count = sum(1 for t in tokens if re.match(r'[\w\u4e00-\u9fff]', t))
        alpha_ratio = alpha_count / num_tokens
        avg_token_len = sum(len(t) for t in tokens) / num_tokens / 10.0
        reset_flag = 1.0 if any(t in self.reset_keywords for t in tokens) else 0.0
        loop_keyword_flag = 1.0 if any(t in self.loop_keywords for t in tokens) else 0.0

        punc_chars = re.findall(r'[^\w\s\u4e00-\u9fff]', text)
        punc_density = len(punc_chars) / len(text) if len(text) > 0 else 0.0

        text_lower = text.lower()
        vowels = len(re.findall(r'[aeiouàèìòù]', text_lower))
        alphas = len(re.findall(r'[a-zàèìòù]', text_lower))
        vowel_ratio = vowels / alphas if alphas > 0 else 0.0

        normal_pattern_flag = 1.0 if any(t in self.normal_patterns for t in tokens) else 0.0
        char_counts = Counter(text_lower.replace(" ", ""))
        char_repetition = (len(text_lower.replace(" ", "")) - len(char_counts)) / len(text_lower.replace(" ", "")) if len(text_lower.replace(" ", "")) > 0 else 0.0
        word_salad_score = (unique_ratio * (1.0 - stop_word_ratio)) if num_tokens > 3 else 0.0
        token_diversity = entropy / (math.log2(num_tokens) + 1e-9)

        entropy_2gram = 0.0
        if num_tokens >= 2:
            ngrams_2 = list(zip(tokens, tokens[1:]))
            entropy_2gram = self._calculate_entropy(ngrams_2)

        adversarial_score = 1.0 if (reset_flag > 0 or loop_keyword_flag > 0) and normal_pattern_flag == 0 else 0.0

        struct_loop_flag = 0.0
        if num_tokens >= 4:
            for i in range(num_tokens - 3):
                if tokens[i] == tokens[i+2] and tokens[i+1] == tokens[i+3]:
                    struct_loop_flag = 1.0
                    break

        semantic_coherence = (stop_count + sum(1 for t in tokens if t in self.normal_patterns)) / num_tokens

        salad_diff = 0.0
        if num_tokens > 6:
            mid = num_tokens // 2
            t1, t2 = tokens[:mid], tokens[mid:]
            u1, u2 = len(set(t1)) / len(t1), len(set(t2)) / len(t2)
            s1 = sum(1 for t in t1 if t in self.stop_words) / len(t1)
            s2 = sum(1 for t in t2 if t in self.stop_words) / len(t2)
            salad_diff = abs((u1 * (1.0 - s1)) - (u2 * (1.0 - s2)))

        digits = len(re.findall(r'\d', text))
        digit_density = digits / len(text) if len(text) > 0 else 0.0

        features_dict = {
            "length": float(length), "unique_ratio": float(unique_ratio), "entropy": float(entropy),
            "repetition_score": float(repetition_score), "max_ngram_repeat": float(max_ngram_repeat),
            "stop_word_ratio": float(stop_word_ratio), "alpha_ratio": float(alpha_ratio),
            "avg_token_len": float(avg_token_len), "reset_flag": float(reset_flag),
            "loop_keyword_flag": float(loop_keyword_flag), "punc_density": float(punc_density),
            "vowel_ratio": float(vowel_ratio), "normal_pattern_flag": float(normal_pattern_flag),
            "char_repetition": float(char_repetition), "word_salad_score": float(word_salad_score),
            "token_diversity": float(token_diversity), "entropy_2gram": float(entropy_2gram),
            "adversarial_score": float(adversarial_score), "struct_loop_flag": float(struct_loop_flag),
            "semantic_coherence": float(semantic_coherence), "salad_diff": float(salad_diff), "digit_density": float(digit_density)
        }

        feature_vector = [
            length, unique_ratio, entropy, repetition_score, max_ngram_repeat,
            stop_word_ratio, alpha_ratio, avg_token_len, reset_flag, loop_keyword_flag,
            punc_density, vowel_ratio, normal_pattern_flag, char_repetition, word_salad_score, 
            token_diversity, entropy_2gram, adversarial_score, struct_loop_flag, semantic_coherence,
            salad_diff, digit_density
        ]

        return feature_vector, features_dict
