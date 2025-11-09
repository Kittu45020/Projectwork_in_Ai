class user_level_manager:
    @staticmethod
    def get_numeric_level(user_level):
        levels = {"Level1": 1, "Level2": 2, "Level3": 3}
        return levels.get(user_level, 1)

    @staticmethod
    def get_message_style(user_level):
        styles = {
            "Level1": "Detailed Descriptive",
            "Level2": "Simple Operational",
            "Level3": "Brief Status"
        }
        return styles.get(user_level, "Detailed Descriptive")

    @staticmethod
    def get_level_description(user_level):
        descriptions = {
            "Level1": "Detailed descriptive messages with full context and safety information",
            "Level2": "Simple operational messages showing basic action information",
            "Level3": "Very brief status messages showing only the essential action"
        }
        return descriptions.get(user_level, "Detailed messages")