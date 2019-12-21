import emoji

class EmojiValidator():
    def char_is_emoji(self, character):
        return character in emoji.UNICODE_EMOJI

    def text_has_emoji(self, text):
        for character in text:
            if character in emoji.UNICODE_EMOJI:
                return True
        return False
