from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.validation import Validator, ValidationError


class CustomCompleter(Completer):
    """自定义补全器，支持从外部传入字典数据"""

    def __init__(self, choices: dict[str, str]):
        """
        初始化补全器
        :param choices: 补全选项字典，格式为 {key: display_text}
        """
        self.choices = choices
        self.choice_items = list(choices.items())

    def get_completions(self, document: Document, complete_event):
        """实现模糊补全逻辑，按匹配质量排序"""
        text = document.text_before_cursor.lower()

        # region 收集所有匹配项及其分数
        matches: list[tuple[int, str, str]] = []
        for key, display in self.choice_items:
            key_score = self._fuzzy_match_score(text, key.lower())
            display_score = self._fuzzy_match_score(text, display.lower())
            best_score = max(key_score, display_score)
            if best_score > 0:
                matches.append((best_score, key, display))
        # endregion

        # region 按分数降序排列后返回补全结果
        matches.sort(key=lambda x: x[0], reverse=True)
        for _, key, display in matches:
            yield Completion(
                key,
                start_position=-len(document.text_before_cursor),
                display=display
            )
        # endregion

    def _fuzzy_match_score(self, pattern: str, text: str) -> int:
        """
        模糊匹配并返回匹配分数（寻找最佳匹配）
        分数越高表示匹配质量越好：
        - 0: 不匹配
        - 完全连续匹配优先级最高
        - 其次考虑位置和紧凑度
        """
        if not pattern:
            return 1

        # region 寻找所有可能的匹配并选择最佳
        best_score = 0
        
        def find_matches(p_idx: int, t_idx: int, positions: list[int]):
            """递归寻找所有可能的匹配组合"""
            nonlocal best_score
            
            if p_idx == len(pattern):
                score = self._calculate_score(positions, len(pattern))
                best_score = max(best_score, score)
                return
            
            for i in range(t_idx, len(text)):
                if text[i] == pattern[p_idx]:
                    find_matches(p_idx + 1, i + 1, positions + [i])
        
        find_matches(0, 0, [])
        # endregion
        
        return best_score

    def _calculate_score(self, match_positions: list[int], pattern_len: int) -> int:
        """根据匹配位置计算分数"""
        # region 计算连续匹配数
        consecutive_count = 0
        for i in range(1, len(match_positions)):
            if match_positions[i] == match_positions[i - 1] + 1:
                consecutive_count += 1
        # endregion

        # region 计算分数
        is_fully_consecutive = consecutive_count == pattern_len - 1

        if is_fully_consecutive:
            score = 1000 - match_positions[0]
        else:
            score = 100
            score += max(0, 50 - match_positions[0] * 2)
            span = match_positions[-1] - match_positions[0] + 1
            score += max(0, 30 - (span - len(match_positions)) * 2)
            score += consecutive_count * 10
        # endregion

        return score

    def get_valid_keys(self) -> list[str]:
        """返回所有有效的 key 列表"""
        return list(self.choices.keys())


class CustomValidator(Validator):
    """验证器：确保用户输入的值有效"""

    def __init__(self, completer: CustomCompleter, error_msg: str = "无效的输入，请从补全列表中选择。"):
        self.completer = completer
        self.valid_keys = completer.get_valid_keys()
        self.error_msg = error_msg

    def validate(self, document: Document):
        """验证用户输入是否有效"""
        text = document.text.strip()

        if text and text not in self.valid_keys:
            raise ValidationError(
                message=self.error_msg,
                cursor_position=len(text)
            )



if __name__ == "__main__":
    # 调试测试
    test_choices = {
        "linux_init.setup_vagrant_user": "linux_init.setup_vagrant_user",
        "linux_init.setup_apt_sources": "linux_init.setup_apt_sources",
        "linux_init.install_kernel_dev_packages": "linux_init.install_kernel_dev_packages",
        "docker.configure_docker_user": "docker.configure_docker_user",
        "docker.uninstall_old_docker": "docker.uninstall_old_docker",
    }

    completer = CustomCompleter(test_choices)
    pattern = "user"
    
    print(f"Pattern: '{pattern}'\n")
    scores = []
    for key in test_choices:
        score = completer._fuzzy_match_score(pattern, key.lower())
        scores.append((score, key))
    
    scores.sort(key=lambda x: x[0], reverse=True)
    for score, key in scores:
        print(f"{score:4d}  {key}")
